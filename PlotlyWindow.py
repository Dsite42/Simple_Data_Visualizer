import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import filedialog

import base64
import plotly.express as px
from cefpython3 import cefpython as cef

class PlotlyWindow:
    def __init__(self, main_app, plot_title=""):
        self.main_app = main_app
        self.plot_title = plot_title

        self.create_window()

    def create_window(self):
        self.window = tk.Toplevel(self.main_app.tk_root)
        self.window.title(self.plot_title)
        self.window.geometry("800x600")

        # Bind the close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Add buttons and other UI elements here
        save_button = tk.Button(self.window, text="Save Plot", command=lambda: self.save_plot())
        save_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')
  
        copy_button = tk.Button(self.window, text="Copy Plot", command=lambda: self.copy_plot(self.fig))
        copy_button.grid(row=0, column=0, padx=100, pady=5, sticky='w')
        
        set_refresh_button = tk.Button(self.window, text="Set Refresh", command=lambda: self.set_refresh())
        set_refresh_button.grid(row=0, column=0, padx=200, pady=5, sticky='w')
        
        # Frame for cefpython browser
        self.frame_cefpython = tk.Frame(self.window)
        #self.frame_cefpython.pack(fill="both", expand=True)
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.frame_cefpython.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        self.frame_cefpython_id = self.frame_cefpython.winfo_id()
    

    def on_close(self):
        #if self.fig:
        #    plt.close(self.fig)
        self.window.destroy()
        self.browser.CloseBrowser(forceClose=True)

    def display_plot(self, fig):
        self.fig = fig
        self.adjust_window_size()
        print(self.frame_cefpython.winfo_width(), self.frame_cefpython.winfo_height())
        plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='my-plot-div')
        data_url = f"data:text/html;charset=utf-8;base64,{base64.b64encode(plot_html.encode()).decode()}"
        if not hasattr(self, 'browser'):
            self.browser = cef.CreateBrowserSync(self.window_info, url=data_url) 
        else:
            self.browser.LoadUrl(data_url)


    def adjust_window_size(self):
        additional_height = 0  # Zusätzliche Höhe für Achsenbeschriftungen und Buttons
        width = self.fig.layout.width if self.fig.layout.width is not None else 800  # Standardbreite, falls nicht gesetzt
        height = self.fig.layout.height + additional_height if self.fig.layout.height is not None else 600 + additional_height  # Standardhöhe, falls nicht gesetzt
        self.window.geometry(f"{int(width)}x{int(height)}")
        self.window_info = cef.WindowInfo(self.frame_cefpython_id)
        self.window_info.SetAsChild(self.frame_cefpython_id, [0, 0, width, height])
        self.window.update_idletasks()
        

    def refresh_plot(self, new_fig):
        # Close the old figure
        #if self.fig:
        #    plt.close(self.fig)
        
        self.display_plot(new_fig)

               
    
    def set_refresh(self):
        if self in self.main_app.open_windows:
            self.main_app.open_windows.remove(self)
            self.main_app.open_windows.append(self)
            print("Refresh set")
        
    def save_plot(self):
        plot_title = self.plot_title if self.plot_title else "MyPlot"
        filepath = filedialog.asksaveasfilename(
            defaultextension='',
            filetypes=[("PNG files", "*.png"), ("All Files", "*.*")],
            title="Save plot",
            initialfile= plot_title
        )
        if filepath:
            self.fig.write_image(filepath)
        
        
    def copy_plot(self, fig):
        if self.main_app.operating_system == "Windows":
            import io
            from PIL import Image
            import win32clipboard
            import plotly.io as pio

            # Plotly-Figur in einen BytesIO-Buffer als PNG speichern
            buf = io.BytesIO()
            pio.write_image(self.fig, buf, format='png')
            buf.seek(0)

            # Das Bild aus dem Buffer in die Zwischenablage kopieren
            image = Image.open(buf)
            output = io.BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            buf.close()

        if self.main_app.operating_system == "Linux":
            import io
            import subprocess
            import plotly.io as pio

            # Plotly-Figur in einen BytesIO-Buffer als PNG speichern
            buf = io.BytesIO()
            pio.write_image(self.fig, buf, format='png')
            buf.seek(0)

            # Das Bild an xclip übergeben, um es in die Zwischenablage zu kopieren
            process = subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'], stdin=subprocess.PIPE)
            process.communicate(input=buf.getvalue())
            buf.close()

        if self.main_app.operating_system == "Darwin":
            import io
            import os
            from PIL import Image
            import subprocess
            import plotly.io as pio

            # Speichern des Plots in einem BytesIO-Buffer
            buf = io.BytesIO()
            pio.write_image(self.fig, buf, format='png')
            buf.seek(0)
            img = Image.open(buf)

            # Speichern des Bildes in einer temporären Datei
            temp_path = "/tmp/temp_plot.png"
            img.save(temp_path, "PNG")

            # Kopieren des Bildes in die Zwischenablage mit macOS-Befehlen
            subprocess.run(["osascript", "-e", f'set the clipboard to (read (POSIX file "{temp_path}") as JPEG picture)'])

            # Löschen der temporären Datei
            os.remove(temp_path)
            buf.close()