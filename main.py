import tkinter as tk
import platform
from DataAnalysisApp import DataAnalysisApp
from cefpython3 import cefpython as cef


def main():
	operating_system = check_os()
	cefpython = cef.Initialize()
	tk_root = tk.Tk()

	## set the scaling
	#scale_factor = 1.0
	#tk_root.tk.call('tk', 'scaling', scale_factor)
	app = DataAnalysisApp(tk_root, operating_system)
	tk_root.mainloop()
	cef.Shutdown()
	

def check_os():
	os_name = platform.system()
	if os_name == 'Windows':
		return "Windows"
	elif os_name == 'Linux':
		return "Linux"
	elif os_name == 'Darwin':
		return "Darwin"
	else:
		return "Different operating system"


if __name__ == "__main__":
	main()
