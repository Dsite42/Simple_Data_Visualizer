import tkinter as tk
import platform
from gui_components import DataAnalysisApp


def main():
	operating_system= check_os()
	print("OS: ", operating_system)
	tk_root = tk.Tk()
	app = DataAnalysisApp(tk_root, operating_system)
	tk_root.mainloop()

def check_os():
	os_name = platform.system()
	if os_name == 'Windows':
		return "Windows"
	elif os_name == 'Linux':
		return "Linux"
	else:
		return "Anderes Betriebssystem"

if __name__ == "__main__":
	main()
	