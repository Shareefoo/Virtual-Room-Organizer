import os
import time
import shutil
import threading
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, StringVar, Toplevel, Frame, scrolledtext
from tkinter import ttk, Menu
from ttkthemes import ThemedTk  # pip install ttkthemes

class FileOrganizer:
    def __init__(self, master):
        self.master = master
        master.title("File Organizer")

        # Define the directory to be monitored
        self.downloads_dir = StringVar(value=os.path.expanduser("~/Downloads"))

        # Define the target directories
        self.target_dirs = {
            "images": StringVar(value=os.path.expanduser("~/Downloads/Images")),
            "music": StringVar(value=os.path.expanduser("~/Downloads/Music")),
            "videos": StringVar(value=os.path.expanduser("~/Downloads/Videos")),
            "programs": StringVar(value=os.path.expanduser("~/Downloads/Programs")),
            "compressed": StringVar(value=os.path.expanduser("~/Downloads/Compressed")),
            "documents": StringVar(value=os.path.expanduser("~/Downloads/Documents")),
            "others": StringVar(value=os.path.expanduser("~/Downloads/Others"))
        }

        # load saved settings
        self.load_settings()

        main_frame = ttk.Frame(master, padding="10 10 10 10")
        main_frame.pack(fill="both", expand=True)

        self.label = ttk.Label(main_frame, text="Downloads Directory:")
        self.label.grid(column=0, row=0, sticky="W", padx=5, pady=5)

        self.downloads_entry = ttk.Entry(main_frame, textvariable=self.downloads_dir, width=50)
        self.downloads_entry.grid(column=1, row=0, sticky="W", padx=5, pady=5)

        self.browse_button = ttk.Button(main_frame, text="Browse", command=self.browse_directory)
        self.browse_button.grid(column=2, row=0, sticky="W", padx=5, pady=5)

        self.options_button = ttk.Button(main_frame, text="Options", command=self.open_options)
        self.options_button.grid(column=0, row=1, sticky="W", padx=5, pady=5)

        self.start_button = ttk.Button(main_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.grid(column=1, row=1, sticky="W", padx=5, pady=5)

        self.stop_button = ttk.Button(main_frame, text="Stop Monitoring", command=self.stop_monitoring, state='disabled')
        self.stop_button.grid(column=2, row=1, sticky="W", padx=5, pady=5)

        self.status_label = ttk.Label(main_frame, text="Status: Not monitoring")
        self.status_label.grid(column=0, row=2, columnspan=3, sticky="W", padx=5, pady=5)

        self.status_text = scrolledtext.ScrolledText(main_frame, wrap='word', height=10, state='disabled')
        self.status_text.grid(column=0, row=3, columnspan=3, sticky="WE", padx=5, pady=5)

        self.progress = ttk.Progressbar(main_frame, orient='horizontal', mode='indeterminate')
        self.progress.grid(column=0, row=4, columnspan=3, sticky="WE", padx=5, pady=5)

        self.dark_mode = False

        self.menu_bar = Menu(master)
        self.theme_menu = Menu(self.menu_bar, tearoff=0)
        self.theme_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.menu_bar.add_cascade(label="Theme", menu=self.theme_menu)
        master.config(menu=self.menu_bar)

        self.observer = None

    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.downloads_dir.get())
        if directory:
            self.downloads_dir.set(directory)

    def open_options(self):
        options_window = Toplevel(self.master)
        options_window.title("Options")

        options_frame = ttk.Frame(options_window, padding="10 10 10 10")
        options_frame.pack(fill="both", expand=True)

        ttk.Label(options_frame, text="Images Directory:").grid(column=0, row=0, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["images"], width=50).grid(column=1, row=0, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("images")).grid(column=2, row=0, sticky="W", padx=5, pady=5)

        ttk.Label(options_frame, text="Music Directory:").grid(column=0, row=1, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["music"], width=50).grid(column=1, row=1, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("music")).grid(column=2, row=1, sticky="W", padx=5, pady=5)

        ttk.Label(options_frame, text="Videos Directory:").grid(column=0, row=2, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["videos"], width=50).grid(column=1, row=2, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("videos")).grid(column=2, row=2, sticky="W", padx=5, pady=5)

        ttk.Label(options_frame, text="Programs Directory:").grid(column=0, row=3, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["programs"], width=50).grid(column=1, row=3, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("programs")).grid(column=2, row=3, sticky="W", padx=5, pady=5)

        ttk.Label(options_frame, text="Compressed Directory:").grid(column=0, row=4, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["compressed"], width=50).grid(column=1, row=4, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("compressed")).grid(column=2, row=4, sticky="W", padx=5, pady=5)

        ttk.Label(options_frame, text="Documents Directory:").grid(column=0, row=5, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["documents"], width=50).grid(column=1, row=5, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("documents")).grid(column=2, row=5, sticky="W", padx=5, pady=5)

        ttk.Label(options_frame, text="Others Directory:").grid(column=0, row=6, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["others"], width=50).grid(column=1, row=6, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("others")).grid(column=2, row=6, sticky="W", padx=5, pady=5)

        ttk.Button(options_frame, text="Save", command=self.save_settings).grid(column=0, row=7, columnspan=3, pady=10)


    def browse_target_directory(self, key):
        directory = filedialog.askdirectory(initialdir=self.target_dirs[key].get())
        if directory:
            self.target_dirs[key].set(directory)

    def start_monitoring(self):
        self.downloads_dir_path = self.downloads_dir.get()
        if not os.path.exists(self.downloads_dir_path):
            messagebox.showerror("Error", "The specified directory does not exist.")
            return

        self.observer = Observer()
        event_handler = DownloadEventHandler(self.update_status, self.target_dirs)
        self.observer.schedule(event_handler, self.downloads_dir_path, recursive=False)

        self.observer_thread = threading.Thread(target=self.observer.start)
        self.observer_thread.start()

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.update_status(f"Monitoring {self.downloads_dir_path}")
        self.progress.start()

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.update_status("Not monitoring")
        self.progress.stop()

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")
        self.status_text.config(state='normal')
        self.status_text.insert('end', f"{message}\n")
        self.status_text.config(state='disabled')
        self.status_text.yview('end')

    def save_settings(self):
        settings = {
            "downloads_dir": self.downloads_dir.get(),
            "target_dirs": {key: var.get() for key, var in self.target_dirs.items()}
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.downloads_dir.set(settings.get("downloads_dir", os.path.expanduser("~/Downloads")))
                for key, value in settings.get("target_dirs", {}).items():
                    self.target_dirs[key].set(value)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.master.style.theme_use('equilux')  # A dark theme available via ttkthemes
            self.master.configure(bg='#333333')
            self.status_text.configure(bg='#333333', fg='white', insertbackground='white')
        else:
            self.master.style.theme_use('clam')
            self.master.configure(bg='SystemButtonFace')
            self.status_text.configure(bg='white', fg='black', insertbackground='black')

class DownloadEventHandler(FileSystemEventHandler):
    def __init__(self, status_callback, target_dirs):
        super().__init__()
        self.status_callback = status_callback
        self.TARGET_DIRS = {key: var.get() for key, var in target_dirs.items()}
        for path in self.TARGET_DIRS.values():
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def get_file_type(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
            return "images"
        elif ext in ['.mp3']:
            return "music"
        elif ext in ['.mp4', '.mov', '.avi']:
            return "videos"
        elif ext in ['.exe', '.msi']:
            return "programs"
        elif ext in ['.rar', '.zip']:
            return "compressed"
        elif ext in ['.txt', '.pdf', '.docx', '.pptx', '.xlsx']:
            return "documents"
        else:
            return "others"

    def move_file_with_retry(self, src_path, dest_path, retries=5, delay=1):
        for i in range(retries):
            try:
                shutil.move(src_path, dest_path)
                self.status_callback(f"Moved: {os.path.basename(src_path)} to {dest_path}")
                return True
            except PermissionError:
                self.status_callback(f"PermissionError: Retrying in {delay} seconds... ({i+1}/{retries})")
                time.sleep(delay)
        self.status_callback(f"Failed to move: {os.path.basename(src_path)}")
        return False

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_type = self.get_file_type(file_path)
            target_path = os.path.join(self.TARGET_DIRS[file_type], os.path.basename(file_path))
            self.move_file_with_retry(file_path, target_path)

if __name__ == "__main__":
    root = ThemedTk(theme="clam")  # Use ThemedTk for better theming options
    root.style = ttk.Style()
    root.style.theme_use('clam')  # Initial theme
    file_organizer = FileOrganizer(root)
    root.mainloop()