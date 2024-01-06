import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import filedialog

class PlotWindow:
    def __init__(self, main_app, plot_title=""):
        self.main_app = main_app
        self.plot_title = plot_title
        self.fig = None
        self.canvas = None
        self.window = None
        self.create_window()

    def create_window(self):
        self.window = tk.Toplevel(self.main_app.tk_root)
        self.window.title(self.plot_title)

        # Bind the close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Add buttons and other UI elements here
        save_button = tk.Button(self.window, text="Save Plot", command=lambda: self.save_plot())
        save_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')
  
        copy_button = tk.Button(self.window, text="Copy Plot", command=lambda: self.copy_plot(self.fig))
        copy_button.grid(row=0, column=0, padx=100, pady=5, sticky='w')
        
        set_refresh_button = tk.Button(self.window, text="Set Refresh", command=lambda: self.set_refresh())
        set_refresh_button.grid(row=0, column=0, padx=200, pady=5, sticky='w')

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
        additional_height = 50  # Additional height for axis labels and buttons
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
        
        
    def copy_plot(self, fig):
        if self.main_app.operating_system == "Windows":
            import io
            from PIL import Image
            import win32clipboard

            plot_title = self.fig._suptitle.get_text() if self.fig._suptitle else "MyPlot"
            # Save plotly figure in a BytesIO buffer as PNG
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            # Copy the image from the buffer to the clipboard
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
            # Save plotly figure in a BytesIO buffer as PNG
            buf = io.BytesIO()
            self.fig.savefig(buf, format='png')
            buf.seek(0)

            # Pass the image to xclip to copy it to the clipboard
            process = subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'], stdin=subprocess.PIPE)
            process.communicate(input=buf.getvalue())

            buf.close()

        if self.main_app.operating_system == "Darwin":
            import io
            import os
            from PIL import Image
            import subprocess

            # Save plotly figure in a BytesIO buffer as PNG
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            img = Image.open(buf)

            # Save the image to a temporary file
            temp_path = "/tmp/temp_plot.png"
            img.save(temp_path, "PNG")

            # Copy the image to the clipboard using macOS commands
            subprocess.run(["osascript", "-e", f'set the clipboard to (read (POSIX file "{temp_path}") as JPEG picture)'])

            # Remove the temporary file
            os.remove(temp_path)
            buf.close()        
