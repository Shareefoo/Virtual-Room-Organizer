import os
import time
import shutil
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, StringVar, Toplevel, Frame
from tkinter import ttk

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

        ttk.Label(options_frame, text="Documents Directory:").grid(column=0, row=1, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["documents"], width=50).grid(column=1, row=1, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("documents")).grid(column=2, row=1, sticky="W", padx=5, pady=5)

        ttk.Label(options_frame, text="Videos Directory:").grid(column=0, row=2, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["videos"], width=50).grid(column=1, row=2, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("videos")).grid(column=2, row=2, sticky="W", padx=5, pady=5)

        ttk.Label(options_frame, text="Others Directory:").grid(column=0, row=3, sticky="W", padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.target_dirs["others"], width=50).grid(column=1, row=3, sticky="W", padx=5, pady=5)
        ttk.Button(options_frame, text="Browse", command=lambda: self.browse_target_directory("others")).grid(column=2, row=3, sticky="W", padx=5, pady=5)

        ttk.Button(options_frame, text="Save", command=options_window.destroy).grid(column=0, row=4, columnspan=3, pady=10)

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

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.update_status("Not monitoring")

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")

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
    root = Tk()
    root.style = ttk.Style()
    root.style.theme_use('clam')  # You can try other themes such as 'default', 'classic', 'clam', 'alt', 'vista', 'xpnative'

    file_organizer = FileOrganizer(root)
    root.mainloop()