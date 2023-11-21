import tkinter as tk
from tkinter import messagebox
from BaseAnalysis import BaseAnalysis

class ManualPlotAnalysis(BaseAnalysis):
	def __init__(self, main_app):
		super().__init__()
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Manual Plot")
		self.scatter_last_window = None
		self.scatter_last_canvas = None

		#plot_args
		self.hue = tk.StringVar()
		self.size = tk.StringVar()
		self.style = tk.StringVar()

		self.code_entry_text = (
			"#Schreiben Sie hier Ihren Code. \n"
			"#Stellen Sie sicher, dass das resultierende Figure-Objekt in einer Variablen namens 'fig' gespeichert wird.\n"
			"#Zum Beispiel:\n"
			"#import seaborn as sns\n"
			"#sns.set(style='darkgrid')\n"
			"#g=sns.jointplot(x=df['Age'],y=df['BMI'],data=df,kind='kde')\n"
			"#fig = g.fig\n"
		) 
 
	def init_ui(self, parent_frame):
		# Zuvor erstellte Widgets im parent_frame entfernen
		for widget in parent_frame.winfo_children():
			widget.destroy()
   
		# Frame für den Button
		button_frame = tk.Frame(parent_frame)
		button_frame.pack(padx=5, pady=5, anchor='w')

		# Button zum Anzeigen des Scatter Plots
		show_plot_button = tk.Button(button_frame, text="Show Plot", command=lambda: self.execute_and_show_plot(False))
		show_plot_button.grid(row=0, column=0, padx=5, sticky='w')
  
		# Button zum Erneuern des Scatter Plots
		show_plot_button = tk.Button(button_frame, text="Refresh Plot", command=lambda: self.execute_and_show_plot(True))
		show_plot_button.grid(row=0, column=0, padx=110, sticky='w')



		self.code_entry = tk.Text(button_frame, height=10)
		self.code_entry.grid(row=1, column=0, padx=5, pady=5, sticky='w')
		self.code_entry.insert(tk.END, self.code_entry_text)

	def execute_and_show_plot(self, refresh_plot):
		user_env = {"df": self.main_app.df}  # Hier ist das DataFrame, das Sie dem Benutzer zur Verfügung stellen
		user_code = self.code_entry.get("1.0", tk.END)
		exec(user_code, user_env)
  
		if "fig" in user_env:
			fig = user_env["fig"]
			if refresh_plot:
				self.scatter_last_canvas = self.display_refresh_plot(fig, self.scatter_last_canvas)
			else:
				self.scatter_last_window, self.scatter_last_canvas = self.display_plot(fig, self.scatter_last_window, self.scatter_last_canvas)
		else:
			# Fehlerbehandlung, falls kein Figure-Objekt vorhanden ist
			messagebox.showinfo("Error", "The code did not produce a 'fig' variable.")
			print("Error: The code did not produce a 'fig' variable.")  

	def save_code_text(self):
		self.code_entry_text = self.code_entry.get("1.0", tk.END)