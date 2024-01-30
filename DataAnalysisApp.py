import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from input_data import open_file
from tkinter import ttk

from RelPlotAnalysis import RelPlotAnalysis
from PairPlotAnalysis import PairPlotAnalysis
from ManualPlotAnalysis import ManualPlotAnalysis
from ConsoleOutput import ConsoleOutput
from ManipulateDataWindow import ManipulateDataWindow
from JointPlotAnalysis import JointPlotAnalysis
from DisPlotAnalysis import DisPlotAnalysis
from CatPlotAnalysis import CatPlotAnalysis
from LmPlotAnalysis import LmPlotAnalysis
import sys
from cefpython3 import cefpython as cef


class DataAnalysisApp:
	# Constructor
	def __init__(self, operating_system):
		self.tk_root = tk.Tk()
		#tk_root.geometry("400x800")
		self.tk_root.title("Simple Data Analyzer")
		self.tk_root.protocol("WM_DELETE_WINDOW", self.on_close)
		## set the scaling
		#scale_factor = 1.0
		#tk_root.tk.call('tk', 'scaling', scale_factor)
		self.operating_system = operating_system
		print("OS: ", self.operating_system)
  
		self.cef_loop()
  
		# Open Windows
		self.open_windows = []


		self.columns_to_analyze = {}
		self.df = None
  
		# Input_Data Frame
		input_data_frame = tk.Frame(self.tk_root)
		input_data_frame.pack(padx=5, pady=5)
		# Button to open csv
		open_button = tk.Button(input_data_frame, text="Open CSV file", command=lambda: open_file(self))
		open_button.pack(side=tk.LEFT, padx=5, pady=5)

		# Button for data manipulation
		data_manipulation_button = tk.Button(input_data_frame, text="Manipulate Data", command=lambda: ManipulateDataWindow(self))
		data_manipulation_button.pack(side=tk.RIGHT, padx=5, pady=5)
  
		# checkbox for use plotly
		self.use_plotly = tk.BooleanVar(value=False)
		self.use_plotly_checkbox = tk.Checkbutton(input_data_frame, text="Use Plotly", variable=self.use_plotly)
		self.use_plotly_checkbox.pack(side=tk.RIGHT, padx=5, pady=5)

		# dataframes
		dataframes_frame = tk.Frame(self.tk_root)
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



		# CSV columns frame with scrollable area
		self.columns_frame = tk.Frame(self.tk_root)
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


		# Tab Control
		self.current_tab = None
		self.tab_control = ttk.Notebook(self.tk_root)
		self.rel_tab_frame = ttk.Frame(self.tab_control)
		self.pairplot_tab_frame = ttk.Frame(self.tab_control)
		self.jointplot_tab_frame = ttk.Frame(self.tab_control)
		self.displot_tab_frame = ttk.Frame(self.tab_control)
		self.catplot_tab_frame = ttk.Frame(self.tab_control)
		self.lmplot_tab_frame = ttk.Frame(self.tab_control)
		self.manual_plot_tab_frame = ttk.Frame(self.tab_control)
		self.console_output_tab_frame = ttk.Frame(self.tab_control)

		self.tab_control.add(self.rel_tab_frame, text='Rel Plot')
		self.tab_control.add(self.pairplot_tab_frame, text='Pair Plot')
		self.tab_control.add(self.jointplot_tab_frame, text='Joint Plot')
		self.tab_control.add(self.displot_tab_frame, text='Dis Plot')
		self.tab_control.add(self.catplot_tab_frame, text='Cat Plot')
		self.tab_control.add(self.lmplot_tab_frame, text='Lm Plot')
		self.tab_control.add(self.manual_plot_tab_frame, text='Manual Plot')
		self.tab_control.add(self.console_output_tab_frame, text='Console Output')
  
		self.tab_control.pack(expand=1, fill="both")
  
		self.rel_analysis = RelPlotAnalysis(self)
		self.pairplot_analysis = None
		self.jointplot_analysis = None
		self.displot_analysis = None
		self.catplot_analysis = None
		self.lmplot_analysis = None
		self.manual_plot_analysis = ManualPlotAnalysis(self)
		self.console_output = ConsoleOutput(self)
		sys.stdout = self.console_output
		sys.stderr = self.console_output

        
		# Event-Handler for tab change
		self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)


	def run(self):
		self.cefpython = cef.Initialize()
		self.tk_root.mainloop()


	def on_tab_changed(self, event):
		selected_tab = event.widget.select()
		tab_text = event.widget.tab(selected_tab, "text")

		if self.current_tab == "Manual Plot":
			self.manual_plot_analysis.save_code_text()

		if tab_text == "Rel Plot":
			self.rel_analysis.init_ui()
		elif tab_text == "Pair Plot":
			if self.pairplot_analysis is None:
				self.pairplot_analysis = PairPlotAnalysis(self)
			self.pairplot_analysis.init_ui()
		elif tab_text == "Joint Plot":
			if self.jointplot_analysis is None:
				self.jointplot_analysis = JointPlotAnalysis(self)
			self.jointplot_analysis.init_ui()
		elif tab_text == "Dis Plot":
			if self.displot_analysis is None:
				self.displot_analysis = DisPlotAnalysis(self)
			self.displot_analysis.init_ui()
		elif tab_text == "Cat Plot":
			if self.catplot_analysis is None:
				self.catplot_analysis = CatPlotAnalysis(self)
			self.catplot_analysis.init_ui()
		elif tab_text == "Lm Plot":
			if self.lmplot_analysis is None:
				self.lmplot_analysis = LmPlotAnalysis(self)
			self.lmplot_analysis.init_ui()
		elif tab_text == "Manual Plot":
			if self.manual_plot_analysis is None:
				self.manual_plot_analysis = ManualPlotAnalysis(self)
			self.manual_plot_analysis.init_ui()

		self.current_tab = tab_text



	def on_dataframe_selected(self, event=None):
		self.df = self.dataframes[self.dataframes_combobox.get()]
		self.update_column_checklist()
		if self.rel_analysis:
			self.rel_analysis.load_argument_values()
		if self.pairplot_analysis:
			self.pairplot_analysis.load_argument_values()
		if self.jointplot_analysis:
			self.jointplot_analysis.load_argument_values()
		if self.displot_analysis:
			self.displot_analysis.load_argument_values()
		if self.catplot_analysis:
			self.catplot_analysis.load_argument_values()
		if self.lmplot_analysis:
			self.lmplot_analysis.load_argument_values()
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
		#if messagebox.askokcancel("Close", "Do you really want to close the program?"):
		self.tk_root.destroy()
		self.tk_root.quit()
		cef.Shutdown()


	def get_selected_columns(self):
		return [col_checkbox["text"] for col_checkbox in self.columns_to_analyze.values() if col_checkbox["var"].get()]

	def show_rel_plot(self):
		self.rel_analysis = RelPlotAnalysis(self)
		self.rel_analysis.show_rel_plot()

	def cef_loop(self):
		cef.MessageLoopWork()
		self.tk_root.after(10, self.cef_loop)



