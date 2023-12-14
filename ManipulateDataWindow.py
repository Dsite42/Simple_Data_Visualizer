import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import filedialog

class ManipulateDataWindow:
	def __init__(self, main_app):
		self.main_app = main_app
		self.fig = None
		self.canvas = None
		self.window = None
		self.create_window()

	def create_window(self):
		self.window = tk.Toplevel(self.main_app.tk_root)
		self.window.title("Manipulate Data")
		self.window.maxsize(1200, 800)

		# Bind the close event
		self.window.protocol("WM_DELETE_WINDOW", self.on_close)

		# Add buttons and other UI elements here
		save_button = tk.Button(self.window, text="Save Plot", command=lambda: self.save_plot())
		save_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')
  
		copy_button = tk.Button(self.window, text="Copy Plot", command=lambda: self.copy_plot(self.fig))
		copy_button.grid(row=0, column=0, padx=100, pady=5, sticky='w')
		
		set_refresh_button = tk.Button(self.window, text="Set Refresh", command=lambda: self.set_refresh())
		set_refresh_button.grid(row=0, column=0, padx=200, pady=5, sticky='w')

		# Frame für Treeview und Scrollbars
		self.treeview_frame = tk.Frame(self.window)
		self.treeview_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

		# Treeview-Widget hinzufügen
		self.treeview_columns = ["Index"] + list(self.main_app.df.columns)
		self.data_treeview = ttk.Treeview(self.treeview_frame, columns=list(self.treeview_columns), show='headings')
		self.data_treeview.grid(row=0, column=0, sticky='nsew')

		# Vertikale Scrollbar hinzufügen
		self.v_scroll = ttk.Scrollbar(self.treeview_frame, orient='vertical', command=self.data_treeview.yview)
		self.v_scroll.grid(row=0, column=1, sticky='ns')
		self.data_treeview.configure(yscrollcommand=self.v_scroll.set)

		# Horizontale Scrollbar hinzufügen
		self.h_scroll = ttk.Scrollbar(self.treeview_frame, orient='horizontal', command=self.data_treeview.xview)
		self.h_scroll.grid(row=2, column=0, sticky='ew')
		self.data_treeview.configure(xscrollcommand=self.h_scroll.set)

		## Anpassen des Grid-Layouts, um das Treeview-Widget auszudehnen
		self.window.grid_rowconfigure(1, weight=1)
		self.window.grid_columnconfigure(0, weight=1)
		self.treeview_frame.grid_columnconfigure(0, weight=1)
		self.treeview_frame.grid_rowconfigure(0, weight=1)

		# Spaltenüberschriften und -breite definieren
		for col in self.treeview_columns:
			self.data_treeview.heading(col, text=col)
			self.data_treeview.column(col, anchor=tk.CENTER, width=100, stretch=False)

		# DataFrame-Daten hinzufügen
		for index, row in self.main_app.df.iterrows():
			row_data = [index] + list(row)
			self.data_treeview.insert("", tk.END, values=row_data)


		# Frame for data maipulation
		self.data_manipulation_frame = tk.Frame(self.window)
		self.data_manipulation_frame.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
		
		# Dropdown-Menü für die Auswahl von Spalten
		self.delete_columns_menubutton = tk.Menubutton(self.data_manipulation_frame, text="Select columns", relief=tk.RAISED)
		self.delete_columns_menubutton.grid(row=0, column=0, padx=5, pady=5, sticky='w')
		self.delete_columns_menu = tk.Menu(self.delete_columns_menubutton, tearoff=False)
		self.delete_columns_menubutton['menu'] = self.delete_columns_menu

		# Schaltfläche zum Löschen ausgewählter Spalten
		self.delete_columns_button = tk.Button(self.data_manipulation_frame, text="Delete columns", command=self.delete_columns)
		self.delete_columns_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

	   
		# set datetime index
		self.datetime = tk.StringVar()
		self.datetime_label = tk.Label(self.data_manipulation_frame, text="Datetime index:")
		self.datetime_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
		self.datetime_combobox = ttk.Combobox(self.data_manipulation_frame, textvariable=self.datetime)
		self.datetime_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
		self.update_datetime_combobox()
  
		# Entry for format of datetime
		self.datetime_format = tk.StringVar(value = "%d.%m.%Y")
		self.datetime_format_label = tk.Label(self.data_manipulation_frame, text="Datetime format:")
		self.datetime_format_label.grid(row=1, column=2, padx=5, pady=5, sticky='w')	
		self.datetime_format_entry = tk.Entry(self.data_manipulation_frame, textvariable=self.datetime_format)
		self.datetime_format_entry.grid(row=1, column=3, padx=5, pady=5, sticky='w')
  
		# Button to set datetime index
		self.set_datetime_index_button = tk.Button(self.data_manipulation_frame, text="Set", command=self.set_datetime_index)
		self.set_datetime_index_button.grid(row=1, column=4, padx=5, pady=5, sticky='w')
  
		# Button to reset datetime index
		self.reset_datetime_index_button = tk.Button(self.data_manipulation_frame, text="Reset", command=self.reset_datetime_index)
		self.reset_datetime_index_button.grid(row=1, column=5, padx=5, pady=5, sticky='w')


		# Devision and multiplication
		self.basic_arithmetical_operations_label = tk.Label(self.data_manipulation_frame, text="New column:")
		self.basic_arithmetical_operations_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
		self.basic_arithmetical_operations_entry_var = tk.StringVar()
		self.basic_arithmetical_operations_entry = tk.Entry(self.data_manipulation_frame, textvariable=self.basic_arithmetical_operations_entry_var)
		self.basic_arithmetical_operations_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
		self.basic_arithmetical_operations_combobox = ttk.Combobox(self.data_manipulation_frame, values=['+', '-', '*', '/'], state="readonly")
		self.basic_arithmetical_operations_combobox.grid(row=2, column=2, padx=5, pady=5, sticky='w')
  
		self.basic_arithmetical_operations_menubutton = tk.Menubutton(self.data_manipulation_frame, text="Select columns", relief=tk.RAISED)
		self.basic_arithmetical_operations_menubutton.grid(row=2, column=3, padx=5, pady=5, sticky='w')
		self.basic_arithmetical_operations_menu = tk.Menu(self.basic_arithmetical_operations_menubutton, tearoff=False)
		self.basic_arithmetical_operations_menubutton['menu'] = self.basic_arithmetical_operations_menu
  
		self.basic_arithmetical_operations_button = tk.Button(self.data_manipulation_frame, text="Create", command=self.basic_arithmetical_operations)
		self.basic_arithmetical_operations_button.grid(row=2, column=4, padx=5, pady=5, sticky='w')


		# Fill menu buttons
		self.column_vars = {}
		self.selected_columns_order = []
		for col in self.main_app.df.columns:
			boolean_var = tk.BooleanVar()
			self.column_vars[col] = boolean_var
			self.delete_columns_menu.add_checkbutton(label=col, variable=boolean_var)
			self.basic_arithmetical_operations_menu.add_checkbutton(label=col, variable=boolean_var, command=lambda col=col: self.on_checkbutton_toggle(col))


	def on_checkbutton_toggle(self, column_name):
		if self.column_vars[column_name].get():
			# Wenn der Checkbutton aktiviert wurde, fügen Sie den Spaltennamen der Liste hinzu
			if column_name not in self.selected_columns_order:
				self.selected_columns_order.append(column_name)
		else:
			# Wenn der Checkbutton deaktiviert wurde, entfernen Sie den Spaltennamen aus der Liste
			if column_name in self.selected_columns_order:
				self.selected_columns_order.remove(column_name)
	

	def basic_arithmetical_operations(self):
		selected_columns = self.selected_columns_order#[col for col, var in self.column_vars.items() if var.get()]
		if self.basic_arithmetical_operations_combobox.get() and self.basic_arithmetical_operations_entry_var.get() and selected_columns:
			try:
				if self.basic_arithmetical_operations_combobox.get() == '+':
					self.main_app.df[self.basic_arithmetical_operations_entry_var.get()] = self.main_app.df[selected_columns].sum(axis=1)
				elif self.basic_arithmetical_operations_combobox.get() == '-':
					subtration_result = self.main_app.df[selected_columns[0]]
					for col in selected_columns[1:]:
						subtration_result = subtration_result.sub(self.main_app.df[col])
					self.main_app.df[self.basic_arithmetical_operations_entry_var.get()] = subtration_result
				elif self.basic_arithmetical_operations_combobox.get() == '*':
					self.main_app.df[self.basic_arithmetical_operations_entry_var.get()] = self.main_app.df[selected_columns].prod(axis=1)
				elif self.basic_arithmetical_operations_combobox.get() == '/':
					division_result = self.main_app.df[selected_columns[0]]
					for col in selected_columns[1:]:
						division_result = division_result.div(self.main_app.df[col])
					self.main_app.df[self.basic_arithmetical_operations_entry_var.get()] = division_result
			except Exception as e:
				messagebox.showerror("Fehler", f"Fehler bei der Berechnung: {e}")
			self.refresh_treeview()
			self.update_column_select_menu()
			self.update_datetime_combobox()
		else:
			messagebox.showinfo("Information", "Bitte Spalten auswählen und einen Spaltennamen eingeben")
  
	def set_datetime_index(self):
		column_name = self.datetime_combobox.get()	
		if column_name in self.main_app.df.columns:
			try:
				# Konvertierung der Spalte in datetime
				self.main_app.df[column_name] = pd.to_datetime(self.main_app.df[column_name], format=self.datetime_format.get())	
				# Setzen der Spalte als Index
				self.main_app.df.set_index(column_name, inplace=True, drop=False)
				# Aktualisierung der Ansicht
				self.refresh_treeview()
			except Exception as e:
				# Anzeigen des Fehlers in einer MessageBox
				messagebox.showerror("Fehler", f"Fehler bei der Konvertierung in datetime: {e}")
		else:
			# Anzeigen einer Nachricht, wenn die Spalte nicht gefunden wird
			messagebox.showinfo("Information", "Spalte nicht gefunden")  
  
	def reset_datetime_index(self):
		self.main_app.df.reset_index(inplace=True, drop=True)
		self.refresh_treeview()
		self.update_datetime_combobox()
	   
		
	def delete_columns(self):
		selected_columns = [col for col, var in self.column_vars.items() if var.get()]
		self.main_app.df.drop(selected_columns, axis=1, inplace=True)
		self.refresh_treeview()
		self.update_column_select_menu()
		self.update_datetime_combobox()

	def update_column_select_menu(self):
		self.delete_columns_menu.delete(0, tk.END)
		self.basic_arithmetical_operations_menu.delete(0, tk.END)
		self.column_vars = {}
		self.selected_columns_order = []
		for col in self.main_app.df.columns:
			boolean_var = tk.BooleanVar()
			self.column_vars[col] = boolean_var
			self.delete_columns_menu.add_checkbutton(label=col, variable=boolean_var)
			self.basic_arithmetical_operations_menu.add_checkbutton(label=col, variable=boolean_var, command=lambda col=col: self.on_checkbutton_toggle(col))
   
	def update_datetime_combobox(self):
		self.datetime_combobox['values'] = list(self.main_app.df.columns)
	  
  
	def refresh_treeview(self):
		# Löschen aller Daten im Treeview
		for row in self.data_treeview.get_children():
			self.data_treeview.delete(row)
	
		# Löschen aller vorhandenen Spalten im Treeview
		for col in self.data_treeview["columns"]:
			self.data_treeview.heading(col, text="")
			self.data_treeview.column(col, width=0, minwidth=0, stretch=False)
	
		# Aktualisieren der Spalten im Treeview basierend auf dem DataFrame
		self.treeview_columns = ["Index"] + list(self.main_app.df.columns)
		self.data_treeview["columns"] = list(self.treeview_columns)
		for col in self.treeview_columns:
			self.data_treeview.heading(col, text=col)
			self.data_treeview.column(col, anchor=tk.CENTER, width=100, stretch=False)
		
		# DataFrame-Daten hinzufügen
		for index, row in self.main_app.df.iterrows():
			row_data = [index] + list(row)
			self.data_treeview.insert("", tk.END, values=row_data)
		
		self.main_app.update_column_checklist()


	def on_close(self):
		if self.fig:
			plt.close(self.fig)
		self.window.destroy()

	def display_plot(self, fig):
		if self.canvas:
			self.canvas.get_tk_widget().destroy()

		self.fig = fig
		self.canvas = FigureCanvasTkAgg(fig, master=self.window)
		self.canvas.draw()
		self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')
		self.adjust_window_size()

	def adjust_window_size(self):
		additional_height = 50  # Zusätzliche Höhe für Achsenbeschriftungen und Buttons
		width = self.fig.get_figwidth() * self.fig.dpi
		height = self.fig.get_figheight() * self.fig.dpi + additional_height
		self.window.geometry(f"{int(width)}x{int(height)}")
	
	def refresh_plot(self, new_fig):
		# Close the old figure
		if self.fig:
			plt.close(self.fig)

		self.display_plot(new_fig)
	
	def set_refresh(self):
		if self in self.main_app.open_windows:
			self.main_app.open_windows.remove(self)
			self.main_app.open_windows.append(self)
			print("Refresh set")
		
	def save_plot(self):
		plot_title = self.fig._suptitle.get_text() if self.fig._suptitle else "MyPlot"
		filepath = filedialog.asksaveasfilename(
			defaultextension='',
			filetypes=[("PNG files", "*.png"), ("All Files", "*.*")],
			title="Save plot",
			initialfile= plot_title
		)
		if filepath:
			self.fig.savefig(filepath)
