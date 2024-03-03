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
import ast


import io
from PIL import Image

class LmPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Lm Plot")
		self.title_x_axis = tk.StringVar()
		self.title_y_axis = tk.StringVar()
		self.plot_with = tk.StringVar()
		self.plot_hight = tk.StringVar()
		self.last_window = None
		self.last_canvas = None

		#plot_args
		self.hue = tk.StringVar()
		self.scatter = tk.StringVar()
		self.x_bins = tk.StringVar()
		self.robust = tk.StringVar()
		self.facet_kws = tk.StringVar()
		self.row = tk.StringVar()
		self.col = tk.StringVar()

 
	def create_plot_args(self, data):
		selected_columns = self.main_app.get_selected_columns()  
		if self.main_app.x_axis_combobox.get() != "":
			x_axis = self.main_app.x_axis_combobox.get()
		else:
			x_axis = selected_columns[0]
		
		y_axis = [col for col in selected_columns if col != x_axis]
  
		if self.main_app.multiplot.get() == False and (len(selected_columns) > 2 or (len(selected_columns) == 2 and self.main_app.x_axis_combobox.get() != "" and self.main_app.x_axis_combobox.get() not in selected_columns)):
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
		else:
			plot_args = {"x": x_axis, "y": y_axis[0] if len(y_axis) == 1 else y_axis, "data": data}
   
		if self.main_app.use_plotly.get() == False:
			if self.hue.get():
				plot_args["hue"] = self.hue.get()
			if self.scatter.get():
				plot_args["scatter"] = ast.literal_eval(self.scatter.get())
			if self.x_bins.get():
				plot_args["x_bins"] = int(self.x_bins.get())
			if self.robust.get():
				plot_args["robust"] = ast.literal_eval(self.robust.get())
			if self.facet_kws.get():
				plot_args["facet_kws"] = ast.literal_eval(self.facet_kws.get())
			if self.row.get():
				plot_args["row"] = self.row.get()
			if self.col.get():
				plot_args["col"] = self.col.get()
    
		else:
			plot_args = {"x": x_axis, "y": y_axis[0] if len(y_axis) == 1 else y_axis, "data_frame": data}
			if self.hue.get():
				plot_args["color"] = self.hue.get()
			if self.row.get():
				plot_args["facet_row"] = self.row.get()
			if self.col.get():
				plot_args["facet_col"] = self.col.get()
			plot_args["trendline"] = "ols"

		return plot_args
 
 
	# Create a Seaborn lm plot
	def create_seaborn_plot(self, refresh_plot, plot_args):
		if plot_args is None:
			selected_columns = self.main_app.get_selected_columns()
			if len(selected_columns) < 1 or (len(selected_columns) == 1 and self.main_app.x_axis_combobox.get() == ""):
				messagebox.showinfo("Information", "Select two or more Columns or one Column and the x-axis")
				return			
			plot_args = self.create_plot_args(self.main_app.df)
		
  		# Create a Seaborn lm plot
		g = sns.lmplot(**plot_args)
		if self.title_x_axis.get() != "":
			g.set_axis_labels(x_var=self.title_x_axis.get())
		if self.title_y_axis.get() != "":
			g.set_axis_labels(y_var=self.title_y_axis.get())
		fig = g.fig
		if self.plot_with.get() and self.plot_hight.get():
			fig.set_size_inches(float(self.plot_with.get()), float(self.plot_hight.get()))
		fig.suptitle(self.plot_title.get(), verticalalignment='top', fontsize=12)
		fig.subplots_adjust(top=0.94)

		# Save the axes and the corresponding facet title
		axes_facet_map = {}
		for ax in g.axes.flatten():
			facet_title = ax.get_title()
			axes_facet_map[ax] = facet_title

		def on_click(event):
			if self.main_app.multiplot.get():
				self.main_app.open_windows.append(self.display_plot(event.canvas.figure))
				return
      
			ax_clicked = event.inaxes
			if ax_clicked in axes_facet_map:
				facet_title = axes_facet_map[ax_clicked]
				splitted_facets = facet_title.split(" | ")
				filtered_data = self.main_app.df.copy()
			if splitted_facets != ['']:
				for facet in splitted_facets:
					column, value = facet.split(" = ")
					value = int(value) if value.isdigit() else value
					filtered_data = filtered_data[filtered_data[column] == value]
			self.show_clicked_plot(False, filtered_data)

		# add event-handeler for clicking on facets
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
		
		# Create a Plotly lm plot
		plot_args = self.create_plot_args(self.main_app.df)
		fig = px.scatter(**plot_args)
		if self.plot_title.get():
			fig.update_layout(title=self.plot_title.get())
		if self.title_x_axis.get():
			fig.update_layout(xaxis_title=self.title_x_axis.get())
		if self.title_y_axis.get():
			fig.update_layout(yaxis_title=self.title_y_axis.get())
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
		if self.main_app.x_axis_combobox.get() == "":
			messagebox.showinfo("Information", "Select the x-axis")
			return
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
				canvas_rows = math.ceil(number_of_plots / self.main_app.multi_plot_columns_var.get())
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


	def show_lm_plot(self, refresh_plot):
		if self.main_app.use_plotly.get() == False and self.main_app.multiplot.get() == False:
			self.create_seaborn_plot(refresh_plot, None)
		elif self.main_app.multiplot.get():
			self.create_multi_plot(refresh_plot)
		else:
			self.create_plotly_plot(refresh_plot)


	def show_clicked_plot(self, refresh_plot, filtered_data):
		selected_columns = self.main_app.get_selected_columns()
		plot_args = self.create_plot_args(filtered_data)
		g = sns.lmplot(**plot_args)
		if self.title_x_axis.get() != "":
			g.set_axis_labels(x_var=self.title_x_axis.get())
		if self.title_y_axis.get() != "":
			g.set_axis_labels(y_var=self.title_y_axis.get())
		
		fig = g.fig
		if self.plot_with.get() and self.plot_hight.get():
			fig.set_size_inches(float(self.plot_with.get()), float(self.plot_hight.get()))
		fig.suptitle(self.plot_title.get(), verticalalignment='top', fontsize=12)
		fig.subplots_adjust(top=0.94)

		if refresh_plot:
			self.display_refresh_plot(fig)
		else:
			self.main_app.open_windows.append(self.display_plot(fig))


	def init_ui(self):
		self.plot_arguments_frame_visible = True
  		# Remove previously created widgets in the parent_frame
		for widget in self.main_app.lmplot_tab_frame.winfo_children():
			widget.destroy()
   

		# Frame for buttons
		button_frame = tk.Frame(self.main_app.lmplot_tab_frame)
		button_frame.pack(padx=5, pady=5, anchor='c')

		# Button to show Lm Plot in new window
		show_plot_button = tk.Button(button_frame, text="Show Plot", command=lambda: self.show_lm_plot(False))
		show_plot_button.grid(row=0, column=0, padx=5)
  
		# Button to refresh Lm Plot in same window
		show_plot_button = tk.Button(button_frame, text="Refresh Plot", command=lambda: self.show_lm_plot(True))
		show_plot_button.grid(row=0, column=1, padx=5)
  
		# Button to show and hide more plot aguments
		self.toggle_arguments_button = tk.Button(button_frame, text="Hide Arguments", command=self.toggle_plot_arguments_frame)
		self.toggle_arguments_button.grid(row=0, column=2, padx=5)


		# Frame for main plot args
		main_plot_arguments_frame = tk.Frame(self.main_app.lmplot_tab_frame)
		main_plot_arguments_frame.pack(padx=5, pady=5, anchor='w')
		# Entry for plot title
		title_label = tk.Label(main_plot_arguments_frame, text="Plot title:")
		title_label.grid(row=0, column=0, padx=5)
		title_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.plot_title)
		title_entry.grid(row=0, column=1)  
		# Entry for x-axis label
		x_axis_label = tk.Label(main_plot_arguments_frame, text="x-axis title:")
		x_axis_label.grid(row=1, column=0, padx=5)
		x_axis_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.title_x_axis)
		x_axis_entry.grid(row=1, column=1, padx=5)
		# Entry for y-axis label
		y_axis_label = tk.Label(main_plot_arguments_frame, text="y-axis title:")
		y_axis_label.grid(row=2, column=0, padx=5)
		y_axis_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.title_y_axis)
		y_axis_entry.grid(row=2, column=1, padx=5)
		# Entry for plot with
		plot_with_label = tk.Label(main_plot_arguments_frame, text="plot with:")
		plot_with_label.grid(row=3, column=0, padx=5)
		plot_with_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.plot_with)
		plot_with_entry.grid(row=3, column=1, padx=5)
		# Entry for plot hight
		plot_hight_label = tk.Label(main_plot_arguments_frame, text="plot hight:")
		plot_hight_label.grid(row=4, column=0, padx=5)
		plot_hight_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.plot_hight)
		plot_hight_entry.grid(row=4, column=1, padx=5)

		# Frame for plot arguments
		self.plot_arguments_frame = tk.Frame(self.main_app.lmplot_tab_frame)
		self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
		# Hue
		self.hue_label = tk.Label(self.plot_arguments_frame, text="Hue:")
		self.hue_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
		self.hue_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.hue)
		self.hue_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
		# Scatter
		self.scatter_label = tk.Label(self.plot_arguments_frame, text="Scatter:")
		self.scatter_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
		self.scatter_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.scatter)
		self.scatter_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='w')
		# x_bins
		self.x_bins_label = tk.Label(self.plot_arguments_frame, text="x_bins:")
		self.x_bins_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
		self.x_bins_combobox = ttk.Entry(self.plot_arguments_frame, textvariable=self.x_bins)
		self.x_bins_combobox.grid(row=3, column=1, padx=5, pady=5, sticky='w')
		# Robust
		self.robust_label = tk.Label(self.plot_arguments_frame, text="Robust:")
		self.robust_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
		self.robust_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.robust)
		self.robust_combobox.grid(row=4, column=1, padx=5, pady=5, sticky='w')
		# Facet_kws
		self.facet_kws_label = tk.Label(self.plot_arguments_frame, text="Facet_kws:")
		self.facet_kws_label.grid(row=5, column=0, padx=5, pady=5, sticky='w')
		self.facet_kws_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.facet_kws)
		self.facet_kws_combobox.grid(row=5, column=1, padx=5, pady=5, sticky='w')
		# Row
		self.row_label = tk.Label(self.plot_arguments_frame, text="Row:")
		self.row_label.grid(row=6, column=0, padx=5, pady=5, sticky='w')
		self.row_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.row)	
		self.row_combobox.grid(row=6, column=1, padx=5, pady=5, sticky='w')	
		# Col
		self.col_label = tk.Label(self.plot_arguments_frame, text="Col:")
		self.col_label.grid(row=7, column=0, padx=5, pady=5, sticky='w')
		self.col_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.col)
		self.col_combobox.grid(row=7, column=1, padx=5, pady=5, sticky='w')
  
		self.load_argument_values()


	def load_argument_values(self):
		if self.main_app.df is not None:
			self.main_app.lmplot_analysis.hue_combobox['values'] = list(self.main_app.df.columns)
			self.main_app.lmplot_analysis.scatter_combobox['values'] = ['True', 'False']
			#self.main_app.lmplot_analysis.x_bins_combobox['values'] = list(range(1, 100))
			self.main_app.lmplot_analysis.robust_combobox['values'] = ['True', 'False']
			self.main_app.lmplot_analysis.facet_kws_combobox['values'] = ['{ "sharex": False, "sharey": False }']

			self.main_app.lmplot_analysis.row_combobox['values'] = list(self.main_app.df.columns)
			self.main_app.lmplot_analysis.col_combobox['values'] = list(self.main_app.df.columns)

  
	def toggle_plot_arguments_frame(self):
		if self.plot_arguments_frame_visible:
			self.plot_arguments_frame.pack_forget()
			self.toggle_arguments_button.config(text="Show Plot Arguments")
		else:
			self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
			self.toggle_arguments_button.config(text="Hide Plot Arguments")
		self.plot_arguments_frame_visible = not self.plot_arguments_frame_visible