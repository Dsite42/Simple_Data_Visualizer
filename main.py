import tkinter as tk
from gui_components import DataAnalysisApp

def main():
	tk_root = tk.Tk()
	app = DataAnalysisApp(tk_root)
	tk_root.mainloop()

if __name__ == "__main__":
	main()
	