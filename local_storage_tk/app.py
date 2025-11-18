import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox
import random
import string
import shutil

# -------------------------------------------------------------
# INITIAL SETUP
# -------------------------------------------------------------
BASE_DIR = "storage"
os.makedirs(BASE_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (user_key TEXT PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS files (user_key TEXT, filename TEXT)")
    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------------------
# KEY GENERATION
# -------------------------------------------------------------
def generate_key():
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(6))

# -------------------------------------------------------------
# MAIN APPLICATION
# -------------------------------------------------------------
class StorageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POCKET")
        self.root.geometry("420x320")
        self.root.resizable(False, False)

        self.root.configure(bg="#F4F4F4")

        title = tk.Label(
            root, text="POCKET", 
            font=("PRESS START 2P", 16, "bold"), bg="#F4F4F4"
        )
        title.pack(pady=15)

        self.key_entry = tk.Entry(root, font=("Segoe UI", 14), justify="center", width=18)
        self.key_entry.pack(pady=5)

        btn_frame = tk.Frame(root, bg="#F4F4F4")
        btn_frame.pack(pady=20)

        access_btn = tk.Button(
            btn_frame, text="Access Storage", command=self.access_storage,
            font=("Segoe UI", 11), bg="#4CAF50", fg="white",
            activebackground="#45A049", width=18, height=1, relief="flat"
        )
        access_btn.pack(pady=5)

        create_btn = tk.Button(
            btn_frame, text="Create New Key", command=self.create_key,
            font=("Segoe UI", 11), bg="#2196F3", fg="white",
            activebackground="#1E88E5", width=18, height=1, relief="flat"
        )
        create_btn.pack(pady=5)

    # ---------------------------------------------------------
    # Create a new storage key
    # ---------------------------------------------------------
    def create_key(self):
        key = generate_key()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (user_key) VALUES (?)", (key,))
        conn.commit()
        conn.close()

        os.makedirs(f"{BASE_DIR}/{key}", exist_ok=True)

        messagebox.showinfo("Key Created", f"Your storage key is:\n\n{key}")
        self.open_dashboard(key)

    # ---------------------------------------------------------
    # Access existing storage
    # ---------------------------------------------------------
    def access_storage(self):
        key = self.key_entry.get()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_key=?", (key,))
        exists = c.fetchone()
        conn.close()

        if exists:
            self.open_dashboard(key)
        else:
            messagebox.showerror("Error", "Invalid Key!")

    # ---------------------------------------------------------
    # Dashboard Window (clean UI)
    # ---------------------------------------------------------
    def open_dashboard(self, key):
        dash = tk.Toplevel(self.root)
        dash.title(f"Storage Dashboard - {key}")
        dash.geometry("420x500")
        dash.resizable(False, False)
        dash.configure(bg="#F4F4F4")

        tk.Label(
            dash, text=f"Storage Key: {key}",
            font=("Segoe UI", 16, "bold"), bg="#F4F4F4"
        ).pack(pady=10)

        upload_btn = tk.Button(
            dash, text="Upload File", command=lambda: self.upload_file(key, file_list),
            font=("Segoe UI", 11), bg="#673AB7", fg="white",
            activebackground="#5E35B1", width=20, relief="flat"
        )
        upload_btn.pack(pady=10)

        tk.Label(
            dash, text="Your Files:", font=("Segoe UI", 12, "bold"), bg="#F4F4F4"
        ).pack()

        file_list = tk.Listbox(
            dash, width=45, height=15, font=("Segoe UI", 10),
            selectbackground="#2196F3", activestyle="none"
        )
        file_list.pack(pady=5)

        self.load_files(key, file_list)

        open_btn = tk.Button(
            dash, text="Open Selected File",
            command=lambda: self.open_file(key, file_list),
            font=("Segoe UI", 11), bg="#009688", fg="white",
            activebackground="#00897B", width=20, relief="flat"
        )
        open_btn.pack(pady=15)

    # ---------------------------------------------------------
    # Load Files
    # ---------------------------------------------------------
    def load_files(self, key, listbox):
        listbox.delete(0, tk.END)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT filename FROM files WHERE user_key=?", (key,))
        files = c.fetchall()
        conn.close()

        for f in files:
            listbox.insert(tk.END, f[0])

    # ---------------------------------------------------------
    # Upload file
    # ---------------------------------------------------------
    def upload_file(self, key, listbox):
        filepath = filedialog.askopenfilename()

        if not filepath:
            return

        filename = os.path.basename(filepath)
        user_folder = f"{BASE_DIR}/{key}"

        shutil.copy(filepath, os.path.join(user_folder, filename))

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO files (user_key, filename) VALUES (?, ?)", (key, filename))
        conn.commit()
        conn.close()

        self.load_files(key, listbox)
        messagebox.showinfo("Success", "File uploaded!")

    # ---------------------------------------------------------
    # Open file
    # ---------------------------------------------------------
    def open_file(self, key, listbox):
        try:
            filename = listbox.get(listbox.curselection())
        except:
            messagebox.showerror("Error", "Please select a file!")
            return

        filepath = os.path.abspath(os.path.join(BASE_DIR, key, filename))

        if not os.path.exists(filepath):
            messagebox.showerror("Error", "File not found!")
            return

        os.startfile(filepath)


# -------------------------------------------------------------
# RUN THE APP IN VS CODE
# -------------------------------------------------------------
root = tk.Tk()
app = StorageApp(root)
root.mainloop()