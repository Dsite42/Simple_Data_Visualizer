import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data_analysis import create_scatter_plot
from input_data import open_file
from tkinter import ttk

from ScatterPlotAnalysis import ScatterPlotAnalysis

class DataAnalysisApp:
	# Constructor
	def __init__(self, tk_root):
		self.tk_root = tk_root
		#tk_root.geometry("800x600")
		tk_root.title("Einfaches Datenanalyse-Programm")

		self.columns_to_analyze = {}
		self.df = None
  
		# Input_Data Frame
		input_data_frame = tk.Frame(tk_root)
		input_data_frame.pack(padx=5, pady=5)

		# Button to open csv
		open_button = tk.Button(input_data_frame, text="Open CSV file", command=lambda: open_file(self))
		open_button.pack(side=tk.LEFT, padx=5, pady=5)

		# Closing main window
		tk_root.protocol("WM_DELETE_WINDOW", self.on_close)

		# CSV columns frame with scrollable area
		self.columns_frame = tk.Frame(tk_root)
		self.columns_frame.pack()

		# Scrollable area for columns
		self.columns_canvas = tk.Canvas(self.columns_frame)
		self.columns_scrollbar = tk.Scrollbar(self.columns_frame, orient="vertical", command=self.columns_canvas.yview)
		self.scrollable_frame = tk.Frame(self.columns_canvas)

		self.scrollable_frame.bind(
			"<Configure>",
			lambda e: self.columns_canvas.configure(
				scrollregion=self.columns_canvas.bbox("all")
			)
		)

		self.columns_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
		self.columns_canvas.configure(yscrollcommand=self.columns_scrollbar.set)

		self.columns_canvas.pack(side="left", fill="both", expand=True)
		self.columns_scrollbar.pack(side="right", fill="y")



		# Erstellen von Tabs für verschiedene Analysen
		self.tab_control = ttk.Notebook(tk_root)
		self.scatter_tab = ttk.Frame(self.tab_control)
		self.histogram_tab = ttk.Frame(self.tab_control)
		self.line_chart_tab = ttk.Frame(self.tab_control)

		self.tab_control.add(self.scatter_tab, text='Scatter Plot')
		self.tab_control.add(self.histogram_tab, text='Histogramm')
		self.tab_control.add(self.line_chart_tab, text='Liniendiagramm')
		self.tab_control.pack(expand=1, fill="both")
  
		# Objekte für die verschiedenen Analysen erstellen
		self.scatter_analysis = ScatterPlotAnalysis(self)
		self.histogram_analysis = None  # Erstellen Sie hier das Histogramm-Analyseobjekt
		self.line_chart_analysis = None  # Erstellen Sie hier das Liniendiagramm-Analyseobjekt

		# UI der Analysen initialisieren
		self.scatter_analysis.init_ui(self.scatter_tab)  
		# Event-Handler für Tabwechsel
		self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)


	def on_tab_changed(self, event):
		selected_tab = event.widget.select()
		tab_text = event.widget.tab(selected_tab, "text")

		if tab_text == "Scatter Plot":
			self.scatter_analysis.init_ui(self.scatter_tab)
		elif tab_text == "Histogramm":
			if self.histogram_analysis is not None:
				self.histogram_analysis = HistogramAnalysis(self)
			self.histogram_analysis.init_ui(self.histogram_tab)
		elif tab_text == "Liniendiagramm":
			if self.line_chart_analysis is not None:
				self.line_chart_analysis = LineChartAnalysis(self)
			self.line_chart_analysis.init_ui(self.line_chart_tab)

	def update_column_checklist(self):
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()

		for column in self.df.columns:
			var = tk.BooleanVar()
			checkbox = tk.Checkbutton(self.scrollable_frame, text=column, variable=var)
			checkbox.pack(anchor='w')
			self.columns_to_analyze[column] = {"var": var, "text": column}
			
	def on_close(self):
		#if messagebox.askokcancel("Schließen", "Wollen Sie das Programm wirklich beenden?"):
		self.tk_root.destroy()
		self.tk_root.quit()

	def get_selected_columns(self):
		return [col_checkbox["text"] for col_checkbox in self.columns_to_analyze.values() if col_checkbox["var"].get()]

	def show_scatter_plot(self):
		self.scatter_analysis = ScatterPlotAnalysis(self)
		self.scatter_analysis.show_scatter_plot()
