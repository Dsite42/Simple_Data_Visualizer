import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data_analysis import read_csv, create_scatter_plot

class DataAnalysisApp:
    def __init__(self, root):
        self.root = root
        root.title("Einfaches Datenanalyse-Programm")

        self.columns_to_analyze = {}
        self.df = None

        open_button = tk.Button(root, text="CSV-Datei öffnen", command=self.open_file)
        open_button.pack()

        analyze_button = tk.Button(root, text="Analysieren", command=self.analyze)
        analyze_button.pack()

        scatter_button = tk.Button(root, text="Scatter", command=self.show_scatter_plot)
        scatter_button.pack()

        self.columns_frame = tk.Frame(root)
        self.columns_frame.pack()

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if messagebox.askokcancel("Schließen", "Wollen Sie das Programm wirklich beenden?"):
            self.root.destroy()
            self.root.quit()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.df, error = read_csv(file_path)
            if error:
                messagebox.showerror("Fehler beim Einlesen der Datei", error)
            else:
                self.update_column_checklist()

    def update_column_checklist(self):
        for widget in self.columns_frame.winfo_children():
            widget.destroy()

        for column in self.df.columns:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(self.columns_frame, text=column, variable=var)
            checkbox.pack(anchor='w')
            self.columns_to_analyze[column] = {"var": var, "text": column}

    def get_selected_columns(self):
        return [col_checkbox["text"] for col_checkbox in self.columns_to_analyze.values() if col_checkbox["var"].get()]

    def show_scatter_plot(self):
        selected_columns = self.get_selected_columns()
        fig = create_scatter_plot(self.df, selected_columns)
        if fig:
            new_window = tk.Toplevel(self.root)
            new_window.title("Streudiagramm")

            canvas = FigureCanvasTkAgg(fig, master=new_window)
            canvas.draw()
            canvas.get_tk_widget().pack()

    def analyze(self):
        selected_columns = self.get_selected_columns()
        print(f"Ausgewählte Spalten für die Analyse: {selected_columns}")
        # Hier können Sie Ihre Analysefunktionen hinzufügen
