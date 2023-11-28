from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import matplotlib.pyplot as plt
from PlotWindow import PlotWindow


class BaseAnalysis:
	def __init__(self):
		pass

	def display_plot(self, fig):
		new_plot_window = PlotWindow(self.main_app, plot_title=self.plot_title.get())
		new_plot_window.display_plot(fig)
		return new_plot_window

	def display_refresh_plot(self, fig):
		self.main_app.open_windows[-1].refresh_plot(fig)
