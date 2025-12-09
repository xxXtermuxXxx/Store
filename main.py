import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import json
import sys
import shutil

def load_apps():
    try:
        with open("apps.json", "r") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load apps.json:\n{e}")
        return []

def open_terminal_and_run(command):
    # Detect available terminals and run command inside new window

    terminals = [
        ("gnome-terminal", ["gnome-terminal", "--"]),
        ("x-terminal-emulator", ["x-terminal-emulator", "-e"]),
        ("konsole", ["konsole", "-e"]),
        ("xfce4-terminal", ["xfce4-terminal", "-e"]),
        ("lxterminal", ["lxterminal", "-e"]),
        ("mate-terminal", ["mate-terminal", "-e"]),
        ("terminator", ["terminator", "-x"]),
        ("urxvt", ["urxvt", "-e"]),
        ("xterm", ["xterm", "-e"])
    ]

    for name, base_cmd in terminals:
        if shutil.which(name):
            # Construct full command list
            full_cmd = base_cmd + [command]
            try:
                subprocess.Popen(full_cmd)
                return True
            except Exception:
                continue
    # If no terminal found, fallback to blocking run (not recommended)
    messagebox.showwarning("Warning", "No known terminal emulator found.\nRunning install in background.")
    threading.Thread(target=lambda: subprocess.run(command, shell=True)).start()
    return False

def install_app_popup(app):
    def do_install():
        # Run the install command in a new terminal window
        if "install_cmd" not in app or not app["install_cmd"]:
            messagebox.showerror("Error", "No install command available for this app.")
            return
        success = open_terminal_and_run(app["install_cmd"])
        if success:
            popup.destroy()

    popup = tk.Toplevel()
    popup.title(f"View App - {app.get('name', 'App')}")
    popup.geometry("400x300")
    popup.grab_set()

    label_name = ttk.Label(popup, text=app.get("name", "App"), font=("Arial", 16, "bold"))
    label_name.pack(pady=(10, 5))

    desc_text = tk.Text(popup, wrap="word", height=10)
    desc_text.pack(fill="both", expand=True, padx=10, pady=5)
    desc_text.insert("1.0", app.get("description", "No description available."))
    desc_text.config(state="disabled")

    btn_frame = ttk.Frame(popup)
    btn_frame.pack(pady=10)

    install_btn = ttk.Button(btn_frame, text="Install", command=do_install)
    install_btn.pack(side="left", padx=10)

    cancel_btn = ttk.Button(btn_frame, text="Cancel", command=popup.destroy)
    cancel_btn.pack(side="right", padx=10)

class AppStoreGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Debian App Store")
        self.geometry("600x400")

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        apps = load_apps()
        for app in apps:
            frame = ttk.Frame(scroll_frame, relief="ridge", borderwidth=2, padding=10)
            frame.pack(fill="x", pady=5, padx=5)

            name_label = ttk.Label(frame, text=app.get("name", "Unnamed App"), font=("Arial", 14, "bold"))
            name_label.pack(anchor="w")

            desc_label = ttk.Label(frame, text=app.get("description", ""), font=("Arial", 10), wraplength=500)
            desc_label.pack(anchor="w")

            view_btn = ttk.Button(frame, text="View", command=lambda a=app: install_app_popup(a))
            view_btn.pack(anchor="e")

if __name__ == "__main__":
    app = AppStoreGUI()
    app.mainloop()
