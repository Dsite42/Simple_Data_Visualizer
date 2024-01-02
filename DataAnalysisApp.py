import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from input_data import open_file
from tkinter import ttk

from RelPlotAnalysis import RelPlotAnalysis
from ManualPlotAnalysis import ManualPlotAnalysis
from ConsoleOutput import ConsoleOutput
from ManipulateDataWindow import ManipulateDataWindow
import sys

class DataAnalysisApp:
	# Constructor
	def __init__(self, tk_root, operating_system):
		self.tk_root = tk_root
		self.operating_system = operating_system
		#tk_root.geometry("400x800")
		tk_root.title("Einfaches Datenanalyse-Programm")
		print("OS: ", self.operating_system)
  
		# Open Windows
		self.open_windows = []


		self.columns_to_analyze = {}
		self.df = None
		self.use_plotly = True
  
		# Input_Data Frame
		input_data_frame = tk.Frame(tk_root)
		input_data_frame.pack(padx=5, pady=5)
		# Button to open csv
		open_button = tk.Button(input_data_frame, text="Open CSV file", command=lambda: open_file(self))
		open_button.pack(side=tk.LEFT, padx=5, pady=5)

		# Button for data manipulation
		data_manipulation_button = tk.Button(input_data_frame, text="Manipulate Data", command=lambda: ManipulateDataWindow(self))
		data_manipulation_button.pack(side=tk.RIGHT, padx=5, pady=5)

		# dataframes
		dataframes_frame = tk.Frame(tk_root)
		dataframes_frame.pack(padx=5, pady=5)
		# set dataframe index
		self.dataframes = {}
		self.dataframes_label = tk.Label(dataframes_frame, text="Dataframes:")
		self.dataframes_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
		self.dataframes_combobox = ttk.Combobox(dataframes_frame)
		self.dataframes_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
		self.dataframes_combobox.bind("<<ComboboxSelected>>", self.on_dataframe_selected)
  
		# Select x axis
		self.x_axis_label = tk.Label(dataframes_frame, text="x-axis:")
		self.x_axis_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
		self.x_axis_combobox = ttk.Combobox(dataframes_frame)
		self.x_axis_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='w')


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
		self.current_tab = None
		self.tab_control = ttk.Notebook(tk_root)
		self.rel_tab_frame = ttk.Frame(self.tab_control)
		self.histogram_tab = ttk.Frame(self.tab_control)
		self.line_chart_tab = ttk.Frame(self.tab_control)
		self.manual_plot_tab_frame = ttk.Frame(self.tab_control)
		self.console_output_tab_frame = ttk.Frame(self.tab_control)

		self.tab_control.add(self.rel_tab_frame, text='Rel Plot')
		self.tab_control.add(self.histogram_tab, text='Histogramm')
		self.tab_control.add(self.line_chart_tab, text='Liniendiagramm')
		self.tab_control.add(self.manual_plot_tab_frame, text='Manual Plot')
		self.tab_control.add(self.console_output_tab_frame, text='Console Output')
  
		self.tab_control.pack(expand=1, fill="both")
  
		# Objekte für die verschiedenen Analysen erstellen
		self.rel_analysis = RelPlotAnalysis(self)
		self.histogram_analysis = None  # Erstellen Sie hier das Histogramm-Analyseobjekt
		self.line_chart_analysis = None  # Erstellen Sie hier das Liniendiagramm-Analyseobjekt
		self.manual_plot_analysis = ManualPlotAnalysis(self)
		self.console_output = ConsoleOutput(self)
		sys.stdout = self.console_output
		sys.stderr = self.console_output

        
		# Event-Handler für Tabwechsel
		self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)


	def on_tab_changed(self, event):
		selected_tab = event.widget.select()
		tab_text = event.widget.tab(selected_tab, "text")

		if self.current_tab == "Manual Plot":
			#if self.manual_plot_analysis is not None:
			self.manual_plot_analysis.save_code_text()

		if tab_text == "Rel Plot":
			self.rel_analysis.init_ui()
		elif tab_text == "Histogramm":
			if self.histogram_analysis is None:
				self.histogram_analysis = HistogramAnalysis(self)
			self.histogram_analysis.init_ui(self.histogram_tab)
		elif tab_text == "Liniendiagramm":
			if self.line_chart_analysis is None:
				self.line_chart_analysis = LineChartAnalysis(self)
			self.line_chart_analysis.init_ui(self.line_chart_tab)
		elif tab_text == "Manual Plot":
			if self.manual_plot_analysis is None:
				self.manual_plot_analysis = ManualPlotAnalysis(self)
			self.manual_plot_analysis.init_ui()

		self.current_tab = tab_text



	def on_dataframe_selected(self, event=None):
		self.df = self.dataframes[self.dataframes_combobox.get()]
		self.update_column_checklist()
		self.rel_analysis.load_argument_values()
		self.x_axis_combobox['values'] = list(self.df.columns)


	def update_column_checklist(self):
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()

		self.columns_to_analyze = {}
		for column in self.dataframes[self.dataframes_combobox.get()].columns:
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

	def show_rel_plot(self):
		self.rel_analysis = RelPlotAnalysis(self)
		self.rel_analysis.show_rel_plot()
