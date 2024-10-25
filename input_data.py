import pandas as pd
from tkinter import filedialog, simpledialog, messagebox
import tkinter as tk

def read_csv(file_path, separator):
	try:
		df = pd.read_csv(file_path, sep=separator)
		return df, None
	except Exception as e:
		return None, str(e)

def open_file(self):
	file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
	if file_path:
		# Ask the user for the CSV separator
		separator = simpledialog.askstring("CSV Separator", "Enter the CSV separator (e.g., ',' or ';'):", initialvalue=';')
		if separator is not None:
			df, error = read_csv(file_path, separator)
			if error:
				messagebox.showerror("Error reading CSV file", error)
			else:
				file_name = file_path.split('/')[-1] 
				self.dataframes[file_name] = df.reset_index()

	# Update the UI after successful file read
	self.dataframes_combobox['values'] = list(self.dataframes.keys())
	self.dataframes_combobox.set(file_name)
	self.df = self.dataframes[self.dataframes_combobox.get()]
	self.on_dataframe_selected()
