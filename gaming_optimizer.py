import os
import sys
import time
import shutil
import ctypes
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path


# -----------------------------
# Windows administrator check
# -----------------------------

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


# -----------------------------
# Utility functions
# -----------------------------

def format_bytes(size):
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def get_folder_size(folder):
    total = 0

    try:
        for root, dirs, files in os.walk(folder):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    total += os.path.getsize(file_path)
                except (PermissionError, FileNotFoundError, OSError):
                    pass
    except (PermissionError, FileNotFoundError, OSError):
        pass

    return total


def delete_contents(folder, log_callback):
    deleted_size = 0
    deleted_files = 0

    if not os.path.exists(folder):
        return deleted_size, deleted_files

    try:
        entries = os.listdir(folder)
    except (PermissionError, OSError):
        return deleted_size, deleted_files

    for entry in entries:
        path = os.path.join(folder, entry)

        try:
            if os.path.isfile(path) or os.path.islink(path):
                try:
                    deleted_size += os.path.getsize(path)
                except OSError:
                    pass

                os.remove(path)
                deleted_files += 1

            elif os.path.isdir(path):
                folder_size = get_folder_size(path)
                shutil.rmtree(path, ignore_errors=False)
                deleted_size += folder_size
                deleted_files += 1

        except (PermissionError, FileNotFoundError, OSError) as error:
            log_callback(f"Skipped: {path} ({error})")

    return deleted_size, deleted_files


# -----------------------------
# Cleanup actions
# -----------------------------

def clean_temp_files(log_callback):
    temp_locations = [
        os.environ.get("TEMP"),
        os.environ.get("TMP"),
        r"C:\Windows\Temp",
    ]

    total_size = 0
    total_files = 0

    for location in temp_locations:
        if location:
            log_callback(f"Cleaning: {location}")

            size, files = delete_contents(location, log_callback)

            total_size += size
            total_files += files

    return total_size, total_files


def empty_recycle_bin(log_callback):
    try:
        flags = 0x00000001 | 0x00000002 | 0x00000004
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
        log_callback("Recycle Bin emptied.")
        return True
    except Exception as error:
        log_callback(f"Could not empty Recycle Bin: {error}")
        return False


def enable_windows_game_mode(log_callback):
    try:
        command = [
            "reg",
            "add",
            r"HKCU\Software\Microsoft\GameBar",
            "/v",
            "AutoGameModeEnabled",
            "/t",
            "REG_DWORD",
            "/d",
            "1",
            "/f",
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=False
        )

        if result.returncode == 0:
            log_callback("Windows Game Mode enabled.")
            return True

        log_callback("Could not enable Windows Game Mode.")
        return False

    except Exception as error:
        log_callback(f"Game Mode error: {error}")
        return False


def set_high_performance_power_plan(log_callback):
    try:
        # Windows built-in High Performance power plan
        result = subprocess.run(
            ["powercfg", "/setactive", "SCHEME_MIN"],
            capture_output=True,
            text=True,
            shell=False
        )

        if result.returncode == 0:
            log_callback("High Performance power plan selected.")
            return True

        log_callback("Could not change the power plan.")
        return False

    except Exception as error:
        log_callback(f"Power plan error: {error}")
        return False


# -----------------------------
# Game launching
# -----------------------------

