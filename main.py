import tkinter as tk
from gui_components import DataAnalysisApp

def main():
    root = tk.Tk()
    app = DataAnalysisApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
