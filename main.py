import customtkinter as ctk
from PIL import Image, ImageFilter, ImageEnhance
import os
import sys
import requests
import shutil
import tempfile
import zipfile
from tkinter import messagebox, filedialog
import webbrowser
import threading
import time
import subprocess
import json
import platform

# --- DETECT OS ---
def detect_os():
    """Detect if running on Linux or Wine"""
    system = platform.system()
    if system == "Linux":
        # Check if running under Wine
        try:
            result = subprocess.run("wine --version", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return "wine"
        except:
            pass
        return "linux"
    elif system == "Windows":
        return "windows"
    else:
        return "other"

OS_TYPE = detect_os()

# --- GIT UPDATE FUNCTIONS ---
GITHUB_REPO = "rwandaxcode/gitpushand-dawnlaods"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
GITHUB_ZIP_URL = f"https://github.com/{GITHUB_REPO}/archive/main.zip"

# Colors - Optimized for speed
COLORS = {
    'bg_primary': '#1a1a1a',
    'bg_secondary': '#2d2d2d',
    'bg_card': '#2d2d2d',
    'accent_blue': '#0a84ff',
    'accent_green': '#30d158',
    'accent_red': '#ff453a',
    'accent_orange': '#ff9f0a',
    'text_primary': '#ffffff',
    'text_secondary': '#98989e',
    'border_light': '#3a3a3a',
    'border_medium': '#4a4a4a',
    'shadow': '#000000',
    'glass_effect': '#2d2d2d'
}

class SmoothButton(ctk.CTkButton):
    """Button isa na macOS/Deepin ihora smooth - Optimized"""
    def __init__(self, master, **kwargs):
        if 'fg_color' in kwargs:
            kwargs.pop('fg_color')
        if 'hover_color' in kwargs:
            kwargs.pop('hover_color')
        if 'corner_radius' in kwargs:
            kwargs.pop('corner_radius')
        if 'font' not in kwargs:
            kwargs['font'] = ctk.CTkFont(family="Roboto", size=13, weight="normal")
            
        super().__init__(
            master,
            corner_radius=12,
            border_width=0,
            fg_color=COLORS['accent_blue'],
            hover_color='#0a7eff',
            text_color=COLORS['text_primary'],
            **kwargs
        )
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def on_hover(self, event):
        self.configure(fg_color='#0a7eff')
        
    def on_leave(self, event):
        self.configure(fg_color=COLORS['accent_blue'])
        
    def on_press(self, event):
        self.configure(fg_color='#0969da')
        
    def on_release(self, event):
        self.configure(fg_color=COLORS['accent_blue'])

class GitConfig:
    """Manage Git configuration - OS level"""
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser("~"), ".gitpush_config.json")
        self.config = self.load_config()
        self.os_name = OS_TYPE
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
        except:
            pass
    
    def get_name(self):
        return self.config.get('name', '')
    
    def get_email(self):
        return self.config.get('email', '')
    
    def get_ssh_key(self):
        return self.config.get('ssh_key', '')
    
    def is_configured(self):
        return bool(self.get_name() and self.get_email() and self.get_ssh_key())
    
    def set_config(self, name, email, ssh_key):
        self.config['name'] = name
        self.config['email'] = email
        self.config['ssh_key'] = ssh_key
        self.save_config()
        
        # Set git config at OS level
        self.set_git_config_os(name, email)
    
    def set_git_config_os(self, name, email):
        """Set git config at OS level"""
        try:
            subprocess.run(f'git config --global user.name "{name}"', shell=True, capture_output=True)
            subprocess.run(f'git config --global user.email "{email}"', shell=True, capture_output=True)
        except:
            pass

