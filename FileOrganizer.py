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
        master.title("Room Organizer")

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
        self.create_widgets()
        self.file_movements = []  # Stack to store file movements for undo functionality
        self.observer = None
        self.dark_mode = False


    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10 10 10 10")
        main_frame.pack(fill="both", expand=True)

        self.create_label_entry_button(main_frame, "Room:", self.downloads_dir, self.select_room, 0)
        
        # self.label = ttk.Label(main_frame, text="Room:")
        # self.label.grid(column=0, row=0, sticky="W", padx=5, pady=5)

        # self.room_entry = ttk.Entry(main_frame, textvariable=self.downloads_dir, width=50)
        # self.room_entry.grid(column=1, row=0, sticky="W", padx=5, pady=5)

        # self.browse_button = ttk.Button(main_frame, text="Select Room", command=self.select_room)
        # self.browse_button.grid(column=2, row=0, sticky="W", padx=5, pady=5)

        self.status_label = ttk.Label(main_frame, text="Status: Not monitoring")
        self.status_label.grid(column=0, row=1, columnspan=3, sticky="W", padx=5, pady=5)

        self.status_text = scrolledtext.ScrolledText(main_frame, wrap='word', height=10, state='disabled')
        self.status_text.grid(column=0, row=2, columnspan=3, sticky="WE", padx=5, pady=5)

        self.progress = ttk.Progressbar(main_frame, orient='horizontal', mode='indeterminate')
        self.progress.grid(column=0, row=3, columnspan=3, sticky="WE", padx=5, pady=5)

        self.create_menu()


    def create_label_entry_button(self, parent, label_text, text_var, command, row):
        ttk.Label(parent, text=label_text).grid(column=0, row=row, sticky="W", padx=5, pady=5)
        ttk.Entry(parent, textvariable=text_var, width=50).grid(column=1, row=row, sticky="W", padx=5, pady=5)
        ttk.Button(parent, text="Browse", command=command).grid(column=2, row=row, sticky="W", padx=5, pady=5)


    def create_menu(self):
        self.menu_bar = Menu(self.master)

        # General Menu
        self.general_menu = Menu(self.menu_bar, tearoff=0)
        self.general_menu.add_command(label="Select Room", command=self.select_room)
        self.general_menu.add_command(label="Organize Now", command=self.organize_now)
        self.general_menu.add_command(label="Undo", command=self.undo)
        self.general_menu.add_command(label="Options", command=self.open_options)
        self.general_menu.add_separator()
        self.general_menu.add_command(label="Exit", command=root.destroy)
        self.menu_bar.add_cascade(label="General", menu=self.general_menu)

        # Monitoring Menu
        self.monitoring_menu = Menu(self.menu_bar, tearoff=0)
        self.monitoring_menu.add_command(label="Start Monitoring", command=self.start_monitoring)
        self.monitoring_menu.add_command(label="Stop Monitoring", command=self.stop_monitoring)
        self.menu_bar.add_cascade(label="Monitoring", menu=self.monitoring_menu)

        # View Menu
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Switch Theme", command=self.switch_theme)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        self.master.config(menu=self.menu_bar)


    # 
    def select_room(self):
        room = filedialog.askdirectory(initialdir=self.downloads_dir.get())
        if room:
            self.downloads_dir.set(room)

    #
    def open_options(self):
        options_window = Toplevel(self.master)
        options_window.title("Options")

        options_frame = ttk.Frame(options_window, padding="10 10 10 10")
        options_frame.pack(fill="both", expand=True)

        for key, text in [("images", "Images Directory:"), 
                          ("music", "Music Directory:"),                             
                          ("videos", "Videos Directory:"), 
                          ("programs", "Programs Directory"),
                          ("compressed", "Compressed Directory"),
                          ("documents", "Documents Directory:"), 
                          ("others", "Others Directory:")]:
            self.create_label_entry_button(options_frame, text, self.target_dirs[key], lambda k=key: self.browse_target_directory(k), list(self.target_dirs.keys()).index(key))

        ttk.Button(options_frame, text="Save", command=self.save_settings).grid(column=0, row=7, columnspan=3, pady=10)

    #
    def browse_target_directory(self, key):
        directory = filedialog.askdirectory(initialdir=self.target_dirs[key].get())
        if directory:
            self.target_dirs[key].set(directory)

    #
    def start_monitoring(self):
        self.downloads_dir_path = self.downloads_dir.get()
        if not os.path.exists(self.downloads_dir_path):
            messagebox.showerror("Error", "The specified directory does not exist.")
            return

        self.observer = Observer()
        event_handler = DownloadEventHandler(self.update_status, self.target_dirs, self.file_movements)
        self.observer.schedule(event_handler, self.downloads_dir_path, recursive=False)

        self.observer_thread = threading.Thread(target=self.observer.start)
        self.observer_thread.start()

        self.update_status(f"Monitoring {self.downloads_dir_path}")
        self.progress.start()

    #
    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        self.update_status("Not monitoring")
        self.progress.stop()

    #
    def organize_now(self):
        self.downloads_dir_path = self.downloads_dir.get()
        if not os.path.exists(self.downloads_dir_path):
            messagebox.showerror("Error", "The specified directory does not exist.")
            return

        self.update_status("Organizing files...")
        for filename in os.listdir(self.downloads_dir_path):
            file_path = os.path.join(self.downloads_dir_path, filename)
            if os.path.isfile(file_path):
                file_type = self.get_file_type(file_path)
                target_path = os.path.join(self.target_dirs[file_type].get(), filename)
                # Ensure the target directory exists
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                self.move_file_with_retry(file_path, target_path)
        self.update_status("Organization complete!")

    #
    def undo(self):
        if not self.file_movements:
            self.update_status("No actions to undo")
            return
        
        src_path, dest_path = self.file_movements.pop()
        try:
            shutil.move(dest_path, src_path)
            self.update_status(f"Undone: {os.path.basename(dest_path)} moved back to {src_path}")
        except Exception as e:
            self.update_status(f"Failed to undo: {e}")

    #
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

    #
    @staticmethod
    def move_file_with_retry(src_path, dest_path, retries=5, delay=1, file_movements=None, status_callback=None):
        for i in range(retries):
            try:
                shutil.move(src_path, dest_path)
                if file_movements is not None:
                    file_movements.append((src_path, dest_path))  # Record the movement
                if status_callback is not None:
                    status_callback(f"Moved: {os.path.basename(src_path)} to {dest_path}")
                return True
            except PermissionError:
                if status_callback is not None:
                    status_callback(f"PermissionError: Retrying in {delay} seconds... ({i+1}/{retries})")
                time.sleep(delay)
        if status_callback is not None:
            status_callback(f"Failed to move: {os.path.basename(src_path)}")
        return False

    #
    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")
        self.status_text.config(state='normal')
        self.status_text.insert('end', f"{message}\n")
        self.status_text.config(state='disabled')
        self.status_text.yview('end')

    #
    def save_settings(self):
        settings = {
            "downloads_dir": self.downloads_dir.get(),
            "target_dirs": {key: var.get() for key, var in self.target_dirs.items()}
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        messagebox.showinfo("Settings", "Settings saved successfully!")

    #
    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.downloads_dir.set(settings.get("downloads_dir", os.path.expanduser("~/Downloads")))
                for key, value in settings.get("target_dirs", {}).items():
                    self.target_dirs[key].set(value)
    
    #
    def switch_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    #
    def apply_theme(self):
        if self.dark_mode:
            self.master.style.theme_use('equilux')  # A dark theme available via ttkthemes
            self.master.configure(bg='#333333')
            self.status_text.configure(bg='#333333', fg='white', insertbackground='white')
        else:
            self.master.style.theme_use('clam')
            self.master.configure(bg='SystemButtonFace')
            self.status_text.configure(bg='white', fg='black', insertbackground='black')

#
class DownloadEventHandler(FileSystemEventHandler):
    def __init__(self, status_callback, target_dirs, file_movements):
        super().__init__()
        self.status_callback = status_callback
        self.TARGET_DIRS = {key: var.get() for key, var in target_dirs.items()}
        self.file_movements = file_movements
        for path in self.TARGET_DIRS.values():
            os.makedirs(path, exist_ok=True)

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_type = FileOrganizer.get_file_type(file_path)
            target_path = os.path.join(self.TARGET_DIRS[file_type], os.path.basename(file_path))
            FileOrganizer.move_file_with_retry(file_path, target_path)


if __name__ == "__main__":
    root = ThemedTk(theme="clam")  # Use ThemedTk for better theming options
    root.style = ttk.Style()
    root.style.theme_use('clam')  # Initial theme
    file_organizer = FileOrganizer(root)
    root.mainloop()