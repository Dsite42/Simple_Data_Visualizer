from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import matplotlib.pyplot as plt


class BaseAnalysis:
	def __init__(self):
		pass

	def display_plot(self, fig, last_window, last_canvas):
		last_window = tk.Toplevel(self.main_app.tk_root)
		last_window.title(self.plot_title.get())
		save_button = tk.Button(last_window, text="Save Plot", command=lambda: self.save_plot(fig))
		save_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')
  
		copy_button = tk.Button(last_window, text="Copy Plot", command=lambda: self.copy_plot(fig))
		copy_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

		last_canvas = FigureCanvasTkAgg(fig, master=last_window)
		last_canvas.draw()
		last_canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')
  
		## Den Plot als Bild in einen BytesIO-Buffer speichern
		#buf = io.BytesIO()
		#plt.savefig(buf, format='png')
		#buf.seek(0)
#
		## Das Bild aus dem Buffer in die Zwischenablage kopieren
		#image = Image.open(buf)
		#output = io.BytesIO()
		#image.convert("RGB").save(output, "BMP")
		#data = output.getvalue()[14:]
		#output.close()
#
		#win32clipboard.OpenClipboard()
		#win32clipboard.EmptyClipboard()
		#win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
		#win32clipboard.CloseClipboard()
#
		#buf.close()

		return last_window, last_canvas

	def display_refresh_plot(self, fig, last_canvas):
		#canvas = FigureCanvasTkAgg(fig, master=self.last_window)
		last_canvas.get_tk_widget().destroy()
		last_canvas = FigureCanvasTkAgg(fig, master=self.last_window)
		last_canvas.draw()
		width = fig.get_figwidth() * fig.dpi
		height = fig.get_figheight() * fig.dpi
		additional_row_height = 50
		self.last_window.geometry(f"{int(width)}x{int(height + additional_row_height)}")
		last_canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')
		return last_canvas

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
   
	def copy_plot(self, fig):
		if self.main_app.operating_system == "Windows":
			import io
			from PIL import Image
			import win32clipboard

			plot_title = fig._suptitle.get_text() if fig._suptitle else "MyPlot"
			# Den Plot als Bild in einen BytesIO-Buffer speichern
			buf = io.BytesIO()
			plt.savefig(buf, format='png')
			buf.seek(0)

			# Das Bild aus dem Buffer in die Zwischenablage kopieren
			image = Image.open(buf)
			output = io.BytesIO()
			image.convert("RGB").save(output, "BMP")
			data = output.getvalue()[14:]
			output.close()

			win32clipboard.OpenClipboard()
			win32clipboard.EmptyClipboard()
			win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
			win32clipboard.CloseClipboard()

			buf.close()

		if self.main_app.operating_system == "Linux":
			import io
			import subprocess
			# Den Plot als PNG-Bild in einen BytesIO-Buffer speichern
			buf = io.BytesIO()
			fig.savefig(buf, format='png')
			buf.seek(0)

			# Das Bild an xclip übergeben, um es in die Zwischenablage zu kopieren
			# Hier wird das Bild in der PNG-Form an die Zwischenablage gesendet
			process = subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'], stdin=subprocess.PIPE)
			process.communicate(input=buf.getvalue())

			buf.close()