class CloneWindow(ctk.CTkToplevel):
    """Window yo gukora git clone - Optimized"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.git_config = GitConfig()
        self.title("Clone Repository")
        self.geometry("600x500")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_secondary'])
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(15, 10), padx=25)
        
        ctk.CTkLabel(
            header,
            text="Clone Repository",
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=25, pady=5)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=10)
        
        ctk.CTkLabel(
            content,
            text="Repository URL (SSH format e.g. git@github.com:user/repo.git):",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        self.repo_entry = ctk.CTkEntry(
            content,
            height=38,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="git@github.com:username/repo.git"
        )
        self.repo_entry.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            content,
            text="Clone to:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        folder_frame = ctk.CTkFrame(content, fg_color="transparent")
        folder_frame.pack(fill="x", pady=(0, 12))
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            height=38,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="/path/to/clone"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = SmoothButton(
            folder_frame,
            text="Browse",
            width=70,
            height=32,
            command=self.browse_folder
        )
        self.browse_btn.pack(side="right")
        
        self.clone_btn = SmoothButton(
            content,
            text="Clone Now",
            height=42,
            fg_color=COLORS['accent_green'],
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            command=self.execute_clone
        )
        self.clone_btn.pack(fill="x", pady=10)
        
        self.clone_progress = ctk.CTkProgressBar(
            content,
            height=6,
            corner_radius=3,
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['border_light']
        )
        self.clone_progress.pack(fill="x", pady=5)
        self.clone_progress.set(0)
        
        self.clone_status = ctk.CTkLabel(
            content,
            text="Ready to clone",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        )
        self.clone_status.pack(anchor="w", pady=3)
        
        self.output_text = ctk.CTkTextbox(
            content,
            height=100,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(family="Roboto", size=10)
        )
        self.output_text.pack(fill="both", pady=5)
        self.output_text.insert("1.0", "Output will appear here...")
        self.output_text.configure(state="disabled")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select clone destination")
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
    
    def safe_update_ui(self, widget, **kwargs):
        def update():
            try:
                for key, value in kwargs.items():
                    if key == "text":
                        widget.configure(text=value)
                    elif key == "text_color":
                        widget.configure(text_color=value)
            except:
                pass
        self.after(0, update)
    
    def execute_clone(self):
        repo_url = self.repo_entry.get().strip()
        folder = self.folder_entry.get().strip()
        
        if not repo_url:
            messagebox.showwarning("Missing URL", "Please enter repository URL")
            return
        
        if not folder:
            messagebox.showwarning("Missing Folder", "Please select clone destination")
            return
        
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except:
                messagebox.showerror("Invalid Folder", "Could not create folder")
                return
        
        self.clone_btn.configure(state="disabled", text="Cloning...")
        self.safe_update_ui(self.clone_status, text="Starting clone...", text_color=COLORS['accent_orange'])
        self.clone_progress.set(0.1)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "=== Git Clone Started (SSH) ===\n")
        self.output_text.insert("end", f"Repository: {repo_url}\n")
        self.output_text.insert("end", "-" * 30 + "\n\n")
        
        def clone():
            try:
                clone_cmd = f'git clone "{repo_url}" "{folder}"'
                
                self.safe_update_ui(self.clone_status, text="Cloning via SSH...", text_color=COLORS['accent_orange'])
                self.clone_progress.set(0.3)
                self.output_text.insert("end", f"Command: {clone_cmd}\n\n")
                
                result = subprocess.run(
                    clone_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                self.clone_progress.set(0.8)
                
                if result.returncode == 0:
                    self.safe_update_ui(self.clone_status, text="Clone completed!", text_color=COLORS['accent_green'])
                    self.clone_progress.set(1.0)
                    self.output_text.insert("end", "\nSUCCESS: Repository cloned successfully via SSH!\n")
                    if result.stdout:
                        self.output_text.insert("end", result.stdout)
                    messagebox.showinfo("Success", "Repository cloned successfully!")
                else:
                    self.safe_update_ui(self.clone_status, text="Clone failed", text_color=COLORS['accent_red'])
                    self.clone_progress.set(0)
                    self.output_text.insert("end", "\nERROR: Clone failed!\n")
                    self.output_text.insert("end", result.stderr)
                    messagebox.showerror("Clone Failed", f"Clone failed:\n{result.stderr[:200]}")
                
                self.clone_btn.configure(state="normal", text="Clone Now")
                self.output_text.configure(state="disabled")
                
            except subprocess.TimeoutExpired:
                self.safe_update_ui(self.clone_status, text="Clone timed out", text_color=COLORS['accent_red'])
                self.clone_btn.configure(state="normal", text="Clone Now")
                self.output_text.insert("end", "\nERROR: Clone timed out\n")
                self.output_text.configure(state="disabled")
                messagebox.showerror("Clone Failed", "Clone timed out")
                
            except Exception as e:
                self.safe_update_ui(self.clone_status, text=f"Error: {str(e)[:40]}", text_color=COLORS['accent_red'])
                self.clone_btn.configure(state="normal", text="Clone Now")
                self.output_text.insert("end", f"\nERROR: {str(e)}\n")
                self.output_text.configure(state="disabled")
                messagebox.showerror("Clone Failed", f"Clone failed:\n{str(e)}")
        
        thread = threading.Thread(target=clone)
        thread.daemon = True
        thread.start()

class GitSetupWindow(ctk.CTkToplevel):
    """Window yo gushiraho Git name, email & SSH - Optimized"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.git_config = GitConfig()
        self.title("Git Setup & SSH Configuration")
        self.geometry("480x500")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_secondary'])
        
        self.setup_complete = False
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(15, 10), padx=20)
        
        ctk.CTkLabel(
            header,
            text="Git Setup (SSH)",
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=f"OS: {OS_TYPE}",
            font=ctk.CTkFont(family="Roboto", size=10),
            text_color=COLORS['text_secondary']
        ).pack(side="right")
        
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=20, pady=5)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            content,
            text="Name:",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 3))
        
        self.name_entry = ctk.CTkEntry(
            content,
            height=35,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="Your full name"
        )
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            content,
            text="Email:",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 3))
        
        self.email_entry = ctk.CTkEntry(
            content,
            height=35,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="your.email@example.com"
        )
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            content,
            text="SSH Key Status:",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(10, 3))
        
        self.ssh_status_label = ctk.CTkLabel(
            content,
            text="Not generated",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        )
        self.ssh_status_label.pack(anchor="w", pady=(0, 5))
        
        self.generate_ssh_btn = SmoothButton(
            content,
            text="Generate & Configure SSH Key",
            height=32,
            command=self.generate_ssh_key
        )
        self.generate_ssh_btn.pack(fill="x", pady=5)
        
        ctk.CTkFrame(content, height=1, fg_color=COLORS['border_light']).pack(fill="x", pady=10)
        
        self.save_btn = SmoothButton(
            content,
            text="Save & Continue",
            height=42,
            fg_color=COLORS['accent_green'],
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            command=self.next_step
        )
        self.save_btn.pack(fill="x", pady=10)
        self.save_btn.configure(state="disabled")
        
        self.ssh_key = None
        self.ssh_generated = False
        self.load_saved_config()
    
    def load_saved_config(self):
        config = self.git_config.load_config()
        if config.get('name'):
            self.name_entry.insert(0, config['name'])
        if config.get('email'):
            self.email_entry.insert(0, config['email'])
        if config.get('ssh_key'):
            self.ssh_key = config['ssh_key']
            self.ssh_generated = True
            self.ssh_status_label.configure(text="SSH Key: Configured", text_color=COLORS['accent_green'])
            self.save_btn.configure(state="normal")
    
    def generate_ssh_key(self):
        email = self.email_entry.get().strip()
        if not email:
            messagebox.showwarning("Missing Email", "Please enter your email before generating SSH key")
            return

        self.generate_ssh_btn.configure(state="disabled", text="Generating...")
        self.ssh_status_label.configure(text="Generating SSH key...", text_color=COLORS['accent_orange'])
        
        def generate():
            try:
                ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
                if not os.path.exists(ssh_dir):
                    os.makedirs(ssh_dir, mode=0o700)
                
                key_path = os.path.join(ssh_dir, "id_rsa")
                
                if not os.path.exists(key_path + ".pub"):
                    cmd = f'ssh-keygen -t rsa -b 4096 -C "{email}" -f "{key_path}" -N ""'
                    subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
                
                with open(f"{key_path}.pub", 'r') as f:
                    self.ssh_key = f.read().strip()
                
                self.ssh_generated = True
                self.ssh_status_label.configure(text="SSH Key: Generated & Ready!", text_color=COLORS['accent_green'])
                self.save_btn.configure(state="normal")
                self.generate_ssh_btn.configure(state="normal", text="Generate & Configure SSH Key")
                
                # Automatically copy public key to clipboard or show it
                messagebox.info("SSH Key Generated", "Your SSH key has been successfully created. Make sure to add this key to your GitHub account settings!")
                
            except Exception as e:
                self.ssh_status_label.configure(text=f"Error: {str(e)[:30]}", text_color=COLORS['accent_red'])
                self.generate_ssh_btn.configure(state="normal", text="Generate & Configure SSH Key")
                messagebox.showerror("SSH Error", f"Failed to generate SSH key:\n{str(e)}")
        
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
    
    def next_step(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not name or not email:
            messagebox.showwarning("Missing Info", "Please enter your name and email")
            return
        
        if not self.ssh_generated:
            messagebox.showwarning("SSH Key", "Please generate SSH key first")
            return
        
        self.git_config.set_config(name, email, self.ssh_key)
        
        self.setup_complete = True
        self.destroy()
        self.parent.show_push_window(name, email)

class GitPushWindow(ctk.CTkToplevel):
    """Window yo gukora Git Push via SSH - Optimized"""
    def __init__(self, parent, name, email):
        super().__init__(parent)
        
        self.parent = parent
        self.name = name
        self.email = email
        self.git_config = GitConfig()
        self.title("Git Push (SSH Authentication)")
        self.geometry("600x520")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_secondary'])
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(15, 10), padx=20)
        
        ctk.CTkLabel(
            header,
            text="Git Push (SSH)",
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=f"User: {name}",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        ).pack(side="right")
        
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=20, pady=5)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            content,
            text="Repository SSH URL:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        self.repo_entry = ctk.CTkEntry(
            content,
            height=38,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="git@github.com:username/repo.git"
        )
        self.repo_entry.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            content,
            text="Project Folder:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        folder_frame = ctk.CTkFrame(content, fg_color="transparent")
        folder_frame.pack(fill="x", pady=(0, 12))
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            height=38,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="/path/to/your/project"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = SmoothButton(
            folder_frame,
            text="Browse",
            width=70,
            height=32,
            command=self.browse_folder
        )
        self.browse_btn.pack(side="right")
        
        options_frame = ctk.CTkFrame(content, fg_color="transparent")
        options_frame.pack(fill="x", pady=5)
        
        self.force_push = ctk.CTkCheckBox(
            options_frame,
            text="Force Push",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['accent_blue']
        )
        self.force_push.pack(side="left", padx=(0, 15))
        
        self.accept_push = ctk.CTkCheckBox(
            options_frame,
            text="Force-with-lease",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['accent_blue']
        )
        self.accept_push.pack(side="left")
        
        self.push_btn = SmoothButton(
            content,
            text="Push via SSH Now",
            height=42,
            fg_color=COLORS['accent_green'],
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            command=self.execute_push
        )
        self.push_btn.pack(fill="x", pady=10)
        
        self.push_progress = ctk.CTkProgressBar(
            content,
            height=6,
            corner_radius=3,
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['border_light']
        )
        self.push_progress.pack(fill="x", pady=5)
        self.push_progress.set(0)
        
        self.push_status = ctk.CTkLabel(
            content,
            text="Ready to push",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        )
        self.push_status.pack(anchor="w", pady=3)
        
        self.output_text = ctk.CTkTextbox(
            content,
            height=90,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(family="Roboto", size=10)
        )
        self.output_text.pack(fill="both", pady=5)
        self.output_text.insert("1.0", "Output will appear here...")
        self.output_text.configure(state="disabled")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
    
    def safe_update_ui(self, widget, **kwargs):
        def update():
            try:
                for key, value in kwargs.items():
                    if key == "text":
                        widget.configure(text=value)
                    elif key == "text_color":
                        widget.configure(text_color=value)
            except:
                pass
        self.after(0, update)
    
    def execute_push(self):
        repo_url = self.repo_entry.get().strip()
        folder = self.folder_entry.get().strip()
        
        if not repo_url:
            messagebox.showwarning("Missing URL", "Please enter repository SSH URL")
            return
        
        if not folder:
            messagebox.showwarning("Missing Folder", "Please select project folder")
            return
        
        if not os.path.exists(folder):
            messagebox.showerror("Invalid Folder", "Selected folder does not exist")
            return
        
        self.push_btn.configure(state="disabled", text="Pushing...")
        self.safe_update_ui(self.push_status, text="Starting SSH push...", text_color=COLORS['accent_orange'])
        self.push_progress.set(0.1)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "=== Git Push (SSH) Started ===\n")
        self.output_text.insert("end", f"User: {self.name} <{self.email}>\n")
        self.output_text.insert("end", f"Repo: {repo_url}\n")
        self.output_text.insert("end", "-" * 30 + "\n\n")
        
        def push():
            try:
                # Init if needed
                git_dir = os.path.join(folder, ".git")
                if not os.path.exists(git_dir):
                    self.safe_update_ui(self.push_status, text="Initializing...", text_color=COLORS['accent_orange'])
                    self.push_progress.set(0.2)
                    self.output_text.insert("end", "Initializing git...\n")
                    subprocess.run(f'cd "{folder}" && git init', shell=True, capture_output=True, check=True)
                
                # Config user locally
                self.push_progress.set(0.3)
                subprocess.run(f'cd "{folder}" && git config user.name "{self.name}"', shell=True, capture_output=True)
                subprocess.run(f'cd "{folder}" && git config user.email "{self.email}"', shell=True, capture_output=True)
                
                # Add remote (Ensure SSH URL is used)
                self.push_progress.set(0.4)
                self.output_text.insert("end", "Configuring SSH remote...\n")
                subprocess.run(f'cd "{folder}" && git remote remove origin', shell=True, capture_output=True)
                subprocess.run(f'cd "{folder}" && git remote add origin "{repo_url}"', shell=True, capture_output=True, check=True)
                
                # Add files
                self.push_progress.set(0.5)
                self.output_text.insert("end", "Adding files...\n")
                subprocess.run(f'cd "{folder}" && git add .', shell=True, capture_output=True, check=True)
                
                # Commit
                self.push_progress.set(0.6)
                self.output_text.insert("end", "Committing...\n")
                subprocess.run(f'cd "{folder}" && git commit -m "Automated SSH commit"', shell=True, capture_output=True)
                
                # Push via SSH
                self.push_progress.set(0.7)
                self.output_text.insert("end", "Pushing via SSH...\n")
                
                push_cmd = "git push -u origin main"
                if self.force_push.get():
                    push_cmd = "git push -u origin main --force"
                elif self.accept_push.get():
                    push_cmd = "git push -u origin main --force-with-lease"
                
                result = subprocess.run(
                    f'cd "{folder}" && {push_cmd}',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                self.push_progress.set(1.0)
                
                if result.returncode == 0:
                    self.safe_update_ui(self.push_status, text="Push completed successfully!", text_color=COLORS['accent_green'])
                    self.output_text.insert("end", "\nSUCCESS: Changes pushed successfully using SSH!\n")
                    if result.stdout:
                        self.output_text.insert("end", result.stdout)
                    messagebox.showinfo("Success", "Changes pushed successfully via SSH!")
                else:
                    self.safe_update_ui(self.push_status, text="Push failed", text_color=COLORS['accent_red'])
                    self.output_text.insert("end", "\nERROR: Push failed!\n")
                    self.output_text.insert("end", result.stderr)
                    messagebox.showerror("Push Failed", f"Push failed:\n{result.stderr[:200]}")
                
                self.push_btn.configure(state="normal", text="Push via SSH Now")
                self.output_text.configure(state="disabled")
                
            except Exception as e:
                self.safe_update_ui(self.push_status, text=f"Error: {str(e)[:40]}", text_color=COLORS['accent_red'])
                self.push_btn.configure(state="normal", text="Push via SSH Now")
                self.output_text.insert("end", f"\nERROR: {str(e)}\n")
                self.output_text.configure(state="disabled")
                messagebox.showerror("Push Failed", f"Push failed:\n{str(e)}")
        
        thread = threading.Thread(target=push)
        thread.daemon = True
        thread.start()
