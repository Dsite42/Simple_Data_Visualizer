import tkinter as tk

class ConsoleOutput():
	def __init__(self, main_app):
		self.main_app = main_app
		self.plot_title = tk.StringVar(value = "Manual Plot")
		self.console_output_text = ("# Console output:\n")
		self.init_ui()
  
	def write(self, message):
		self.console_output.insert(tk.END, message)
		self.console_output.see(tk.END)
  
	def flush(self):
		self.console_output.delete("1.0", tk.END)

	def init_ui(self):
		# Frame for Buttons and console output
		console_frame = tk.Frame(self.main_app.console_output_tab_frame)
		console_frame.pack(padx=5, pady=5, anchor='w')
  
		clear_console_output_button = tk.Button(console_frame, text="Clear console output", command=lambda: self.flush())
		clear_console_output_button.grid(row=0, column=0, padx=5, sticky='w')

		self.console_output = tk.Text(console_frame, height=20)
		self.console_output.grid(row=1, column=0, padx=5, pady=5, sticky='w')
		self.console_output.insert(tk.END, self.console_output_text)
