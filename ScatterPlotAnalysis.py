import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from BaseAnalysis import BaseAnalysis
import seaborn as sns
sns.set(style="darkgrid")

class ScatterPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Scatter Plot")
		self.title_x_axis = tk.StringVar()
		self.title_y_axis = tk.StringVar()
		self.scatter_last_window = None
		self.scatter_last_canvas = None

		#plot_args
		self.hue = tk.StringVar()

 
 
 
	def create_plot_args(self):
		selected_columns = self.main_app.get_selected_columns()
		plot_args = {"x": selected_columns[0], "y": selected_columns[1], "data": self.main_app.df}
		if self.hue.get():
			plot_args["hue"] = self.hue.get()
		return plot_args
 
	def show_scatter_plot(self, refresh_plot):
		selected_columns = self.main_app.get_selected_columns()
		#plot_args = {"x": selected_columns[0], "y": selected_columns[1], "data": self.main_app.df}
		plot_args = self.create_plot_args()
		if len(selected_columns) == 2:
			# Create a Seaborn relational plot
			g = sns.relplot(**plot_args)
			#g = sns.relplot(x=selected_columns[0], y=selected_columns[1], data=self.main_app.df)
			if self.title_x_axis.get() != "":
				g.set_axis_labels(x_var=self.title_x_axis.get())
			if self.title_y_axis.get() != "":
				g.set_axis_labels(y_var=self.title_y_axis.get())
			fig = g.fig
			fig.set_size_inches(8, 6)
			fig.suptitle(self.plot_title.get(), verticalalignment='top', fontsize=12)
			fig.subplots_adjust(top=0.94)
			if refresh_plot:
				self.scatter_last_canvas = self.display_refresh_plot(fig, self.scatter_last_canvas)
			else:
				self.scatter_last_window, self.scatter_last_canvas = self.display_plot(fig, self.scatter_last_window, self.scatter_last_canvas)
		else:
			messagebox.showinfo("Information", "Select two Columns")

	def display_refresh_plot(self, fig, scatter_last_canvas):
		#canvas = FigureCanvasTkAgg(fig, master=self.last_window)
		scatter_last_canvas.figure = fig
		scatter_last_canvas.draw()
		scatter_last_canvas.get_tk_widget().pack()
		return scatter_last_canvas

	def display_plot(self, fig, scatter_last_window, scatter_last_canvas):
		scatter_last_window = tk.Toplevel(self.main_app.tk_root)
		scatter_last_window.title(self.plot_title.get())

		scatter_last_canvas = FigureCanvasTkAgg(fig, master=scatter_last_window)
		scatter_last_canvas.draw()
		scatter_last_canvas.get_tk_widget().pack()
		return scatter_last_window, scatter_last_canvas

   
	def init_ui(self, parent_frame):
		# Zuvor erstellte Widgets im parent_frame entfernen
		for widget in parent_frame.winfo_children():
			widget.destroy()


		# Frame für den Button
		button_frame = tk.Frame(parent_frame)
		button_frame.pack(padx=5, pady=5)

		# Button zum Anzeigen des Scatter Plots
		show_plot_button = tk.Button(button_frame, text="Show Plot", command=lambda: self.show_scatter_plot(False))
		show_plot_button.pack(side = tk.LEFT, padx=5, pady=5)
  
		# Button zum Erneuern des Scatter Plots
		show_plot_button = tk.Button(button_frame, text="Refresh Plot", command=lambda: self.show_scatter_plot(True))
		show_plot_button.pack(padx=5, pady=5)


		# Frame für den Titel und das Eingabefeld
		title_frame = tk.Frame(parent_frame)
		title_frame.pack(padx=5, pady=5, anchor='w')

		# Eingabefeld für den Titel des Scatter Plots
		title_label = tk.Label(title_frame, text="Plot title:")
		title_label.pack(side=tk.LEFT, padx=5)

		title_entry = tk.Entry(title_frame, textvariable=self.plot_title)
		title_entry.pack(side=tk.LEFT)


		# Frame for axis labels
		axis_frame = tk.Frame(parent_frame)
		axis_frame.pack(padx=5, pady=5, anchor='w')
  
		# Entry for x-axis label
		x_axis_label = tk.Label(axis_frame, text="x-axis title:")
		x_axis_label.pack(side=tk.LEFT, padx=5)
		x_axis_entry = tk.Entry(axis_frame, textvariable=self.title_x_axis)
		x_axis_entry.pack(side=tk.LEFT, padx=5)
  
		# Entry for y-axis label
		y_axis_entry = tk.Entry(axis_frame, textvariable=self.title_y_axis)
		y_axis_entry.pack(side=tk.RIGHT, padx=5)
		y_axis_label = tk.Label(axis_frame, text="y-axis title:")
		y_axis_label.pack(side=tk.RIGHT, padx=5)


		# Frame for plot arguments
		plot_arguments_frame = tk.Frame(parent_frame)
		plot_arguments_frame.pack(padx=5, pady=5, anchor='w')

		# combobox for hue argument
		self.hue_label = tk.Label(plot_arguments_frame, text="hue:")
		self.hue_label.pack(side=tk.LEFT, padx=5)
		self.hue_combobox = ttk.Combobox(plot_arguments_frame, textvariable=self.hue)
		if self.main_app.df is not None:
			self.hue_combobox['values'] = list(self.main_app.df.columns)
		self.hue_combobox.pack(side=tk.LEFT)
  
