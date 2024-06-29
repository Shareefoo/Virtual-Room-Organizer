import os
import time
import shutil
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, StringVar


class FileOrganizer:

    def __init__(self, master):
        self.master = master
        master.title("File Organizer")

        # Define the directory to be monitored
        self.downloads_dir = StringVar(value=os.path.expanduser("~/Downloads"))

        self.label = Label(master, text="Downloads Directory:")
        self.label.pack()

        self.downloads_entry = Entry(master, textvariable=self.downloads_dir, width=50)
        self.downloads_entry.pack()

        self.browse_button = Button(master, text="Browse", command=self.browse_directory)
        self.browse_button.pack()

        self.start_button = Button(master, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack()

        self.stop_button = Button(master, text="Stop Monitoring", command=self.stop_monitoring, state='disabled')
        self.stop_button.pack()

        self.status_label = Label(master, text="Status: Not monitoring")
        self.status_label.pack()

        self.observer = None


    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.downloads_dir.get())
        if directory:
            self.downloads_dir.set(directory)


    def start_monitoring(self):
        self.downloads_dir_path = self.downloads_dir.get()
        if not os.path.exists(self.downloads_dir_path):
            messagebox.showerror("Error", "The specified directory does not exist.")
            return

        self.observer = Observer()
        event_handler = DownloadEventHandler(self.update_status)
        event_handler.set_target_dirs(self.downloads_dir_path)
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
        self.status_label.config(text="Status: Not monitoring")

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")


# Handler for prcoessing file system events
class DownloadEventHandler(FileSystemEventHandler):

    def __init__(self, status_callback):
        super().__init__()
        self.status_callback = status_callback
        self.TARGET_DIRS = {}

    def set_target_dirs(self, base_dir):
        self.TARGET_DIRS = {
            "images": os.path.join(base_dir, "Images"),
            "music": os.path.join(base_dir, "Music"),
            "videos": os.path.join(base_dir, "Videos"),
            "documents": os.path.join(base_dir, "Documents"),
            "programs": os.path.join(base_dir, "Programs"),
            "others": os.path.join(base_dir, "Others")
        }

        # Ensure the target directories exists
        for path in self.TARGET_DIRS.values():
            os.makedirs(path, exist_ok=True)

    # Function to determine the file type based on extension
    @staticmethod
    def get_file_type(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
            return "images"
        elif ext in ['.mp3']:
            return "music"
        elif ext in ['.mp4', '.mov', '.avi']:
            return "videos"
        elif ext in ['.text', '.pdf', '.epub', '.docx', 'pptx', 'xlsx']:
            return "documents"
        elif ext in ['.exe', '.msi']:
            return "programs"
        elif ext in ['.zip', '.rar']:
            return "compressed"
        else:
            return "others"
        
        
    # Function to move file with retry mechanism to prevent errors when the file is being used by another process
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
    file_organizer = FileOrganizer(root)
    root.mainloop()