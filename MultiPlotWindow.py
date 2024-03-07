import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import filedialog

class MultiPlotWindow:
    def __init__(self, main_app, plot_title=""):
        self.main_app = main_app
        self.plot_title = plot_title
        self.figures = None
        self.canvas = None
        self.canvas_frame = None
        self.window = None
        self.current_width = None
        self.current_height = None
        self.last_width = None
        self.last_height = None
         
        self.create_window()
        # Verzögerter Aufruf zur Initialisierung der letzten Größenwerte
        self.window.after(200, self.initialize_last_size)
        
    def initialize_last_size(self):
        """Initialisiere die letzten Größenwerte basierend auf dem aktuellen Fenster."""
        self.last_width = self.window.winfo_width()
        self.last_height = self.window.winfo_height()

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
  
        copy_button = tk.Button(self.window, text="Copy Plot", command=lambda: self.copy_plot(self.figures))
        copy_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        set_refresh_button = tk.Button(self.window, text="Set Refresh", command=lambda: self.set_refresh())
        set_refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        self.fig_autoscale = tk.BooleanVar(value=True)
        set_fig_auto_scale_checkbox = tk.Checkbutton(self.window, text="Auto Scale", variable=self.fig_autoscale)
        set_fig_auto_scale_checkbox.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        

    def on_close(self):
        for fig in self.figures:
            plt.close(fig)
        self.window.destroy()



    def display_multiple_plots(self, figures, canvas_rows, canvas_columns):        
        self.figures = figures
        # Convert plot size from inches to pixels for tkinter canvas 
        self.plot_width = self.figures[0].get_figwidth() * self.figures[0].dpi
        self.plot_height = self.figures[0].get_figheight() * self.figures[0].dpi
        self.max_window_width = self.window.winfo_screenwidth()*0.99 #1600
        self.max_window_height = self.window.winfo_screenheight()*0.92 #1200

        # Erstelle einen neuen Frame für die Canvas-Widgets
        self.canvas_frame = tk.Frame(self.window)
        self.canvas_frame.grid(row=1, column=0, columnspan=4, sticky='nsew')
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Scrollable canvas
        self.scroll_canvas = tk.Canvas(self.canvas_frame, width=int(min(self.plot_width, self.max_window_width)), height=int(min(self.plot_height, self.max_window_height)))
        self.scroll_canvas.grid(row=0, column=0, sticky='nsew')

        v_scroll = tk.Scrollbar(self.canvas_frame, orient='vertical', command=self.scroll_canvas.yview)
        v_scroll.grid(row=0, column=1, sticky='ns')
        self.scroll_canvas.configure(yscrollcommand=v_scroll.set)

        # Horizontaler Scrollbalken
        h_scroll = tk.Scrollbar(self.canvas_frame, orient='horizontal', command=self.scroll_canvas.xview)
        h_scroll.grid(row=1, column=0, sticky='ew')
        self.scroll_canvas.configure(xscrollcommand=h_scroll.set)


        # Frame innerhalb des scrollable canvas
        self.plot_frame = tk.Frame(self.scroll_canvas)
        self.scroll_canvas.create_window((0, 0), window=self.plot_frame, anchor='nw')

        # Berechne die Anzahl der benötigten Reihen und Spalten
        total_plots = len(figures)
        self.rows = canvas_rows
        self.columns = canvas_columns

        # Erstelle für jedes Figure-Objekt ein Canvas-Widget und ordne es im Raster an
        for i, fig in enumerate(figures):
            row = i // self.columns
            column = i % self.columns
            fig_canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            fig_canvas.draw()
            plot_widget = fig_canvas.get_tk_widget()
            # Verwende grid statt pack für die Anordnung
            plot_widget.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)

        # Stelle sicher, dass der plot_frame genug Platz für alle widgets bietet
        for i in range(self.rows):
            self.plot_frame.grid_rowconfigure(i, weight=1)
        for i in range(self.columns):
            self.plot_frame.grid_columnconfigure(i, weight=1)

        # Aktualisiere die Scrollregion auf die Größe des inneren Frames
        if self.current_width and self.current_height:
            self.scroll_canvas.config(width=self.current_width-20, height=self.current_height-60) # 20 is the width of the scrollbar

        self.plot_frame.update_idletasks()
        self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox("all"))


    def on_plot_resize(self, event=None):
        self.plot_canvas.configure(scrollregion=self.plot_canvas.bbox("all"))


    def adjust_window_size(self):
        self.additional_width = 20  # Additional width for axis labels and buttons
        self.additional_height = 60  # Additional height for axis labels and buttons
        self.window.geometry(f"{int(min(self.plot_width, self.max_window_width)+self.additional_width)}x{int(min(self.plot_height, self.max_window_height) + self.additional_height)}")      

    
    def refresh_plot(self, new_figures, canvas_rows, canvas_columns):
        # Close the old figures
        for fig in self.figures:
            plt.close(fig)

        self.display_multiple_plots(new_figures, canvas_rows, canvas_columns)
    
    def set_refresh(self):
        if self in self.main_app.open_windows:
            self.main_app.open_windows.remove(self)
            self.main_app.open_windows.append(self)
            print("Refresh set")
        
    def save_plot(self):
        plot_title = self.figures[0]._suptitle.get_text() if self.figures[0]._suptitle else "MyPlot"
        filepath = filedialog.asksaveasfilename(defaultextension='', filetypes=[("PNG files", "*.png"), ("All Files", "*.*")],
            title="Save plot", initialfile=plot_title)
        if filepath:
            import io
            from PIL import Image
            # Temporary storage for buffers to keep them open
            buffers = []

            rendered_images = []
            for fig in self.figures:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                img = Image.open(buf)
                rendered_images.append(img)
                # Add the buffer to the list instead of closing it
                buffers.append(buf)
                
            # Calculate the total grid size based on the max width and height of the images in each row/column
            max_width_per_column = max(img.width for img in rendered_images)  # Assuming uniform width for simplicity
            max_height_per_row = max(img.height for img in rendered_images)  # Assuming uniform height for simplicity
            total_width = max_width_per_column * self.columns
            total_height = max_height_per_row * self.rows

            # Create a new image with the appropriate size
            combined_img = Image.new('RGB', (total_width, total_height), 'white')  # Background color is white

            # Initialize coordinates for pasting images
            current_x, current_y = 0, 0
            for i, img in enumerate(rendered_images):
                combined_img.paste(img, (current_x, current_y))
                current_x += max_width_per_column
                # Check if we've reached the end of a row
                if (i + 1) % self.columns == 0:
                    current_x = 0
                    current_y += max_height_per_row

            # After pasting all images, save the combined image
            combined_img.save(filepath)
            
            for buf in buffers:
                buf.close()
        
        
    def copy_plot(self, figures):
        if self.main_app.operating_system == "Windows":
            self.copyToClipboardWindows()
        elif self.main_app.operating_system == "Linux":
            self.copyToClippboardLinux()
        elif self.main_app.operating_system == "Darwin":
            self.copyToClipboardMac()
            

    def copyToClipboardWindows(self):
        import io
        from PIL import Image
        import win32clipboard
        import matplotlib.pyplot as plt

        buffers = []
        rendered_images = []
        for fig in self.figures:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img = Image.open(buf)
            rendered_images.append(img)
            buffers.append(buf)

        # Calculate the total grid size based on the max width and height of the images in each row/column
        max_width_per_column = max(img.width for img in rendered_images)
        max_height_per_row = max(img.height for img in rendered_images)
        total_width = max_width_per_column * self.columns
        total_height = max_height_per_row * self.rows
        # Create a new image with the appropriate size
        combined_img = Image.new('RGB', (total_width, total_height), 'white')
        # Initialize coordinates for pasting images
        current_x, current_y = 0, 0
        for i, img in enumerate(rendered_images):
            combined_img.paste(img, (current_x, current_y))
            current_x += max_width_per_column
            # Check if we've reached the end of a row
            if (i + 1) % self.columns == 0:
                current_x = 0
                current_y += max_height_per_row

        # Copy the combined image to the clipboard
        output = io.BytesIO()
        combined_img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # BMP files have a 14-byte header that needs to be removed
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        for buf in buffers:
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


    def on_window_configure(self, event):
        self.current_width = self.window.winfo_width()
        self.current_height = self.window.winfo_height()
        # Check if the window size has changed
        if self.last_width is not None and self.last_height is not None:
            if self.current_width != self.last_width or self.current_height != self.last_height:
                self.last_width = self.current_width
                self.last_height = self.current_height
                self.on_window_resize(event)
            
    def on_window_resize(self, event):
        if self.fig_autoscale.get() == True :
            self.scroll_canvas.config(width=self.current_width-20, height=self.current_height-60) # 20 is the width of the scrollbar
            self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox("all"))
