from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class BaseAnalysis:
	def __init__(self):
		pass

	def display_plot(self, fig, scatter_last_window, scatter_last_canvas):
		scatter_last_window = tk.Toplevel(self.main_app.tk_root)
		scatter_last_window.title(self.plot_title.get())
		save_button = tk.Button(scatter_last_window, text="Save Plot", command=lambda: self.save_plot(fig))
		save_button.pack()

		scatter_last_canvas = FigureCanvasTkAgg(fig, master=scatter_last_window)
		scatter_last_canvas.draw()
		scatter_last_canvas.get_tk_widget().pack()
		return scatter_last_window, scatter_last_canvas

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

	def save_plot(self, fig):
		plot_title = fig._suptitle.get_text() if fig._suptitle else "MyPlot"
		filepath = filedialog.asksaveasfilename(
			defaultextension='',
			filetypes=[("PNG files", "*.png"), ("All Files", "*.*")],
			title="Save plot",
			initialfile= plot_title
		)
		if filepath:
			fig.savefig(filepath)
