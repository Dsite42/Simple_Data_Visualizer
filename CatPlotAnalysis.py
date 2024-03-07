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
import numpy as np
import scipy.stats as stats

import io
from PIL import Image

class CatPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Cat Plot")
		self.title_x_axis = tk.StringVar()
		self.title_y_axis = tk.StringVar()
		self.plot_with = tk.StringVar()
		self.plot_hight = tk.StringVar()
		self.last_window = None
		self.last_canvas = None

		#plot_args
		self.kind = tk.StringVar()
		self.hue = tk.StringVar()
		self.row = tk.StringVar()
		self.col = tk.StringVar()

 
 
	def create_plot_args(self, data):
		selected_columns = self.main_app.get_selected_columns()  		
		if self.main_app.x_axis_combobox.get() != "":
			x_axis = self.main_app.x_axis_combobox.get()
		elif len(selected_columns) != 0:
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
		elif (len(selected_columns) == 1 and (self.main_app.x_axis_combobox.get() == "" or selected_columns[0] == self.main_app.x_axis_combobox.get())) or (len(selected_columns) == 0 and self.main_app.x_axis_combobox.get() != ""):
			plot_args = {"x": x_axis, "data": data}
		elif len(selected_columns) == 0 and self.main_app.x_axis_combobox.get() == "":
			plot_args = {"data": data}
		else:
			plot_args = {"x": x_axis, "y": y_axis[0] if len(y_axis) == 1 else y_axis, "data": data}
   
		if self.main_app.use_plotly.get() == False:
			if self.hue.get():
				plot_args["hue"] = self.hue.get()
			if self.kind.get():
				plot_args["kind"] = self.kind.get()
			if self.row.get():
				plot_args["row"] = self.row.get()
			if self.col.get():
				plot_args["col"] = self.col.get()
    
		else:
			if "data" in plot_args:
				del plot_args["data"]
			if "data_frame" not in plot_args:
				plot_args["data_frame"] = data
			if self.hue.get():
				plot_args["color"] = self.hue.get()
			if self.row.get():
				plot_args["facet_row"] = self.row.get()
			if self.col.get():
				plot_args["facet_col"] = self.col.get()
		
		return plot_args


	# Create a Seaborn CatPlot
	def create_seaborn_plot(self, refresh_plot, plot_args):
		selected_columns = self.main_app.get_selected_columns()
		if plot_args is None:
			plot_args = self.create_plot_args(self.main_app.df)

  		# Create a Seaborn cat plot
		g = sns.catplot(**plot_args)
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
		if self.main_app.use_plotly.get() == False:
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

		# Create a Plotly cat plot
		# Not supported plots in plotly: hex, resid
		if self.kind.get() == "swarm" or self.kind.get() == "boxen" or self.kind.get() == "point":
			messagebox.showinfo("Info", "Plotly does not support the kind: " + self.kind.get())
			return
		plot_args = self.create_plot_args(self.main_app.df)
		if self.kind.get() == "strip" or self.kind.get() == "":
			fig = px.strip(**plot_args)
		elif self.kind.get() == "box":
			fig = px.box(**plot_args)
		elif self.kind.get() == "violin":
			fig = px.violin(**plot_args, box=True)
		elif self.kind.get() == "bar":
			fig = px.bar(**plot_args)
		elif self.kind.get() == "count":
			fig = px.histogram(**plot_args)
			fig.update_layout(bargap=0.1)
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
			if self.main_app.x_axis_combobox.get() == "":
				plot_args.pop("x", None)
			plot_args["y"] = selected_columns[i]
			figures.append(self.create_seaborn_plot(refresh_plot, plot_args))
		if refresh_plot:
			self.display_refresh_multiple_plots(figures, canvas_rows, canvas_columns)
		else:
			self.main_app.open_windows.append(self.display_multiple_plots(figures, canvas_rows, canvas_columns))
 

	def show_cat_plot(self, refresh_plot):
		if self.main_app.use_plotly.get() == False and self.main_app.multiplot.get() == False:
			self.create_seaborn_plot(refresh_plot, None)
		elif self.main_app.multiplot.get():
			self.create_multi_plot(refresh_plot)
		else:
			self.create_plotly_plot(refresh_plot)


	def show_clicked_plot(self, refresh_plot, filtered_data):
		selected_columns = self.main_app.get_selected_columns()
		plot_args = self.create_plot_args(filtered_data)
		g = sns.catplot(**plot_args)
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
		for widget in self.main_app.catplot_tab_frame.winfo_children():
			widget.destroy()
   

		# Frame for buttons
		button_frame = tk.Frame(self.main_app.catplot_tab_frame)
		button_frame.pack(padx=5, pady=5, anchor='c')

		# Button to show Cat Plot in new window
		show_plot_button = tk.Button(button_frame, text="Show Plot", command=lambda: self.show_cat_plot(False))
		show_plot_button.grid(row=0, column=0, padx=5)
  
		# Button to refresh Cat Plot in same window
		show_plot_button = tk.Button(button_frame, text="Refresh Plot", command=lambda: self.show_cat_plot(True))
		show_plot_button.grid(row=0, column=1, padx=5)
  
		# Button to show and hide more plot aguments
		self.toggle_arguments_button = tk.Button(button_frame, text="Hide Arguments", command=self.toggle_plot_arguments_frame)
		self.toggle_arguments_button.grid(row=0, column=2, padx=5)


		# Frame for main plot args
		main_plot_arguments_frame = tk.Frame(self.main_app.catplot_tab_frame)
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
		self.plot_arguments_frame = tk.Frame(self.main_app.catplot_tab_frame)
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
		# Row
		self.row_label = tk.Label(self.plot_arguments_frame, text="Row:")
		self.row_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
		self.row_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.row)	
		self.row_combobox.grid(row=3, column=1, padx=5, pady=5, sticky='w')	
		# Col
		self.col_label = tk.Label(self.plot_arguments_frame, text="Col:")
		self.col_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
		self.col_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.col)
		self.col_combobox.grid(row=4, column=1, padx=5, pady=5, sticky='w')
  
		self.load_argument_values()


	def load_argument_values(self):
		if self.main_app.df is not None:
			self.main_app.catplot_analysis.kind_combobox['values'] = ['strip', 'swarm', 'box', 'violin', 'boxen', 'point', 'bar', 'count']
			self.main_app.catplot_analysis.hue_combobox['values'] = list(self.main_app.df.columns)
			self.main_app.catplot_analysis.row_combobox['values'] = list(self.main_app.df.columns)
			self.main_app.catplot_analysis.col_combobox['values'] = list(self.main_app.df.columns)

  

	def toggle_plot_arguments_frame(self):
		if self.plot_arguments_frame_visible:
			self.plot_arguments_frame.pack_forget()
			self.toggle_arguments_button.config(text="Show Plot Arguments")
		else:
			self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
			self.toggle_arguments_button.config(text="Hide Plot Arguments")
		self.plot_arguments_frame_visible = not self.plot_arguments_frame_visible
  
