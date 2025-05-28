import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime
import hashlib
import tkinter.scrolledtext as scrolledtext

# --- LRU Page Fault Analyzer Class ---
class LRUPageFaultAnalyzer:
    def __init__(self, frame_size=4, log_path="page_fault_log.txt"):
        self.frame_size = frame_size
        self.frames = []  # List to maintain LRU order
        self.page_faults = 0
        self.page_hits = 0
        self.page_history = []
        self.log_path = log_path

    def generate_page_id(self, filename):
        """Generate consistent page ID based on filename using hash"""
        basename = os.path.basename(filename)
        return int(hashlib.md5(basename.encode()).hexdigest()[:8], 16) % 100 + 1

    def process_page(self, filename, operation):
        """Process page reference using LRU algorithm"""
        page_id = self.generate_page_id(filename)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if page_id in self.frames:
            self.page_hits += 1
            status = "Hit"
            self.frames.remove(page_id)
            self.frames.append(page_id)
        else:
            self.page_faults += 1
            status = "Page Fault"
            if len(self.frames) >= self.frame_size:
                self.frames.pop(0)
            self.frames.append(page_id)

        self.page_history.append((page_id, operation, filename, status))
        self.log_page(page_id, operation, filename, status, timestamp)

    def log_page(self, page_id, operation, filename, status, timestamp):
        try:
            with open(self.log_path, "a") as f:
                f.write(f"{timestamp} | Operation: {operation} | File: {filename} | Page ID: {page_id} | {status}\n")
        except Exception as e:
            print("Logging failed:", e)

    def get_stats(self):
        total = self.page_faults + self.page_hits
        hit_ratio = (self.page_hits / total * 100) if total > 0 else 0
        return {
            'total': total,
            'hits': self.page_hits,
            'faults': self.page_faults,
            'hit_ratio': hit_ratio,
            'frames': list(self.frames),
            'history': list(self.page_history[-10:])
        }

    def reset(self):
        self.frames = []
        self.page_faults = 0
        self.page_hits = 0
        self.page_history = []
        try:
            open(self.log_path, 'w').close()
        except:
            pass

