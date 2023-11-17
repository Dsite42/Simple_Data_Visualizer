import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from BaseAnalysis import BaseAnalysis

class ScatterPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app

	def perform_analysis(self):
		# Implementierung der Scatter Plot Analyse
		selected_columns = self.main_app.get_selected_columns()
		fig = plt.figure(figsize=(8, 6))
		plt.scatter(self.main_app.df[selected_columns[0]], self.main_app.df[selected_columns[1]])
		plt.xlabel(selected_columns[0])
		plt.ylabel(selected_columns[1])
		plt.title("Scatter Plot")
		return fig

	def show_scatter_plot(self):
		fig = self.perform_analysis()
		if fig:
			new_window = tk.Toplevel(self.main_app.tk_root)
			new_window.title("Streudiagramm")

			canvas = FigureCanvasTkAgg(fig, master=new_window)
			canvas.draw()
			canvas.get_tk_widget().pack()