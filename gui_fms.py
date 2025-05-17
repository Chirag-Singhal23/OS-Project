import os
import tkinter as tk
from tkinter import messagebox, simpledialog

class FileManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure File Admin System with User Folders")
        self.logged_in_user = None
        
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.USERS_FILE = os.path.join(self.BASE_DIR, "users.txt")
        self.USERS_DIR = os.path.join(self.BASE_DIR, "users_data")  # base folder for user dirs
        os.makedirs(self.USERS_DIR, exist_ok=True)  # create if not exists
        
        self.create_login_screen()

    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.authenticate).pack(pady=20)

    def authenticate(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not os.path.exists(self.USERS_FILE):
            messagebox.showerror("Error", f"users.txt not found at:\n{self.USERS_FILE}")
            return
        
        try:
            with open(self.USERS_FILE, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 2:
                        continue
                    fileUser, filePass = parts
                    if username == fileUser and password == filePass:
                        self.logged_in_user = username
                        # create user folder if not exists
                        self.user_folder = os.path.join(self.USERS_DIR, username)
                        os.makedirs(self.user_folder, exist_ok=True)
                        messagebox.showinfo("Success", f"Welcome {username}!")
                        self.create_main_menu()
                        return
            messagebox.showerror("Login Failed", "Invalid username or password!")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading users file:\n{str(e)}")

    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Logged in as: {self.logged_in_user}", font=("Arial", 12)).pack(pady=10)

        buttons = [
            ("Create File", self.create_file),
            ("Write to File", self.write_to_file),
            ("Modify File", self.modify_file),
            ("Search in File", self.search_in_file),
            ("Read File", self.read_file),
            ("Delete File", self.delete_file),
            ("Logout", self.logout)
        ]

        for (text, cmd) in buttons:
            tk.Button(self.root, text=text, width=30, command=cmd).pack(pady=5)

    def get_full_path(self, filename):
        # file path inside user folder
        return os.path.join(self.user_folder, filename)

    def create_file(self):
        filename = simpledialog.askstring("Create File", "Enter file name:")
        if not filename:
            return
        full_path = self.get_full_path(filename)
        try:
            with open(full_path, 'x') as f:
                pass
            messagebox.showinfo("Success", f"File '{filename}' created in your folder.")
        except FileExistsError:
            messagebox.showwarning("Warning", "File already exists.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def write_to_file(self):
        filename = simpledialog.askstring("Write to File", "Enter file name:")
        if not filename:
            return
        full_path = self.get_full_path(filename)
        if not os.path.exists(full_path):
            messagebox.showerror("Error", "File does not exist.")
            return
        content = simpledialog.askstring("Write to File", "Enter content to append:")
        if content is None:
            return
        try:
            with open(full_path, 'a') as f:
                f.write(content + "\n")
            messagebox.showinfo("Success", "Content written successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def modify_file(self):
        filename = simpledialog.askstring("Modify File", "Enter file name:")
        if not filename:
            return
        full_path = self.get_full_path(filename)
        if not os.path.exists(full_path):
            messagebox.showerror("Error", "File does not exist.")
            return
        content = simpledialog.askstring("Modify File", "Enter new content (will overwrite):")
        if content is None:
            return
        try:
            with open(full_path, 'w') as f:
                f.write(content + "\n")
            messagebox.showinfo("Success", "File modified successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_in_file(self):
        filename = simpledialog.askstring("Search File", "Enter file name:")
        if not filename:
            return
        keyword = simpledialog.askstring("Search File", "Enter keyword to search:")
        if keyword is None:
            return
        full_path = self.get_full_path(filename)
        if not os.path.exists(full_path):
            messagebox.showerror("Error", "File does not exist.")
            return

        try:
            with open(full_path, 'r') as f:
                lines = f.readlines()
            found_lines = [line.strip() for line in lines if keyword in line]
            if found_lines:
                messagebox.showinfo("Search Results", "\n".join(found_lines))
            else:
                messagebox.showinfo("Search Results", "Keyword not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def read_file(self):
        filename = simpledialog.askstring("Read File", "Enter file name:")
        if not filename:
            return
        full_path = self.get_full_path(filename)
        if not os.path.exists(full_path):
            messagebox.showerror("Error", "File does not exist.")
            return
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            messagebox.showinfo(f"Contents of {filename}", content if content else "(Empty file)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_file(self):
        filename = simpledialog.askstring("Delete File", "Enter file name:")
        if not filename:
            return
        full_path = self.get_full_path(filename)
        if not os.path.exists(full_path):
            messagebox.showerror("Error", "File does not exist.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{filename}'?"):
            try:
                os.remove(full_path)
                messagebox.showinfo("Deleted", f"File '{filename}' deleted.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def logout(self):
        self.logged_in_user = None
        messagebox.showinfo("Logout", "You have been logged out.")
        self.create_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagementApp(root)
    root.geometry("400x450")
    root.mainloop()
