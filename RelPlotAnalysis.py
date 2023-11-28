import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from BaseAnalysis import BaseAnalysis
import seaborn as sns
sns.set(style="darkgrid")

import io
from PIL import Image

class RelPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Rel Plot")
		self.title_x_axis = tk.StringVar()
		self.title_y_axis = tk.StringVar()
		self.plot_with = tk.StringVar()
		self.plot_hight = tk.StringVar()
		self.last_window = None
		self.last_canvas = None

		#plot_args
		self.kind = tk.StringVar()
		self.hue = tk.StringVar()
		self.size = tk.StringVar()
		self.style = tk.StringVar()
		self.row = tk.StringVar()
		self.col = tk.StringVar()

 
 
	def create_plot_args(self, data):
		selected_columns = self.main_app.get_selected_columns()  
		plot_args = {"x": selected_columns[0], "y": selected_columns[1], "data": data}
		if self.hue.get():
			plot_args["hue"] = self.hue.get()
		if self.size.get():
			plot_args["size"] = self.size.get()
		if self.style.get():
			plot_args["style"] = self.style.get()
		if self.kind.get():
			plot_args["kind"] = self.kind.get()
		if self.row.get():
			plot_args["row"] = self.row.get()
		if self.col.get():
			plot_args["col"] = self.col.get()
		return plot_args
 
	def show_rel_plot(self, refresh_plot):
		if self.main_app.datetime.get():
			self.main_app.df[self.main_app.datetime.get()] = pd.to_datetime(self.main_app.df[self.main_app.datetime.get()], format='%d.%m.%Y')
			data = self.main_app.df.set_index(self.main_app.datetime.get())

		selected_columns = self.main_app.get_selected_columns()
		if len(selected_columns) != 2:
			messagebox.showinfo("Information", "Select two Columns")
			return
		plot_args = self.create_plot_args(self.main_app.df)
		# Create a Seaborn relational plot
		g = sns.relplot(**plot_args)
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



		# Speichern der Achsen und der zugehörigen Facet-Titel
		axes_facet_map = {}
		for ax in g.axes.flatten():
			facet_title = ax.get_title()
			axes_facet_map[ax] = facet_title

		def on_click(event):
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

		# add event-handeler
		g.fig.canvas.mpl_connect('button_press_event', on_click)

	def show_clicked_plot(self, refresh_plot, filtered_data):
		selected_columns = self.main_app.get_selected_columns()
		if len(selected_columns) != 2:
			messagebox.showinfo("Information", "Select two Columns")
			return
		plot_args = self.create_plot_args(filtered_data)
		g = sns.relplot(**plot_args)
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




	def init_ui(self, parent_frame):
		self.plot_arguments_frame_visible = True
		# Zuvor erstellte Widgets im parent_frame entfernen
		for widget in parent_frame.winfo_children():
			widget.destroy()
   
		# Frame für den Button
		button_frame = tk.Frame(parent_frame)
		button_frame.pack(padx=5, pady=5, anchor='c')

		# Button zum Anzeigen des Rel Plots
		show_plot_button = tk.Button(button_frame, text="Show Plot", command=lambda: self.show_rel_plot(False))
		show_plot_button.grid(row=0, column=0, padx=5)
  
		# Button zum Erneuern des Rel Plots
		show_plot_button = tk.Button(button_frame, text="Refresh Plot", command=lambda: self.show_rel_plot(True))
		show_plot_button.grid(row=0, column=1, padx=5)
  
		# Button to show and hide more plot aguments
		self.toggle_arguments_button = tk.Button(button_frame, text="Hide Arguments", command=self.toggle_plot_arguments_frame)
		self.toggle_arguments_button.grid(row=0, column=2, padx=5)


		# Frame for main plot args
		main_plot_arguments_frame = tk.Frame(parent_frame)
		main_plot_arguments_frame.pack(padx=5, pady=5, anchor='w')
		# Eingabefeld für den Titel des Rel Plots
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
		self.plot_arguments_frame = tk.Frame(parent_frame)
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
		# Size
		self.size_label = tk.Label(self.plot_arguments_frame, text="Size:")
		self.size_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
		self.size_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.size)
		self.size_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='w')
		# Style
		self.style_label = tk.Label(self.plot_arguments_frame, text="Style:")
		self.style_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
		self.style_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.style)
		self.style_combobox.grid(row=3, column=1, padx=5, pady=5, sticky='w')
		# Row
		self.row_label = tk.Label(self.plot_arguments_frame, text="Row:")
		self.row_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
		self.row_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.row)	
		self.row_combobox.grid(row=4, column=1, padx=5, pady=5, sticky='w')	
		# Col
		self.col_label = tk.Label(self.plot_arguments_frame, text="Col:")
		self.col_label.grid(row=5, column=0, padx=5, pady=5, sticky='w')
		self.col_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.col)
		self.col_combobox.grid(row=5, column=1, padx=5, pady=5, sticky='w')

  

	def toggle_plot_arguments_frame(self):
		if self.plot_arguments_frame_visible:
			self.plot_arguments_frame.pack_forget()
			self.toggle_arguments_button.config(text="Show Plot Arguments")
		else:
			self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
			self.toggle_arguments_button.config(text="Hide Plot Arguments")
		self.plot_arguments_frame_visible = not self.plot_arguments_frame_visible