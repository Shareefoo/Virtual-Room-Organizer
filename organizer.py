import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

# Define the directory to be monitored and the target directories
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
TARGET_DIRS = {
    "images": os.path.expanduser("~/Downloads/Images"),
    "music": os.path.expanduser("~/Downloads/Music"),
    "videos": os.path.expanduser("~/Downloads/Videos"),
    "documents": os.path.expanduser("~/Downloads/Documents"),
    "programs": os.path.expanduser("~/Downloads/Programs"),
    "compressed": os.path.expanduser("~/Downloads/Compressed"),
    "others": os.path.expanduser("~/Downloads/Others")
}

# Ensure the target directories exists
for path in TARGET_DIRS.values():
    os.makedirs(path, exist_ok=True)

# Function to determine the file type based on extension
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
def move_file_with_retry(src_path, dest_path, retries=5, delay=1):
    for i in range(retries):
        try:
            shutil.move(src_path, dest_path)
            print(f"Moved: {src_path} to {dest_path}")
            return True
        except PermissionError:
            print(f"PermissionError: Retrying in {delay} seconds... ({i+1}/{retries})")
            time.sleep(delay)
    print(f"Failed to move: {src_path}")
    return False

# Handler for prcoessing file system events
class DownloadEventHandler(FileSystemEventHandler):
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            file_path = event.src_path
            file_type = get_file_type(file_path)
            target_path = os.path.join(TARGET_DIRS[file_type], os.path.basename(file_path))
            shutil.move(file_path, target_path)
            move_file_with_retry(file_path, target_path)

# Setting up the observer
event_handler = DownloadEventHandler()
Observer = Observer()
Observer.schedule(event_handler, DOWNLOADS_DIR, recursive=False)

try:
    Observer.start()
    print(f"Monitoring {DOWNLOADS_DIR}...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    Observer.stop()
Observer.join