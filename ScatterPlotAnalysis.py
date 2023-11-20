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
		self.plot_with = tk.StringVar()
		self.plot_hight = tk.StringVar()
		self.scatter_last_window = None
		self.scatter_last_canvas = None

		#plot_args
		self.plot_arguments_frame_visible = True
		self.hue = tk.StringVar()
		self.size = tk.StringVar()
		self.style = tk.StringVar()

 
 
 
	def create_plot_args(self):
		selected_columns = self.main_app.get_selected_columns()
		plot_args = {"x": selected_columns[0], "y": selected_columns[1], "data": self.main_app.df}
		if self.hue.get():
			plot_args["hue"] = self.hue.get()
		if self.size.get():
			plot_args["size"] = self.size.get()
		if self.style.get():
			plot_args["style"] = self.style.get()
		return plot_args
 
	def show_scatter_plot(self, refresh_plot):
		selected_columns = self.main_app.get_selected_columns()
		plot_args = self.create_plot_args()
		if len(selected_columns) == 2:
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
				self.scatter_last_canvas = self.display_refresh_plot(fig, self.scatter_last_canvas)
			else:
				self.scatter_last_window, self.scatter_last_canvas = self.display_plot(fig, self.scatter_last_window, self.scatter_last_canvas)
		else:
			messagebox.showinfo("Information", "Select two Columns")

	def display_refresh_plot(self, fig, scatter_last_canvas):
		#canvas = FigureCanvasTkAgg(fig, master=self.last_window)
		scatter_last_canvas.get_tk_widget().destroy()
		scatter_last_canvas = FigureCanvasTkAgg(fig, master=self.scatter_last_window)
		scatter_last_canvas.draw()
		width = fig.get_figwidth() * fig.dpi
		height = fig.get_figheight() * fig.dpi
		self.scatter_last_window.geometry(f"{int(width)}x{int(height)}")
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
  
		# Button to show and hide more plot aguments
		self.toggle_arguments_button = tk.Button(button_frame, text="Hide Plot Arguments", command=self.toggle_plot_arguments_frame)
		self.toggle_arguments_button.pack(padx=5, pady=5)


		# Frame for main plot args
		main_plot_arguments_frame = tk.Frame(parent_frame)
		main_plot_arguments_frame.pack(padx=5, pady=5, anchor='w')
		# Eingabefeld für den Titel des Scatter Plots
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
		# Hue
		self.hue_label = tk.Label(self.plot_arguments_frame, text="Hue:")
		self.hue_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
		self.hue_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.hue)
		self.hue_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
		# Size
		self.size_label = tk.Label(self.plot_arguments_frame, text="Size:")
		self.size_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
		self.size_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.size)
		self.size_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
		# Style
		self.style_label = tk.Label(self.plot_arguments_frame, text="Style:")
		self.style_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
		self.style_combobox = ttk.Combobox(self.plot_arguments_frame, textvariable=self.style)
		self.style_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='w')
  
	def toggle_plot_arguments_frame(self):
		if self.plot_arguments_frame_visible:
			self.plot_arguments_frame.pack_forget()
			self.toggle_arguments_button.config(text="Show Plot Arguments")
		else:
			self.plot_arguments_frame.pack(padx=5, pady=5, fill='x')
			self.toggle_arguments_button.config(text="Hide Plot Arguments")
		self.plot_arguments_frame_visible = not self.plot_arguments_frame_visible