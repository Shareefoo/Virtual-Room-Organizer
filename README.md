# Virtual Room Organizer

**A Python application that simulates the process of organizing your room by monitoring your room/directory and automatically organizes newly downloaded files into specific shelfs/folders based on their file types (images, music, videos, documents, programs, others). This helps in keeping your room/directory clean and organized.**

## Features

- Monitors the downloads directory for new files.
- Automatically moves files to predefined target directories based on file type.
- Provides a simple and modern graphical user interface (GUI) for easy setup and monitoring.
- Allows customization of target directories through an options menu.
- Displays detailed status messages and logs activities.
- ~~Supports system notifications using the `plyer` library.~~ (TBA)
- Saves and loads settings from a configuration file (`settings.json`).

## Requirements

- Python 3.6 or later
- `watchdog` library to monitor file system events. 
- `tkinter` library (usually included with Python installations)
- `ttkthemes` library for modern UI themes
- ~~`plyer` library for system notifications~~

## Installation

1. Clone the repository:
   
   ```bash
   git clone https://github.com/yourusername/file-organizer.git
   cd file-organizer

2. Install the required libraries:
   
   ```bash
   pip install watchdog ttkthemes plyer

## Usage

1. Run the application:
   
   ```bash
   python file_organizer.py

2. The application window will open. Use the GUI to configure the downloads directory and target directories for different file types.

3. Click on "Start Monitoring" to begin monitoring the downloads directory. The application will automatically move newly downloaded files to the appropriate target directories.

4. To stop monitoring, click on "Stop Monitoring".


## Configuration

The application saves its settings in a settings.json file located in the same directory as the script. This file includes the downloads directory and target directories for different file types. The settings are automatically loaded when the application starts.

