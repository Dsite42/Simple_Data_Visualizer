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
		tk_root.title("Einfaches Datenanalyse-Programm")

		self.columns_to_analyze = {}
		self.df = None

		open_button = tk.Button(tk_root, text="CSV-Datei öffnen", command=lambda: open_file(self))
		open_button.pack()

		analyze_button = tk.Button(tk_root, text="Analysieren", command=self.analyze)
		analyze_button.pack()

		scatter_button = tk.Button(tk_root, text="Scatter", command=self.show_scatter_plot)
		scatter_button.pack()

		self.columns_frame = tk.Frame(tk_root)
		self.columns_frame.pack()

		tk_root.protocol("WM_DELETE_WINDOW", self.on_close)





		# Erstellen von Tabs für verschiedene Analysen
		self.tab_control = ttk.Notebook(tk_root)
		self.scatter_tab = ttk.Frame(self.tab_control)
		self.histogram_tab = ttk.Frame(self.tab_control)
		self.line_chart_tab = ttk.Frame(self.tab_control)

		self.tab_control.add(self.scatter_tab, text='Scatter Plot')
		self.tab_control.add(self.histogram_tab, text='Histogramm')
		self.tab_control.add(self.line_chart_tab, text='Liniendiagramm')
		self.tab_control.pack(expand=1, fill="both")

		# Initialisieren der Scatter Plot Einstellungen
		self.init_scatter_tab()

		# Initialisieren der Histogramm Einstellungen
		self.init_histogram_tab()

		# Initialisieren der Liniendiagramm Einstellungen
		self.init_line_chart_tab()


	def init_scatter_tab(self):
		print("X")
		# Initialisierung der Scatter Plot Einstellungen
		# ...

	def init_histogram_tab(self):
		print("X")

		# Initialisierung der Histogramm Einstellungen
		# ...

	def init_line_chart_tab(self):
		print("X")
		# Initialisierung der Liniendiagramm Einstellungen
		# ...




	def update_column_checklist(self):
		for widget in self.columns_frame.winfo_children():
			widget.destroy()

		for column in self.df.columns:
			var = tk.BooleanVar()
			checkbox = tk.Checkbutton(self.columns_frame, text=column, variable=var)
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

	def analyze(self):
		selected_columns = self.get_selected_columns()
		print(f"Ausgewählte Spalten für die Analyse: {selected_columns}")
		# Hier können Sie Ihre Analysefunktionen hinzufügen
