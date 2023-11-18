import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox
from BaseAnalysis import BaseAnalysis

class ScatterPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Scatter Plot")

	def show_scatter_plot(self):
		selected_columns = self.main_app.get_selected_columns()
		if len(selected_columns) == 2:
			fig = plt.figure(figsize=(8, 6))
			plt.scatter(self.main_app.df[selected_columns[0]], self.main_app.df[selected_columns[1]])
			plt.xlabel(selected_columns[0])
			plt.ylabel(selected_columns[1])
			plt.title(self.plot_title.get())
			self.display_plot(fig)
		else:
			messagebox.showinfo("Information", "Select two Columns")

	def display_plot(self, fig):
		new_window = tk.Toplevel(self.main_app.tk_root)
		new_window.title(self.plot_title.get())

		canvas = FigureCanvasTkAgg(fig, master=new_window)
		canvas.draw()
		canvas.get_tk_widget().pack()

   
	def init_ui(self, parent_frame):
		# Zuvor erstellte Widgets im parent_frame entfernen
		for widget in parent_frame.winfo_children():
			widget.destroy()

		# Frame für den Button
		button_frame = tk.Frame(parent_frame)
		button_frame.pack(padx=5, pady=5)

		# Button zum Anzeigen des Scatter Plots
		show_plot_button = tk.Button(button_frame, text="Show Plot", command=self.show_scatter_plot)
		show_plot_button.pack(padx=5, pady=5)
     

		# Frame für den Titel und das Eingabefeld
		title_frame = tk.Frame(parent_frame)
		title_frame.pack(padx=5, pady=5)

		# Eingabefeld für den Titel des Scatter Plots
		title_label = tk.Label(title_frame, text="Title:")
		title_label.pack(side=tk.LEFT, padx=5, pady=5)

		title_entry = tk.Entry(title_frame, textvariable=self.plot_title)
		title_entry.pack(side=tk.LEFT, padx=5, pady=5)

