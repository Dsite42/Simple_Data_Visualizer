import tkinter as tk
import tkinter.ttk as ttk
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
        self.window.maxsize(800, 600)

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
        self.data_treeview = ttk.Treeview(self.treeview_frame, columns=list(self.main_app.df.columns), show='headings')
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
        for col in self.main_app.df.columns:
            self.data_treeview.heading(col, text=col)
            self.data_treeview.column(col, anchor=tk.CENTER, width=100, stretch=False)

        # DataFrame-Daten hinzufügen
        for index, row in self.main_app.df.iterrows():
            self.data_treeview.insert("", tk.END, values=list(row))


		# Frame for data maipulation
        self.data_manipulation_frame = tk.Frame(self.window)
        self.data_manipulation_frame.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        
        # Dropdown-Menü für die Auswahl von Spalten
        self.delete_columns_menubutton = tk.Menubutton(self.data_manipulation_frame, text="Select columns", relief=tk.RAISED)
        self.delete_columns_menubutton.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.column_menu = tk.Menu(self.delete_columns_menubutton, tearoff=False)
        self.delete_columns_menubutton['menu'] = self.column_menu

        self.column_vars = {}
        for col in self.main_app.df.columns:
            self.column_vars[col] = tk.BooleanVar()
            self.column_menu.add_checkbutton(label=col, variable=self.column_vars[col])

        # Schaltfläche zum Löschen ausgewählter Spalten
        self.delete_columns_button = tk.Button(self.data_manipulation_frame, text="Delete columns", command=self.delete_columns)
        self.delete_columns_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        
    def delete_columns(self):
        selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        self.main_app.df.drop(selected_columns, axis=1, inplace=True)
        self.refresh_treeview()
        self.update_column_select_menu()

    def update_column_select_menu(self):
        self.column_menu.delete(0, tk.END)
        for col in self.main_app.df.columns:
            self.column_vars[col] = tk.BooleanVar()
            self.column_menu.add_checkbutton(label=col, variable=self.column_vars[col])
  
    def refresh_treeview(self):
        # Löschen aller Daten im Treeview
        for row in self.data_treeview.get_children():
            self.data_treeview.delete(row)
    
        # Löschen aller vorhandenen Spalten im Treeview
        for col in self.data_treeview["columns"]:
            self.data_treeview.heading(col, text="")
            self.data_treeview.column(col, width=0, minwidth=0, stretch=False)
    
        # Aktualisieren der Spalten im Treeview basierend auf dem DataFrame
        self.data_treeview["columns"] = list(self.main_app.df.columns)
        for col in self.main_app.df.columns:
            self.data_treeview.heading(col, text=col)
            self.data_treeview.column(col, anchor=tk.CENTER, width=100, stretch=False)
        
        # DataFrame-Daten hinzufügen
        for index, row in self.main_app.df.iterrows():
            self.data_treeview.insert("", tk.END, values=list(row))

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
