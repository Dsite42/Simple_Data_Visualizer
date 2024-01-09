import tkinter as tk
import platform
from DataAnalysisApp import DataAnalysisApp
from cefpython3 import cefpython as cef


def main():
	operating_system = check_os()

	app = DataAnalysisApp(operating_system)
	app.run()
	

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
