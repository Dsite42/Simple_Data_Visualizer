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
        self.window.bind("<Configure>", self.on_window_configure)
        self.resize_timer = None
                
        # Bind the close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Add buttons and other UI elements here
        # Set column with equal
        for i in range(4):
            self.window.grid_columnconfigure(i, weight=1, uniform="button")

        save_button = tk.Button(self.window, text="Save Plot", command=lambda: self.save_plot())
        save_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')
  
        copy_button = tk.Button(self.window, text="Copy Plot", command=lambda: self.copy_plot(self.fig))
        copy_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        set_refresh_button = tk.Button(self.window, text="Set Refresh", command=lambda: self.set_refresh())
        set_refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        self.fig_autoscale = tk.BooleanVar(value=True)
        set_fig_auto_scale_checkbox = tk.Checkbutton(self.window, text="Auto Scale", variable=self.fig_autoscale)
        set_fig_auto_scale_checkbox.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        

    def on_close(self):
        if self.fig:
            plt.close(self.fig)
        self.window.destroy()

    def display_plot(self, fig):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.fig = fig
        
        # Convert plot size from inches to pixels for tkinter canvas 
        self.plot_width = self.fig.get_figwidth() * self.fig.dpi
        self.plot_height = self.fig.get_figheight() * self.fig.dpi
        self.max_window_width = self.window.winfo_screenwidth()*0.99 #1600
        self.max_window_height = self.window.winfo_screenheight()*0.92 #1200

        # Create Canvas and Scrollbars
        self.canvas_frame = tk.Frame(self.window)
        self.canvas_frame.grid(row=1, column=0, columnspan=4, sticky='nsew')
         # Configure window to be able to resize
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.plot_canvas = tk.Canvas(self.canvas_frame, width=min(self.plot_width, self.max_window_width), height=min(self.plot_height, self.max_window_height))
        self.plot_canvas.grid(row=0, column=0, sticky='nsew')

        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient='vertical', command=self.plot_canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.h_scroll = tk.Scrollbar(self.window, orient='horizontal', command=self.plot_canvas.xview)
        self.h_scroll.grid(row=2, column=0, columnspan=4, sticky='ew')

        self.plot_canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        # Show plot in canvas
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_canvas)
        self.canvas.draw()
        plot_widget = self.canvas.get_tk_widget()
        self.plot_canvas.create_window((0, 0), window=plot_widget, anchor='nw')

        plot_widget.bind("<Configure>", self.on_plot_resize)
        self.adjust_window_size()


    def on_plot_resize(self, event=None):
        self.plot_canvas.configure(scrollregion=self.plot_canvas.bbox("all"))


    def adjust_window_size(self):
        self.additional_width = 20  # Additional width for axis labels and buttons
        self.additional_height = 60  # Additional height for axis labels and buttons
        self.window.geometry(f"{int(min(self.plot_width, self.max_window_width)+self.additional_width)}x{int(min(self.plot_height, self.max_window_height) + self.additional_height)}")      

    
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
            self.copyToClipboardWindows(fig)
        elif self.main_app.operating_system == "Linux":
            self.copyToClippboardLinux(fig)
        
            

        elif self.main_app.operating_system == "Darwin":
            self.copyToClipboardMac(fig)
            

    def copyToClipboardWindows(self, fig):
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


    def copyToClippboardLinux(self, fig):
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


    def copyToClipboardMac(self, fig):
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


    def on_window_configure(self, event=None):
        if self.resize_timer is not None:
            self.window.after_cancel(self.resize_timer)
        self.resize_timer = self.window.after(500, self.on_window_resize)

    def on_window_resize(self, event=None):
        # Erhalten der aktuellen Fenstergröße
        current_width = self.window.winfo_width()
        current_height = self.window.winfo_height()
        
        if self.fig_autoscale.get() == True :
            if (abs(current_width - self.plot_width) > self.additional_width or abs(current_height - self.plot_height) > self.additional_height):
                self.resize_fig(current_width, current_height)
                self.display_plot(self.fig)

        else:
            self.plot_canvas.config(width=current_width-20, height=current_height-20) # 20 is the width of the scrollbar
                        
    def resize_fig(self, width, height):
        new_fig_width = width / self.fig.dpi
        new_fig_height = height / self.fig.dpi
        self.fig.set_size_inches(new_fig_width, new_fig_height, forward=True)