def launch_game(game_path, log_callback):
    if not game_path:
        messagebox.showwarning("No game selected", "Please select a game executable first.")
        return

    if not os.path.isfile(game_path):
        messagebox.showerror("Invalid file", "The selected game file does not exist.")
        return

    try:
        log_callback(f"Launching game: {game_path}")

        process = subprocess.Popen(
            [game_path],
            cwd=os.path.dirname(game_path),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

        # HIGH priority is generally safer than REALTIME.
        try:
            process.nice = None
            import psutil

            game_process = psutil.Process(process.pid)
            game_process.nice(psutil.HIGH_PRIORITY_CLASS)

            log_callback("Game launched with High priority.")

        except ImportError:
            log_callback(
                "Game launched, but process priority was not changed.\n"
                "Install psutil with: pip install psutil"
            )

        except Exception as error:
            log_callback(f"Could not set game priority: {error}")

    except Exception as error:
        messagebox.showerror("Launch error", str(error))


# -----------------------------
# GUI application
# -----------------------------

class GamingOptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gaming PC Optimizer")
        self.root.geometry("760x560")
        self.root.minsize(650, 480)

        self.selected_game = tk.StringVar()

        self.create_widgets()
        self.update_disk_space()

    def create_widgets(self):
        title = ttk.Label(
            self.root,
            text="Gaming PC Optimizer",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=(15, 5))

        subtitle = ttk.Label(
            self.root,
            text="Clean temporary files and prepare Windows for gaming",
            font=("Segoe UI", 10)
        )
        subtitle.pack(pady=(0, 15))

        info_frame = ttk.LabelFrame(self.root, text="System Information")
        info_frame.pack(fill="x", padx=20, pady=5)

        self.disk_label = ttk.Label(info_frame, text="Checking disk space...")
        self.disk_label.pack(anchor="w", padx=10, pady=8)

        settings_frame = ttk.LabelFrame(self.root, text="Gaming Options")
        settings_frame.pack(fill="x", padx=20, pady=10)

        self.game_mode_var = tk.BooleanVar(value=True)
        self.power_plan_var = tk.BooleanVar(value=False)
        self.recycle_bin_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            settings_frame,
            text="Enable Windows Game Mode",
            variable=self.game_mode_var
        ).pack(anchor="w", padx=10, pady=4)

        ttk.Checkbutton(
            settings_frame,
            text="Use High Performance power plan",
            variable=self.power_plan_var
        ).pack(anchor="w", padx=10, pady=4)

        ttk.Checkbutton(
            settings_frame,
            text="Empty Recycle Bin",
            variable=self.recycle_bin_var
        ).pack(anchor="w", padx=10, pady=4)

        game_frame = ttk.LabelFrame(self.root, text="Launch Game With High Priority")
        game_frame.pack(fill="x", padx=20, pady=5)

        game_entry = ttk.Entry(
            game_frame,
            textvariable=self.selected_game
        )
        game_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        ttk.Button(
            game_frame,
            text="Browse",
            command=self.browse_game
        ).pack(side="right", padx=10, pady=10)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=10)

        self.clean_button = ttk.Button(
            button_frame,
            text="Clean and Optimize",
            command=self.start_optimization
        )
        self.clean_button.pack(side="left", padx=(0, 8))

        ttk.Button(
            button_frame,
            text="Launch Game",
            command=self.launch_selected_game
        ).pack(side="left")

        log_frame = ttk.LabelFrame(self.root, text="Activity Log")
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.log_text = tk.Text(
            log_frame,
            height=12,
            wrap="word",
            state="disabled",
            background="#111111",
            foreground="#eeeeee"
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.log_text.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.log_text.configure(yscrollcommand=scrollbar.set)

    def log(self, message):
        self.root.after(0, self._write_log, message)

    def _write_log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def browse_game(self):
        path = filedialog.askopenfilename(
            title="Select a game executable",
            filetypes=[
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            ]
        )

        if path:
            self.selected_game.set(path)

    def update_disk_space(self):
        try:
            drive = os.environ.get("SystemDrive", "C:") + "\\"
            total, used, free = shutil.disk_usage(drive)

            self.disk_label.config(
                text=(
                    f"Drive {drive} | "
                    f"Free: {format_bytes(free)} | "
                    f"Total: {format_bytes(total)}"
                )
            )

        except Exception:
            self.disk_label.config(text="Could not read disk space.")

    def start_optimization(self):
        self.clean_button.config(state="disabled")
        self.log("Starting optimization...")

        worker = threading.Thread(
            target=self.optimize,
            daemon=True
        )
        worker.start()

    def optimize(self):
        try:
            before_free = self.get_free_space()

            cleaned_size, cleaned_files = clean_temp_files(self.log)

            if self.recycle_bin_var.get():
                empty_recycle_bin(self.log)

            if self.game_mode_var.get():
                enable_windows_game_mode(self.log)

            if self.power_plan_var.get():
                set_high_performance_power_plan(self.log)

            after_free = self.get_free_space()

            self.log("")
            self.log(f"Files cleaned: {cleaned_files}")
            self.log(f"Estimated data removed: {format_bytes(cleaned_size)}")

            if before_free is not None and after_free is not None:
                self.log(
                    f"Free space change: "
                    f"{format_bytes(after_free - before_free)}"
                )

            self.log("Optimization completed.")

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Complete",
                    "Cleanup and optimization completed."
                )
            )

        finally:
            self.root.after(
                0,
                lambda: self.clean_button.config(state="normal")
            )
            self.root.after(0, self.update_disk_space)

    def get_free_space(self):
        try:
            drive = os.environ.get("SystemDrive", "C:") + "\\"
            return shutil.disk_usage(drive).free
        except Exception:
            return None

    def launch_selected_game(self):
        game_path = self.selected_game.get().strip()

        threading.Thread(
            target=launch_game,
            args=(game_path, self.log),
            daemon=True
        ).start()


def main():
    if os.name != "nt":
        print("This program is designed for Windows.")
        sys.exit(1)

    root = tk.Tk()
    app = GamingOptimizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
