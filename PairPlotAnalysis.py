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

class PairPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Pair Plot")
		self.plot_with = tk.StringVar()
		self.plot_hight = tk.StringVar()
		self.last_window = None
		self.last_canvas = None

		#plot_args
		self.kind = tk.StringVar()
		self.diag_kind = tk.StringVar()
		self.hue = tk.StringVar()
		self.corner = tk.StringVar()

 
 
	def create_plot_args(self, data):
		selected_columns = self.main_app.get_selected_columns()     
		plot_args = {"vars": selected_columns if len(selected_columns) >= 1 else None, "data": data}
		if self.main_app.use_plotly.get() == False:
			if self.hue.get():
				plot_args["hue"] = self.hue.get()
			if self.kind.get():
				plot_args["kind"] = self.kind.get()
			if self.diag_kind.get():
				plot_args["diag_kind"] = self.diag_kind.get()
			if self.corner.get():
				plot_args["corner"] = self.corner.get()
    
		else:
			plot_args = {"dimensions": selected_columns if len(selected_columns) >= 1 else None, "data_frame": data}
			if len(selected_columns) == 2 and self.hue.get():
				plot_args["color"] = self.hue.get()

		return plot_args
 
	def show_pair_plot(self, refresh_plot):
		selected_columns = self.main_app.get_selected_columns()
		
		if self.main_app.use_plotly.get() == False:
  			# Create a Seaborn pair plot
			plot_args = self.create_plot_args(self.main_app.df)
			g = sns.pairplot(**plot_args)

			fig = g.fig
			if self.plot_with.get() and self.plot_hight.get():
				fig.set_size_inches(float(self.plot_with.get()), float(self.plot_hight.get()))
			fig.suptitle(self.plot_title.get(), verticalalignment='top', fontsize=12)
			fig.subplots_adjust(top=0.94)
      
		else:
			# Create a Plotly pair plot
   
			# Not supported plots in plotly: kde, hist, reg
			if self.kind.get() == "kde" or self.kind.get() == "hist" or self.kind.get() == "reg":
				messagebox.showinfo("Info", "Plotly does not support the kind: " + self.kind.get())
				return

			plot_args = self.create_plot_args(self.main_app.df)
			fig = px.scatter_matrix(**plot_args)
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
			for i, ax in enumerate(g.axes.flatten()):
				if ax == event.inaxes:
					row, col = divmod(i, len(g.axes))
					x_var = g.x_vars[col]
					y_var = g.y_vars[row]
					self.show_clicked_plot(x_var, y_var)
					break
 
		# add event-handeler for clicking on facets
		if self.main_app.use_plotly.get() == False:
			g.fig.canvas.mpl_connect('button_press_event', on_click)

	def show_clicked_plot(self, x_var, y_var):
		fig, ax = plt.subplots()
		if self.kind.get() == "scatter" or self.kind.get() == "":
			g = sns.scatterplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax, hue=self.hue.get() if self.hue.get() else None)
		elif self.kind.get() == "kde":
			g = sns.kdeplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax, hue=self.hue.get() if self.hue.get() else None)
		elif self.kind.get() == "hist":
			g = sns.histplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax, hue=self.hue.get() if self.hue.get() else None)
		elif self.kind.get() == "reg":
			g = sns.regplot(x=x_var, y=y_var, data=self.main_app.df, ax=ax, hue=self.hue.get() if self.hue.get() else None)
		
		if self.plot_with.get() and self.plot_hight.get():
			fig.set_size_inches(float(self.plot_with.get()), float(self.plot_hight.get()))
		fig.suptitle(self.plot_title.get(), verticalalignment='top', fontsize=12)
		fig.subplots_adjust(top=0.94)

		self.main_app.open_windows.append(self.display_plot(fig))


	def init_ui(self):
		self.plot_arguments_frame_visible = True
  		# Remove previously created widgets in the parent_frame
		for widget in self.main_app.pairplot_tab_frame.winfo_children():
			widget.destroy()
   

		# Frame for buttons
		button_frame = tk.Frame(self.main_app.pairplot_tab_frame)
		button_frame.pack(padx=5, pady=5, anchor='c')

		# Button to show Pair Plot in new window
		show_plot_button = tk.Button(button_frame, text="Show Plot", command=lambda: self.show_pair_plot(False))
		show_plot_button.grid(row=0, column=0, padx=5)
  
		# Button to refresh Pair Plot in same window
		show_plot_button = tk.Button(button_frame, text="Refresh Plot", command=lambda: self.show_pair_plot(True))
		show_plot_button.grid(row=0, column=1, padx=5)
  
		# Button to show and hide more plot aguments
		self.toggle_arguments_button = tk.Button(button_frame, text="Hide Arguments", command=self.toggle_plot_arguments_frame)
		self.toggle_arguments_button.grid(row=0, column=2, padx=5)


		# Frame for main plot args
		main_plot_arguments_frame = tk.Frame(self.main_app.pairplot_tab_frame)
		main_plot_arguments_frame.pack(padx=5, pady=5, anchor='w')
		# Entry for plot title
		title_label = tk.Label(main_plot_arguments_frame, text="Plot title:")
		title_label.grid(row=0, column=0, padx=5)
		title_entry = tk.Entry(main_plot_arguments_frame, textvariable=self.plot_title)
		title_entry.grid(row=0, column=1)  
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
		self.plot_arguments_frame = tk.Frame(self.main_app.pairplot_tab_frame)
		self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
		# Kind
		self.kind_label = tk.Label(self.plot_arguments_frame, text="Kind:")
		self.kind_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
		self.kind_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.kind)
		self.kind_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
		# Diag_Kind
		self.diag_kind_label = tk.Label(self.plot_arguments_frame, text="Diag Kind:")
		self.diag_kind_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
		self.diag_kind_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.diag_kind)
		self.diag_kind_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
		# Hue
		self.hue_label = tk.Label(self.plot_arguments_frame, text="Hue:")
		self.hue_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
		self.hue_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.hue)
		self.hue_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='w')
		# Corner
		self.corner_label = tk.Label(self.plot_arguments_frame, text="Corner:")
		self.corner_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
		self.corner_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.corner)
		self.corner_combobox.grid(row=3, column=1, padx=5, pady=5, sticky='w')

		self.load_argument_values()


	def load_argument_values(self):
		if self.main_app.df is not None:
			self.main_app.pairplot_analysis.kind_combobox['values'] = ['scatter', 'kde', 'hist', 'reg']
			self.main_app.pairplot_analysis.diag_kind_combobox['values'] = ['auto', 'hist', 'kde', None]
			self.main_app.pairplot_analysis.hue_combobox['values'] = list(self.main_app.df.columns)
			self.main_app.pairplot_analysis.corner_combobox['values'] = [True, False]

  
	def toggle_plot_arguments_frame(self):
		if self.plot_arguments_frame_visible:
			self.plot_arguments_frame.pack_forget()
			self.toggle_arguments_button.config(text="Show Plot Arguments")
		else:
			self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
			self.toggle_arguments_button.config(text="Hide Plot Arguments")
		self.plot_arguments_frame_visible = not self.plot_arguments_frame_visible
