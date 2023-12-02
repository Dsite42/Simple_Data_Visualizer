import pandas as pd
from tkinter import filedialog, messagebox
import tkinter as tk

def read_csv(file_path):
	try:
		df = pd.read_csv(file_path, sep=';')
		return df, None
	except Exception as e:
		return None, str(e)

def open_file(self):
	file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
	if file_path:
		#self.df, error = pd.read_csv(file_path)
		self.df = pd.read_csv(file_path, sep=';')
		#if error:
		#	messagebox.showerror("Fehler beim Einlesen der Datei", error)
		#else:
		self.update_column_checklist()
		self.rel_analysis.load_argument_values()

		self.datetime_combobox['values'] = list(self.df.columns)