# --- File Management App ---
class FileManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure File Administration with LRU Page Fault Analysis")
        self.logged_in_user = None
        self.page_analyzer = LRUPageFaultAnalyzer()

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.USERS_FILE = os.path.join(self.BASE_DIR, "users.txt")
        self.USERS_DIR = os.path.join(self.BASE_DIR, "users_data")
        os.makedirs(self.USERS_DIR, exist_ok=True)

        self.create_login_screen()

    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        login_frame = tk.Frame(self.root)
        login_frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(login_frame, text="Secure File Administration System", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(login_frame, text="Username:", font=("Arial", 12)).pack(pady=5)
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12))
        self.username_entry.pack(pady=5, fill='x')

        tk.Label(login_frame, text="Password:", font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5, fill='x')

        tk.Button(login_frame, text="Login", command=self.authenticate,
                  font=("Arial", 12), bg="#4CAF50", fg="white", width=20).pack(pady=20)

        self.root.bind('<Return>', lambda event: self.authenticate())

    def authenticate(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return

        if not os.path.exists(self.USERS_FILE):
            messagebox.showerror("Error", "users.txt file not found!")
            return

        try:
            with open(self.USERS_FILE, "r") as f:
                for line in f:
                    if ' ' in line:
                        u, p = line.strip().split(' ', 1)
                        if username == u and password == p:
                            self.logged_in_user = username
                            self.user_folder = os.path.join(self.USERS_DIR, username)
                            os.makedirs(self.user_folder, exist_ok=True)
                            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                            self.create_main_menu()
                            return
            messagebox.showerror("Login Failed", "Invalid credentials.")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")

    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(main_frame, text=f"Welcome: {self.logged_in_user}",
                 font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(main_frame, text="LRU Page Fault Analysis Enabled",
                 font=("Arial", 10), fg="blue").pack(pady=5)

        buttons = [
            ("Create File", self.create_file, "#2196F3"),
            ("Write to File", self.write_file, "#4CAF50"),
            ("Modify File", self.modify_file, "#FF9800"),
            ("Read File", self.read_file, "#9C27B0"),
            ("Search in File", self.search_file, "#607D8B"),
            ("Delete File", self.delete_file, "#F44336"),
            ("View Page Fault Analysis", self.view_stats, "#795548"),
            ("Reset Page Fault Analysis", self.reset_stats, "#FFC107"),
            ("Logout", self.logout, "#9E9E9E"),
        ]

        for (text, command, color) in buttons:
            tk.Button(main_frame, text=text, width=30, command=command,
                      font=("Arial", 11), bg=color, fg="white", pady=5).pack(pady=3)

    def get_full_path(self, filename):
        return os.path.join(self.user_folder, filename)

    def log_page_op(self, operation, filename):
        self.page_analyzer.process_page(filename, operation)

    def create_file(self):
        filename = simpledialog.askstring("Create File", "Enter file name:")
        if filename:
            path = self.get_full_path(filename.strip())
            try:
                with open(path, 'x') as f:
                    pass
                messagebox.showinfo("Success", f"File '{filename}' created successfully.")
                self.log_page_op("CREATE", filename)
            except FileExistsError:
                messagebox.showwarning("File Exists", "File already exists.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file: {str(e)}")

    def write_file(self):
        filename = simpledialog.askstring("Write to File", "Enter file name:")
        if filename:
            path = self.get_full_path(filename.strip())
            if not os.path.exists(path):
                messagebox.showerror("Error", "File doesn't exist. Create it first.")
                return
            content = simpledialog.askstring("Write Content", "Enter content to add:")
            if content:
                try:
                    with open(path, "a") as f:
                        f.write(content + "\n")
                    messagebox.showinfo("Success", "Content added successfully.")
                    self.log_page_op("WRITE", filename)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to write: {str(e)}")

    def modify_file(self):
        filename = simpledialog.askstring("Modify File", "Enter file name:")
        if filename:
            path = self.get_full_path(filename.strip())
            if not os.path.exists(path):
                messagebox.showerror("Error", "File doesn't exist.")
                return
            content = simpledialog.askstring("Modify Content", "Enter new content:")
            if content:
                try:
                    with open(path, "w") as f:
                        f.write(content + "\n")
                    messagebox.showinfo("Success", "File modified successfully.")
                    self.log_page_op("MODIFY", filename)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to modify: {str(e)}")

    def read_file(self):
        filename = simpledialog.askstring("Read File", "Enter file name:")
        if filename:
            path = self.get_full_path(filename.strip())
            if not os.path.exists(path):
                messagebox.showerror("Error", "File doesn't exist.")
                return
            try:
                with open(path, "r") as f:
                    content = f.read()
                messagebox.showinfo(f"Contents of '{filename}'", content or "(File is empty)")
                self.log_page_op("READ", filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read: {str(e)}")

    def search_file(self):
        filename = simpledialog.askstring("Search File", "Enter file name:")
        if filename:
            keyword = simpledialog.askstring("Search", "Enter keyword to search:")
            path = self.get_full_path(filename.strip())
            if not os.path.exists(path):
                messagebox.showerror("Error", "File doesn't exist.")
                return
            try:
                with open(path, "r") as f:
                    matches = [f"Line {i+1}: {line.strip()}"
                               for i, line in enumerate(f) if keyword.lower() in line.lower()]
                if matches:
                    messagebox.showinfo("Search Results", "\n".join(matches[:10]))
                else:
                    messagebox.showinfo("No Match", "Keyword not found.")
                self.log_page_op("SEARCH", filename)
            except Exception as e:
                messagebox.showerror("Error", f"Search failed: {str(e)}")

    def delete_file(self):
        filename = simpledialog.askstring("Delete File", "Enter file name:")
        if filename:
            path = self.get_full_path(filename.strip())
            if os.path.exists(path):
                confirm = messagebox.askyesno("Delete File", f"Delete '{filename}'?")
                if confirm:
                    try:
                        os.remove(path)
                        messagebox.showinfo("Success", "File deleted.")
                        self.log_page_op("DELETE", filename)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete: {str(e)}")
            else:
                messagebox.showerror("Error", "File not found.")

    def view_stats(self):
        stats = self.page_analyzer.get_stats()

        win = tk.Toplevel(self.root)
        win.title("Page Fault Analysis")
        win.geometry("600x500")

        tk.Label(win, text="=== LRU Page Fault Analysis ===", font=("Arial", 14, "bold")).pack(pady=10)

        text = f"""
Total Page References: {stats['total']}
Page Hits: {stats['hits']}
Page Faults: {stats['faults']}
Hit Ratio: {stats['hit_ratio']:.2f}%

Current Pages in Memory (LRU Order): {' → '.join(map(str, stats['frames']))}
"""
        tk.Label(win, text=text, font=("Arial", 11), justify='left').pack()

        tk.Label(win, text="Recent Operations:", font=("Arial", 12, "bold")).pack(pady=5)

        history_box = scrolledtext.ScrolledText(win, width=70, height=15, font=("Courier", 10))
        history_box.pack(fill='both', expand=True)

        history_box.insert('1.0', "Page ID | Operation | Filename        | Status\n")
        history_box.insert('2.0', "-" * 50 + "\n")
        for pid, op, fn, st in stats['history']:
            history_box.insert(tk.END, f"{pid:<7} | {op:<9} | {fn:<15} | {st}\n")
        history_box.config(state='disabled')

    def reset_stats(self):
        if messagebox.askyesno("Reset Stats", "Reset page fault statistics?"):
            self.page_analyzer.reset()
            messagebox.showinfo("Reset", "Page fault data cleared.")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logged_in_user = None
            self.page_analyzer.reset()
            self.create_login_screen()

# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagementApp(root)
    root.geometry("500x600")
    root.resizable(True, True)
    root.mainloop()
