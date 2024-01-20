import matplotlib.pyplot as plt
import pandas as pd
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
  
		if len(selected_columns) > 2 or (len(selected_columns) == 2 and self.main_app.x_axis_combobox.get() != ""):
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
			if len(selected_columns) == 2 and self.hue.get():
				plot_args["hue"] = self.hue.get()
			if self.kind.get():
				plot_args["kind"] = self.kind.get()
    
		else:
			plot_args = {"x": x_axis, "y": y_axis[0] if len(y_axis) == 1 else y_axis, "data_frame": data}
			if len(selected_columns) == 2 and self.hue.get():
				plot_args["color"] = self.hue.get()
			if self.style.get():
				plot_args["symbol"] = self.style.get()	
			if self.row.get():
				plot_args["facet_row"] = self.row.get()
			if self.col.get():
				plot_args["facet_col"] = self.col.get()
		
		
		return plot_args
 
	def show_joint_plot(self, refresh_plot):
		selected_columns = self.main_app.get_selected_columns()
		
		if self.main_app.use_plotly.get() == False:
  			# Create a Seaborn joint plot
			plot_args = self.create_plot_args(self.main_app.df)
			g = sns.jointplot(**plot_args)

			fig = g.fig
			if self.plot_with.get() and self.plot_hight.get():
				fig.set_size_inches(float(self.plot_with.get()), float(self.plot_hight.get()))
			fig.suptitle(self.plot_title.get(), verticalalignment='top', fontsize=12)
			fig.subplots_adjust(top=0.94)
      
		else:
			# Create a Plotly joint plot
			plot_args = self.create_plot_args(self.main_app.df)
			if self.kind.get() == "line":
				if isinstance(plot_args["data_frame"].index, pd.DatetimeIndex) == False:
					plot_args["data_frame"] = plot_args["data_frame"].groupby(plot_args["x"]).mean().reset_index()
				fig = px.line(**plot_args)
			else:
				fig = px.scatter(**plot_args)
			if self.plot_title.get():
				fig.update_layout(title=self.plot_title.get())
			fig.update_layout(autosize=True, width=None, height=None)
			if self.plot_with.get() and self.plot_hight.get():
				fig.update_layout(width=float(self.plot_with.get()), height=float(self.plot_hight.get()))
       
		if refresh_plot:
			self.display_refresh_plot(fig)
		else:
			if self.main_app.use_plotly.get() == False:
				self.main_app.open_windows.append(self.display_plot(fig))
			else:
				self.main_app.open_windows.append(self.display_plotly_plot(fig))

  
		def on_click(event):
			# Finden Sie heraus, welcher Subplot (Facet) geklickt wurde
			if event.inaxes == g.ax_joint:
				x_var = g.x
				y_var = g.y
				self.show_clicked_plot(x_var, y_var)
	
		# add event-handeler for clicking on facets
		if self.main_app.use_plotly.get() == False:
			g.fig.canvas.mpl_connect('button_press_event', on_click)


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