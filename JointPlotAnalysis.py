import matplotlib.pyplot as plt
import pandas as pd
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from BaseAnalysis import BaseAnalysis
import seaborn as sns
sns.set(style="darkgrid")
import plotly.express as px


import io
from PIL import Image

class JointPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Joint Plot")
		self.plot_with = tk.StringVar()
		self.plot_hight = tk.StringVar()
		self.last_window = None
		self.last_canvas = None

		#plot_args
		self.kind = tk.StringVar()
		self.hue = tk.StringVar()
 
 
	def create_plot_args(self, data):
		selected_columns = self.main_app.get_selected_columns()  
		if self.main_app.x_axis_combobox.get() != "":
			x_axis = self.main_app.x_axis_combobox.get()
		elif len(selected_columns) != 0:
			x_axis = selected_columns[0]
		
		y_axis = [col for col in selected_columns if col != x_axis]
  
		if self.main_app.multiplot.get() == False and (len(selected_columns) > 2 or (len(selected_columns) == 2 and self.main_app.x_axis_combobox.get() != "")):
			all_columns = list(data.columns)
			if self.main_app.x_axis_combobox.get() == "":
				id_vars = [col for col in all_columns if col not in selected_columns[1:]]
			else:
				id_vars = [col for col in all_columns if col not in selected_columns or col == x_axis]
			melted_df = data.melt(id_vars=id_vars, value_vars=y_axis, var_name='Measurement', value_name='Value')
			if self.main_app.use_plotly.get() == False:
				plot_args = {"x": x_axis, "y": "Value", "hue": "Measurement", "data": melted_df} 
			else:
				plot_args = {"x": x_axis, "y": "Value", "color": "Measurement", "data_frame": melted_df}
		elif (len(selected_columns) == 1 and (self.main_app.x_axis_combobox.get() == "" or selected_columns[0] == self.main_app.x_axis_combobox.get())) or (len(selected_columns) == 0 and self.main_app.x_axis_combobox.get() != ""):
			plot_args = {"x": x_axis, "data": data}
		elif len(selected_columns) == 0 and self.main_app.x_axis_combobox.get() == "":
			plot_args = {"data": data}
		else:
			plot_args = {"x": x_axis, "y": y_axis[0] if len(y_axis) == 1 else y_axis, "data": data}
	
   
		if self.main_app.use_plotly.get() == False:
			if (self.main_app.multiplot.get() or len(selected_columns) == 2) and self.hue.get():
				plot_args["hue"] = self.hue.get()
			if self.kind.get():
				plot_args["kind"] = self.kind.get()
    
		else:
			plot_args = {"x": x_axis, "y": y_axis[0] if len(y_axis) == 1 else y_axis, "data_frame": data}
			if len(selected_columns) == 2 and self.hue.get() and self.kind.get() != "hist":
				plot_args["color"] = self.hue.get()
			if self.kind.get() == "scatter" or self.kind.get() == "":
				plot_args["opacity"] = 0.3
				plot_args["marginal_x"] = "histogram"
				plot_args["marginal_y"] = "histogram"
			elif self.kind.get() == "kde" or self.kind.get() == "hist":
				plot_args["marginal_x"] = "histogram"
				plot_args["marginal_y"] = "histogram"
			elif self.kind.get() == "reg":
				plot_args["opacity"] = 0.3
				plot_args["trendline"] = "ols"
				plot_args["marginal_x"] = "histogram"
				plot_args["marginal_y"] = "histogram"
		
		return plot_args
 
 
	# Create a Seaborn lm plot
	def create_seaborn_plot(self, refresh_plot, plot_args):
		if plot_args is None:
			selected_columns = self.main_app.get_selected_columns()  
			if len(selected_columns) < 1 or (len(selected_columns) == 1 and self.main_app.x_axis_combobox.get() == ""):
				messagebox.showinfo("Information", "Select two or more Columns or one Column and the x-axis")
				return
			plot_args = self.create_plot_args(self.main_app.df)
		
  		# Create a Seaborn joint plot
		g = sns.jointplot(**plot_args)
		fig = g.fig
		if self.plot_with.get() and self.plot_hight.get():
			fig.set_size_inches(float(self.plot_with.get()), float(self.plot_hight.get()))
		fig.suptitle(self.plot_title.get(), verticalalignment='top', fontsize=12)
		fig.subplots_adjust(top=0.94)
             
		def on_click(event):
			# Finden Sie heraus, welcher Subplot (Facet) geklickt wurde
			if event.inaxes == g.ax_joint:
				x_var = g.x
				y_var = g.y
				self.show_clicked_plot(x_var, y_var)
	
		# add event-handeler for clicking on facets
		if self.main_app.use_plotly.get() == False:
			g.fig.canvas.mpl_connect('button_press_event', on_click)

		if self.main_app.multiplot.get():
			return fig
		if refresh_plot:
			self.display_refresh_plot(fig)
		else:
			self.main_app.open_windows.append(self.display_plot(fig))
 
 
	# Create Plotly plot
	def create_plotly_plot(self, refresh_plot):
		selected_columns = self.main_app.get_selected_columns()  
		if len(selected_columns) < 1 or (len(selected_columns) == 1 and self.main_app.x_axis_combobox.get() == ""):
			messagebox.showinfo("Information", "Select two or more Columns or one Column and the x-axis")
			return			
		
		# Create a Plotly joint plot

		# Not supported plots in plotly: hex, resid
		if self.kind.get() == "hex" or self.kind.get() == "resid":
			messagebox.showinfo("Info", "Plotly does not support the kind: " + self.kind.get())
			return

		plot_args = self.create_plot_args(self.main_app.df)
		if self.kind.get() == "scatter" or self.kind.get() == "" or self.kind.get() == "reg":
			fig = px.scatter(**plot_args)
		elif self.kind.get() == "kde":
			fig = px.density_contour(**plot_args)
		elif self.kind.get() == "hist":
			fig = px.density_heatmap(**plot_args)
		if self.plot_title.get():
			fig.update_layout(title=self.plot_title.get())
		fig.update_layout(autosize=True, width=None, height=None)
		if self.plot_with.get() and self.plot_hight.get():
			fig.update_layout(width=float(self.plot_with.get()), height=float(self.plot_hight.get()))
       
		if refresh_plot:
			self.display_refresh_plot(fig)
		else:
			self.main_app.open_windows.append(self.display_plotly_plot(fig))


	# Create a multiplot
	def create_multi_plot(self, refresh_plot):
		selected_columns = self.main_app.get_selected_columns()
		if len(selected_columns) == 0:
			selected_columns = list(self.main_app.df.columns)
			if self.main_app.x_axis_combobox.get() != "":
				selected_columns.remove(self.main_app.x_axis_combobox.get())
		if self.main_app.multi_plot_rows_var.get() == 0 and self.main_app.multi_plot_columns_var.get() == 0:
			messagebox.showinfo("Information", "Number of rows or columns must be greater than 0")
			return
		if self.main_app.multi_plot_rows_var.get() != 0 and self.main_app.multi_plot_columns_var.get() != 0 and (self.main_app.multi_plot_rows_var.get() * self.main_app.multi_plot_columns_var.get() < len(selected_columns)):
			messagebox.showinfo("Information", "Number of rows times number of columns must be greater than or equal to the number of selected columns")
			return

		# Calculate numer of rows and columns
		number_of_plots = len(selected_columns)
		if self.main_app.multi_plot_rows_var.get() == 0:
			if self.main_app.multi_plot_columns_var.get() >= number_of_plots:
				canvas_rows = 1
				canvas_columns = number_of_plots
			else:
				canvas_rows = math.ceil(number_of_plots // self.main_app.multi_plot_columns_var.get())
				canvas_columns = self.main_app.multi_plot_columns_var.get()
		
		elif self.main_app.multi_plot_columns_var.get() == 0:
			if self.main_app.multi_plot_rows_var.get() >= number_of_plots:
				canvas_rows = number_of_plots
				canvas_columns = 1
			else:
				canvas_rows = self.main_app.multi_plot_rows_var.get()
				canvas_columns = math.ceil(number_of_plots // self.main_app.multi_plot_rows_var.get())
		else:
			canvas_rows = self.main_app.multi_plot_rows_var.get()
			canvas_columns = self.main_app.multi_plot_columns_var.get()
   
		# Create figs
		figures = []
		for i in range(len(selected_columns)):
			plot_args = self.create_plot_args(self.main_app.df)
			plot_args["x"] = self.main_app.x_axis_combobox.get()
			plot_args["y"] = selected_columns[i]
			figures.append(self.create_seaborn_plot(refresh_plot, plot_args))
		if refresh_plot:
			self.display_refresh_multiple_plots(figures, canvas_rows, canvas_columns)
		else:
			self.main_app.open_windows.append(self.display_multiple_plots(figures, canvas_rows, canvas_columns))


	def show_joint_plot(self, refresh_plot):
		if self.hue.get() and self.main_app.use_plotly.get() == False and (self.kind.get() == "hex" or self.kind.get() == "reg" or self.kind.get() == "resid"):
			messagebox.showinfo("Info", "Hue is not supported for the kind: " + self.kind.get())
			
		if self.main_app.use_plotly.get() == False and self.main_app.multiplot.get() == False:
			self.create_seaborn_plot(refresh_plot, None)
		elif self.main_app.multiplot.get():
			self.create_multi_plot(refresh_plot)
		else:
			self.create_plotly_plot(refresh_plot)


	def show_clicked_plot(self, x_var, y_var):
		if self.kind.get() == "hex":
			return	
   
		fig, ax = plt.subplots()
		if self.kind.get() == "scatter" or self.kind.get() == "":
			g = sns.scatterplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax, hue=self.hue.get() if self.hue.get() else None)
		elif self.kind.get() == "kde":
			g = sns.kdeplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax)
		elif self.kind.get() == "hist":
			g = sns.histplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax)
		elif self.kind.get() == "reg":
			g = sns.regplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax)
		elif self.kind.get() == "resid":
			g = sns.residplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax)
		
		if self.plot_with.get() and self.plot_hight.get():
			fig.set_size_inches(float(self.plot_with.get()), float(self.plot_hight.get()))
		fig.suptitle(self.plot_title.get(), verticalalignment='top', fontsize=12)
		fig.subplots_adjust(top=0.94)

		self.main_app.open_windows.append(self.display_plot(fig))



	def init_ui(self):
		self.plot_arguments_frame_visible = True
  		# Remove previously created widgets in the parent_frame
		for widget in self.main_app.jointplot_tab_frame.winfo_children():
			widget.destroy()
   

		# Frame for buttons
		button_frame = tk.Frame(self.main_app.jointplot_tab_frame)
		button_frame.pack(padx=5, pady=5, anchor='c')

		# Button to show Joint Plot in new window
		show_plot_button = tk.Button(button_frame, text="Show Plot", command=lambda: self.show_joint_plot(False))
		show_plot_button.grid(row=0, column=0, padx=5)
  
		# Button to refresh Joint Plot in same window
		show_plot_button = tk.Button(button_frame, text="Refresh Plot", command=lambda: self.show_joint_plot(True))
		show_plot_button.grid(row=0, column=1, padx=5)
  
		# Button to show and hide more plot aguments
		self.toggle_arguments_button = tk.Button(button_frame, text="Hide Arguments", command=self.toggle_plot_arguments_frame)
		self.toggle_arguments_button.grid(row=0, column=2, padx=5)


		# Frame for main plot args
		main_plot_arguments_frame = tk.Frame(self.main_app.jointplot_tab_frame)
		main_plot_arguments_frame.pack(padx=5, pady=5, anchor='w')
		# Entry for plot title
		title_label = tk.Label(main_plot_arguments_frame, text="Plot title:")
		title_label.grid(row=0, column=0, padx=5)
		title_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.plot_title)
		title_entry.grid(row=0, column=1)  
		# Entry for plot with
		plot_with_label = tk.Label(main_plot_arguments_frame, text="plot with:")
		plot_with_label.grid(row=1, column=0, padx=5)
		plot_with_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.plot_with)
		plot_with_entry.grid(row=1, column=1, padx=5)
		# Entry for plot hight
		plot_hight_label = tk.Label(main_plot_arguments_frame, text="plot hight:")
		plot_hight_label.grid(row=2, column=0, padx=5)
		plot_hight_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.plot_hight)
		plot_hight_entry.grid(row=2, column=1, padx=5)

		# Frame for plot arguments
		self.plot_arguments_frame = tk.Frame(self.main_app.jointplot_tab_frame)
		self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
		# Kind
		self.kind_label = tk.Label(self.plot_arguments_frame, text="Kind:")
		self.kind_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
		self.kind_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.kind)
		self.kind_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
		# Hue
		self.hue_label = tk.Label(self.plot_arguments_frame, text="Hue:")
		self.hue_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
		self.hue_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.hue)
		self.hue_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
  
		self.load_argument_values()


	def load_argument_values(self):
		if self.main_app.df is not None:
			self.main_app.jointplot_analysis.kind_combobox['values'] = ['scatter', 'kde', 'hist', 'hex', 'reg', 'resid']
			self.main_app.jointplot_analysis.hue_combobox['values'] = list(self.main_app.df.columns)

  
	def toggle_plot_arguments_frame(self):
		if self.plot_arguments_frame_visible:
			self.plot_arguments_frame.pack_forget()
			self.toggle_arguments_button.config(text="Show Plot Arguments")
		else:
			self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
			self.toggle_arguments_button.config(text="Hide Plot Arguments")
		self.plot_arguments_frame_visible = not self.plot_arguments_frame_visible