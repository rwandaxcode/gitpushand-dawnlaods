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
    
    def get_git_token(self):
        return self.config.get('git_token', '')
    
    def is_configured(self):
        return bool(self.get_name() and self.get_email() and self.get_ssh_key())
    
    def set_config(self, name, email, ssh_key, git_token=''):
        self.config['name'] = name
        self.config['email'] = email
        self.config['ssh_key'] = ssh_key
        if git_token:
            self.config['git_token'] = git_token
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
        
        # Header - Simplified for speed
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(15, 10), padx=25)
        
        try:
            if os.path.exists("download.png"):
                clone_icon = ctk.CTkImage(light_image=Image.open("download.png"), dark_image=Image.open("download.png"), size=(28, 28))
                ctk.CTkLabel(header, image=clone_icon, text="").pack(side="left", padx=(0, 10))
        except:
            pass
        
        ctk.CTkLabel(
            header,
            text="Clone Repository",
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=25, pady=5)
        
        # Content - Simplified
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Repository URL
        ctk.CTkLabel(
            content,
            text="Repository URL:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        self.repo_entry = ctk.CTkEntry(
            content,
            height=38,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="https://github.com/username/repo.git"
        )
        self.repo_entry.pack(fill="x", pady=(0, 12))
        
        # Destination folder
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
        
        # Clone button
        self.clone_btn = SmoothButton(
            content,
            text="Clone Now",
            height=42,
            fg_color=COLORS['accent_green'],
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            command=self.execute_clone
        )
        self.clone_btn.pack(fill="x", pady=10)
        
        # Progress
        self.clone_progress = ctk.CTkProgressBar(
            content,
            height=6,
            corner_radius=3,
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['border_light']
        )
        self.clone_progress.pack(fill="x", pady=5)
        self.clone_progress.set(0)
        
        # Status
        self.clone_status = ctk.CTkLabel(
            content,
            text="Ready to clone",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        )
        self.clone_status.pack(anchor="w", pady=3)
        
        # Output - smaller for speed
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
        self.output_text.insert("end", "=== Git Clone Started ===\n")
        self.output_text.insert("end", f"Repository: {repo_url}\n")
        self.output_text.insert("end", "-" * 30 + "\n\n")
        
        def clone():
            try:
                git_token = self.git_config.get_git_token()
                clone_cmd = "git clone"
                
                # Check if shallow clone option exists (use checkbox from parent)
                # We'll keep it simple - no options for speed
                
                if 'https://' in repo_url and git_token:
                    repo_url_with_token = repo_url.replace('https://', f'https://{git_token}@')
                    clone_cmd += f' "{repo_url_with_token}" "{folder}"'
                else:
                    clone_cmd += f' "{repo_url}" "{folder}"'
                
                self.safe_update_ui(self.clone_status, text="Cloning...", text_color=COLORS['accent_orange'])
                self.clone_progress.set(0.3)
                self.output_text.insert("end", f"Command: {clone_cmd}\n\n")
                
                env = os.environ.copy()
                env['GIT_ASKPASS'] = 'echo'
                
                result = subprocess.run(
                    clone_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=env
                )
                
                self.clone_progress.set(0.8)
                
                if result.returncode == 0:
                    self.safe_update_ui(self.clone_status, text="Clone completed!", text_color=COLORS['accent_green'])
                    self.clone_progress.set(1.0)
                    self.output_text.insert("end", "\nSUCCESS: Repository cloned successfully!\n")
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
    """Window yo gushiraho Git name, email - Optimized"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.git_config = GitConfig()
        self.title("Git Setup")
        self.geometry("480x550")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_secondary'])
        
        self.setup_complete = False
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(15, 10), padx=20)
        
        ctk.CTkLabel(
            header,
            text="Git Setup",
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=f"OS: {OS_TYPE}",
            font=ctk.CTkFont(family="Roboto", size=10),
            text_color=COLORS['text_secondary']
        ).pack(side="right")
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=20, pady=5)
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Name
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
        
        # Email
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
        
        # SSH Key
        ctk.CTkLabel(
            content,
            text="SSH Key (auto-generated):",
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
        
        # Generate SSH button
        self.generate_ssh_btn = SmoothButton(
            content,
            text="Generate SSH Key",
            height=32,
            command=self.generate_ssh_key
        )
        self.generate_ssh_btn.pack(fill="x", pady=5)
        
        # Token
        ctk.CTkLabel(
            content,
            text="GitHub Token (optional):",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(10, 3))
        
        self.token_entry = ctk.CTkEntry(
            content,
            height=35,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="ghp_xxxxxxxxxxxxxxxxxxxx"
        )
        self.token_entry.pack(fill="x", pady=(0, 10))
        
        # Separator
        ctk.CTkFrame(content, height=1, fg_color=COLORS['border_light']).pack(fill="x", pady=10)
        
        # Save button
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
        if config.get('git_token'):
            self.token_entry.insert(0, config['git_token'])
        if config.get('ssh_key'):
            self.ssh_key = config['ssh_key']
            self.ssh_generated = True
            self.ssh_status_label.configure(text="SSH Key: Configured", text_color=COLORS['accent_green'])
            self.save_btn.configure(state="normal")
    
    def generate_ssh_key(self):
        self.generate_ssh_btn.configure(state="disabled", text="Generating...")
        self.ssh_status_label.configure(text="Generating SSH key...", text_color=COLORS['accent_orange'])
        
        def generate():
            try:
                ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
                if not os.path.exists(ssh_dir):
                    os.makedirs(ssh_dir, mode=0o700)
                
                key_path = os.path.join(ssh_dir, "id_rsa")
                
                if os.path.exists(key_path + ".pub"):
                    with open(f"{key_path}.pub", 'r') as f:
                        self.ssh_key = f.read().strip()
                    self.ssh_generated = True
                    self.ssh_status_label.configure(text="SSH Key: Already exists", text_color=COLORS['accent_green'])
                    self.save_btn.configure(state="normal")
                    self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
                    return
                
                email = self.email_entry.get().strip()
                if not email:
                    email = "user@example.com"
                
                cmd = f'ssh-keygen -t rsa -b 4096 -C "{email}" -f "{key_path}" -N ""'
                subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
                
                with open(f"{key_path}.pub", 'r') as f:
                    self.ssh_key = f.read().strip()
                
                self.ssh_generated = True
                self.ssh_status_label.configure(text="SSH Key: Generated!", text_color=COLORS['accent_green'])
                self.save_btn.configure(state="normal")
                
                self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
                
            except Exception as e:
                self.ssh_status_label.configure(text=f"Error: {str(e)[:30]}", text_color=COLORS['accent_red'])
                self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
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
        
        self.git_config.set_config(
            name,
            email,
            self.ssh_key,
            self.token_entry.get().strip()
        )
        
        self.setup_complete = True
        self.destroy()
        self.parent.show_push_window(name, email)

class GitPushWindow(ctk.CTkToplevel):
    """Window yo gukora Git Push - Optimized"""
    def __init__(self, parent, name, email):
        super().__init__(parent)
        
        self.parent = parent
        self.name = name
        self.email = email
        self.git_config = GitConfig()
        self.title("Git Push")
        self.geometry("600x500")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_secondary'])
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(15, 10), padx=20)
        
        ctk.CTkLabel(
            header,
            text="Git Push",
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=f"User: {name}",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        ).pack(side="right")
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=20, pady=5)
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Repository URL
        ctk.CTkLabel(
            content,
            text="Repository URL:",
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
        
        # Project folder
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
        
        # Options
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
        
        # Push button
        self.push_btn = SmoothButton(
            content,
            text="Push Now",
            height=42,
            fg_color=COLORS['accent_green'],
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            command=self.execute_push
        )
        self.push_btn.pack(fill="x", pady=10)
        
        # Progress
        self.push_progress = ctk.CTkProgressBar(
            content,
            height=6,
            corner_radius=3,
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['border_light']
        )
        self.push_progress.pack(fill="x", pady=5)
        self.push_progress.set(0)
        
        # Status
        self.push_status = ctk.CTkLabel(
            content,
            text="Ready to push",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        )
        self.push_status.pack(anchor="w", pady=3)
        
        # Output
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
            messagebox.showwarning("Missing URL", "Please enter repository URL")
            return
        
        if not folder:
            messagebox.showwarning("Missing Folder", "Please select project folder")
            return
        
        if not os.path.exists(folder):
            messagebox.showerror("Invalid Folder", "Selected folder does not exist")
            return
        
        self.push_btn.configure(state="disabled", text="Pushing...")
        self.safe_update_ui(self.push_status, text="Starting push...", text_color=COLORS['accent_orange'])
        self.push_progress.set(0.1)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "=== Git Push Started ===\n")
        self.output_text.insert("end", f"User: {self.name}\n")
        self.output_text.insert("end", f"Repo: {repo_url}\n")
        self.output_text.insert("end", "-" * 30 + "\n\n")
        
        def push():
            try:
                git_token = self.git_config.get_git_token()
                
                # Init if needed
                git_dir = os.path.join(folder, ".git")
                if not os.path.exists(git_dir):
                    self.safe_update_ui(self.push_status, text="Initializing...", text_color=COLORS['accent_orange'])
                    self.push_progress.set(0.2)
                    self.output_text.insert("end", "Initializing git...\n")
                    subprocess.run(f'cd "{folder}" && git init', shell=True, capture_output=True, check=True)
                
                # Config user (OS level already set, but set locally too)
                self.push_progress.set(0.3)
                subprocess.run(f'cd "{folder}" && git config user.name "{self.name}"', shell=True, capture_output=True)
                subprocess.run(f'cd "{folder}" && git config user.email "{self.email}"', shell=True, capture_output=True)
                
                # Add remote
                self.push_progress.set(0.4)
                self.output_text.insert("end", "Adding remote...\n")
                subprocess.run(f'cd "{folder}" && git remote remove origin', shell=True, capture_output=True)
                subprocess.run(f'cd "{folder}" && git remote add origin {repo_url}', shell=True, capture_output=True, check=True)
                
                # Add files
                self.push_progress.set(0.5)
                self.output_text.insert("end", "Adding files...\n")
                subprocess.run(f'cd "{folder}" && git add .', shell=True, capture_output=True, check=True)
                
                # Commit
                self.push_progress.set(0.6)
                self.output_text.insert("end", "Committing...\n")
                subprocess.run(f'cd "{folder}" && git commit -m "Initial commit"', shell=True, capture_output=True)
                
                # Push
                self.push_progress.set(0.7)
                self.output_text.insert("end", "Pushing...\n")
                
                env = os.environ.copy()
                env['GIT_ASKPASS'] = 'echo'
                
                push_cmd = "git push -u origin main"
                if self.force_push.get():
                    push_cmd = "git push -u origin main --force"
                elif self.accept_push.get():
                    push_cmd = "git push -u origin main --force-with-lease"
                
                if 'https://' in repo_url and git_token:
                    repo_url_with_token = repo_url.replace('https://', f'https://{git_token}@')
                    cmd = f'cd "{folder}" && git remote set-url origin {repo_url_with_token} && {push_cmd}'
                else:
                    cmd = f'cd "{folder}" && {push_cmd}'
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env=env
                )
                
                self.push_progress.set(0.9)
                
                if result.returncode == 0:
                    self.safe_update_ui(self.push_status, text="Push successful!", text_color=COLORS['accent_green'])
                    self.push_progress.set(1.0)
                    self.output_text.insert("end", "\nSUCCESS: Push completed!\n")
                    messagebox.showinfo("Success", "Git Push completed successfully!")
                else:
                    self.safe_update_ui(self.push_status, text="Push failed", text_color=COLORS['accent_red'])
                    self.push_progress.set(0)
                    self.output_text.insert("end", f"\nERROR: {result.stderr}\n")
                    messagebox.showerror("Push Failed", f"Push failed:\n{result.stderr[:200]}")
                
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.configure(state="disabled")
                
            except subprocess.TimeoutExpired:
                self.safe_update_ui(self.push_status, text="Timed out", text_color=COLORS['accent_red'])
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.insert("end", "\nERROR: Push timed out\n")
                self.output_text.configure(state="disabled")
                messagebox.showerror("Push Failed", "Push timed out")
                
            except Exception as e:
                self.safe_update_ui(self.push_status, text=f"Error: {str(e)[:40]}", text_color=COLORS['accent_red'])
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.insert("end", f"\nERROR: {str(e)}\n")
                self.output_text.configure(state="disabled")
                messagebox.showerror("Push Failed", f"Push failed:\n{str(e)}")
        
        thread = threading.Thread(target=push)
        thread.daemon = True
        thread.start()

class App(ctk.CTk):
    """Main App - Optimized for speed"""
    def __init__(self):
        super().__init__()
        
        self.title("Git & Download Panel Pro")
        self.geometry("900x700")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Variables
        self.animation_running = False
        self.update_available = False
        self.update_version = ""
        self.update_commit_message = ""
        self.original_bg_image = None
        self.git_setup_window = None
        self.git_push_window = None
        self.clone_window = None
        self.git_config = GitConfig()
        
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        
        # --- HEADER - Simplified ---
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent", height=50)
        self.header_frame.pack(fill="x", pady=(10, 0), padx=15)
        
        self.app_icon = ctk.CTkLabel(self.header_frame, text="", width=10, height=10, corner_radius=5, fg_color=COLORS['accent_blue'])
        self.app_icon.pack(side="left", padx=(0, 8))
        
        self.title_text = ctk.CTkLabel(
            self.header_frame,
            text="Git & Download Panel",
            font=ctk.CTkFont(family="Roboto", size=18, weight="bold"),
            text_color=COLORS['text_primary']
        )
        self.title_text.pack(side="left")
        
        # OS badge
        os_badge = ctk.CTkLabel(
            self.header_frame,
            text=OS_TYPE.upper(),
            font=ctk.CTkFont(family="Roboto", size=9, weight="bold"),
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['bg_secondary'],
            corner_radius=8,
            padx=8,
            pady=2
        )
        os_badge.pack(side="right", padx=(0, 5))
        
        self.version_badge = ctk.CTkLabel(
            self.header_frame,
            text="v2.0",
            font=ctk.CTkFont(family="Roboto", size=9, weight="normal"),
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['bg_secondary'],
            corner_radius=8,
            padx=8,
            pady=2
        )
        self.version_badge.pack(side="right", padx=(0, 5))
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.header_frame,
            text="[S]",
            width=30,
            height=28,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.toggle_settings
        )
        self.settings_btn.pack(side="right", padx=(0, 5))
        
        self.close_btn = ctk.CTkButton(
            self.header_frame,
            text="X",
            width=28,
            height=28,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.quit
        )
        self.close_btn.pack(side="right")
        
        # --- SETTINGS PANEL ---
        self.settings_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS['bg_secondary'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border_light']
        )
        self.settings_frame.pack(fill="x", padx=25, pady=(0, 10))
        self.settings_frame.pack_forget()
        
        # Settings header
        settings_header = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        settings_header.pack(fill="x", pady=(12, 5), padx=18)
        
        ctk.CTkLabel(
            settings_header,
            text="Settings",
            font=ctk.CTkFont(family="Roboto", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkButton(
            settings_header,
            text="X",
            width=25,
            height=25,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_settings
        ).pack(side="right")
        
        ctk.CTkFrame(self.settings_frame, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=18, pady=5)
        
        # Update section - Simplified
        update_section = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        update_section.pack(fill="x", padx=18, pady=8)
        
        ctk.CTkLabel(
            update_section,
            text="Update",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 3))
        
        self.update_status_label = ctk.CTkLabel(
            update_section,
            text="Checking for updates...",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        )
        self.update_status_label.pack(anchor="w")
        
        self.update_progress = ctk.CTkProgressBar(
            update_section,
            height=4,
            corner_radius=2,
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['border_light']
        )
        self.update_progress.pack(fill="x", pady=(5, 5))
        self.update_progress.set(0)
        
        self.restart_btn = ctk.CTkButton(
            update_section,
            text="Restart & Update",
            height=32,
            corner_radius=8,
            fg_color=COLORS['accent_green'],
            hover_color='#2a9d4d',
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            command=self.restart_app
        )
        self.restart_btn.pack(fill="x", pady=3)
        self.restart_btn.configure(state="disabled")
        
        ctk.CTkFrame(self.settings_frame, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=18, pady=5)
        
        # About section - Simplified
        about_section = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        about_section.pack(fill="x", padx=18, pady=8)
        
        ctk.CTkLabel(
            about_section,
            text="About",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 3))
        
        ctk.CTkLabel(
            about_section,
            text="Git & Download Panel Pro v2.0",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            about_section,
            text="Developer: Niyibizi Kevin",
            font=ctk.CTkFont(family="Roboto", size=11, weight="bold"),
            text_color=COLORS['accent_blue']
        ).pack(anchor="w")
        
        website_link = ctk.CTkLabel(
            about_section,
            text="niyibizi_kevin.netlify.app",
            font=ctk.CTkFont(family="Roboto", size=10),
            text_color=COLORS['accent_blue'],
            cursor="hand2"
        )
        website_link.pack(anchor="w")
        website_link.bind("<Button-1>", lambda e: self.open_website())
        
        # --- BACKGROUND ---
        self.bg_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bg_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        self.bg_image_label = ctk.CTkLabel(self.bg_frame, text="")
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Load background - only if exists
        bg_loaded = False
        try:
            if os.path.exists("app.jpeg"):
                self.original_bg_image = Image.open("app.jpeg").resize((870, 650), Image.Resampling.LANCZOS)
                self.bg_photo = ctk.CTkImage(light_image=self.original_bg_image, dark_image=self.original_bg_image, size=(870, 650))
                self.bg_image_label.configure(image=self.bg_photo)
                bg_loaded = True
        except:
            pass
        
        if not bg_loaded:
            self.bg_frame.configure(fg_color=COLORS['bg_primary'])
        
        def make_blur_crop(box):
            if not bg_loaded or self.original_bg_image is None:
                return None
            try:
                crop = self.original_bg_image.crop(box)
                blurred = crop.filter(ImageFilter.GaussianBlur(20))
                enhancer = ImageEnhance.Brightness(blurred)
                darkened = enhancer.enhance(0.5)
                return ctk.CTkImage(light_image=darkened, dark_image=darkened, size=(box[2]-box[0], box[3]-box[1]))
            except:
                return None
        
        # --- CARDS ---
        # Git Push Card
        self.git_blur_img = make_blur_crop((180, 180, 420, 560))
        self.git_card = ctk.CTkFrame(self.bg_frame, corner_radius=18, border_width=1, border_color=COLORS['border_light'], fg_color=COLORS['bg_secondary'])
        self.git_card.place(relx=0.33, rely=0.5, anchor="center", relwidth=0.28, relheight=0.50)
        
        ctk.CTkFrame(self.git_card, fg_color=COLORS['bg_secondary'], corner_radius=18).place(x=0, y=0, relwidth=1, relheight=1)
        
        # Git icon
        try:
            if os.path.exists("image_0.png"):
                git_pil = Image.open("image_0.png")
                git_photo = ctk.CTkImage(light_image=git_pil, dark_image=git_pil, size=(60, 60))
            else:
                git_photo = None
        except:
            git_photo = None
        
        git_content = ctk.CTkFrame(self.git_card, fg_color="transparent")
        git_content.place(relx=0.5, rely=0.5, anchor="center")
        
        if git_photo:
            ctk.CTkLabel(git_content, image=git_photo, text="").pack(pady=(0, 10))
        ctk.CTkLabel(git_content, text="Git Push", font=ctk.CTkFont(family="Roboto", size=16, weight="bold"), text_color=COLORS['text_primary']).pack(pady=(0, 3))
        ctk.CTkLabel(git_content, text="Push to remote", font=ctk.CTkFont(family="Roboto", size=11), text_color=COLORS['text_secondary']).pack(pady=(0, 15))
        SmoothButton(git_content, text="Execute Push", width=140, height=36, command=self.start_git_setup).pack(pady=(0, 10))
        
        # Clone Card
        self.clone_blur_img = make_blur_crop((440, 180, 680, 560))
        self.clone_card = ctk.CTkFrame(self.bg_frame, corner_radius=18, border_width=1, border_color=COLORS['border_light'], fg_color=COLORS['bg_secondary'])
        self.clone_card.place(relx=0.67, rely=0.5, anchor="center", relwidth=0.28, relheight=0.50)
        
        ctk.CTkFrame(self.clone_card, fg_color=COLORS['bg_secondary'], corner_radius=18).place(x=0, y=0, relwidth=1, relheight=1)
        
        # Clone icon
        try:
            if os.path.exists("download.png"):
                clone_pil = Image.open("download.png")
                clone_photo = ctk.CTkImage(light_image=clone_pil, dark_image=clone_pil, size=(60, 60))
            else:
                clone_photo = None
        except:
            clone_photo = None
        
        clone_content = ctk.CTkFrame(self.clone_card, fg_color="transparent")
        clone_content.place(relx=0.5, rely=0.5, anchor="center")
        
        if clone_photo:
            ctk.CTkLabel(clone_content, image=clone_photo, text="").pack(pady=(0, 10))
        else:
            ctk.CTkLabel(clone_content, text="[Clone]", font=ctk.CTkFont(family="Roboto", size=24, weight="bold"), text_color=COLORS['accent_blue']).pack(pady=(0, 10))
        
        ctk.CTkLabel(clone_content, text="Clone Repository", font=ctk.CTkFont(family="Roboto", size=16, weight="bold"), text_color=COLORS['text_primary']).pack(pady=(0, 3))
        ctk.CTkLabel(clone_content, text="Clone from remote", font=ctk.CTkFont(family="Roboto", size=11), text_color=COLORS['text_secondary']).pack(pady=(0, 15))
        SmoothButton(clone_content, text="Open Clone", width=140, height=36, fg_color=COLORS['accent_green'], command=self.start_clone).pack(pady=(0, 10))
        
        # --- STATUS BAR ---
        self.status_bar = ctk.CTkFrame(self.main_container, fg_color=COLORS['bg_secondary'], height=28, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_dot = ctk.CTkLabel(self.status_bar, text="*", font=ctk.CTkFont(family="Roboto", size=8), text_color=COLORS['accent_green'])
        self.status_dot.pack(side="left", padx=(15, 6))
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(family="Roboto", size=10), text_color=COLORS['text_secondary'])
        self.status_label.pack(side="left")
        
        self.shortcuts_label = ctk.CTkLabel(
            self.status_bar,
            text="Ctrl+G: Git | Ctrl+C: Clone | Ctrl+S: Settings",
            font=ctk.CTkFont(family="Roboto", size=9),
            text_color=COLORS['text_secondary']
        )
        self.shortcuts_label.pack(side="right", padx=15)
        
        # Shortcuts
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<Control-g>", lambda e: self.start_git_setup())
        self.bind("<Control-c>", lambda e: self.start_clone())
        self.bind("<Control-s>", lambda e: self.toggle_settings())
        
        # --- AUTO UPDATE ---
        self.after(1500, self.auto_check_update)
    
    def start_clone(self):
        if self.clone_window is None or not self.clone_window.winfo_exists():
            self.clone_window = CloneWindow(self)
            self.status_label.configure(text="Clone opened")
        else:
            self.clone_window.focus()
    
    def start_git_setup(self):
        try:
            subprocess.run("git --version", shell=True, capture_output=True, check=True)
        except:
            messagebox.showerror("Git Not Found", "Please install Git first.")
            return
        
        if self.git_config.is_configured():
            self.show_push_window(self.git_config.get_name(), self.git_config.get_email())
            return
        
        if self.git_setup_window is None or not self.git_setup_window.winfo_exists():
            self.git_setup_window = GitSetupWindow(self)
            self.status_label.configure(text="Git setup")
        else:
            self.git_setup_window.focus()
    
    def show_push_window(self, name, email):
        if self.git_push_window is None or not self.git_push_window.winfo_exists():
            self.git_push_window = GitPushWindow(self, name, email)
            self.status_label.configure(text="Git push")
        else:
            self.git_push_window.focus()
    
    def open_website(self):
        webbrowser.open("https://niyibizi_kevin.netlify.app")
        self.status_label.configure(text="Opening website...")
    
    def toggle_settings(self):
        if self.settings_frame.winfo_ismapped():
            self.settings_frame.pack_forget()
            self.geometry("900x700")
        else:
            self.settings_frame.pack(fill="x", padx=25, pady=(0, 10), before=self.bg_frame)
            self.geometry("900x760")
    
    def auto_check_update(self):
        self.update_status_label.configure(text="Checking for updates...")
        
        def check():
            try:
                response = requests.get(GITHUB_API_URL, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.update_available = True
                    self.update_version = data['sha'][:7]
                    self.update_commit_message = data['commit']['message']
                    self.update_status_label.configure(text=f"Update: {self.update_commit_message[:40]}...", text_color=COLORS['accent_blue'])
                    self.restart_btn.configure(state="normal")
                    self.download_update_auto()
                else:
                    self.update_status_label.configure(text="No updates", text_color=COLORS['accent_green'])
            except:
                self.update_status_label.configure(text="Update check failed", text_color=COLORS['accent_red'])
        
        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()
    
    def download_update_auto(self):
        def download():
            try:
                response = requests.get(GITHUB_ZIP_URL, stream=True, timeout=30)
                if response.status_code != 200:
                    return
                
                self.update_progress.set(0.3)
                temp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(temp_dir, "update.zip")
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.update_progress.set(0.6)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                extracted_dir = None
                for item in os.listdir(temp_dir):
                    if item.startswith('gitpushand-dawnlaods-main'):
                        extracted_dir = os.path.join(temp_dir, item)
                        break
                
                if extracted_dir:
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    main_file = os.path.join(extracted_dir, 'main.py')
                    if os.path.exists(main_file):
                        shutil.copy2(main_file, os.path.join(current_dir, 'main.py'))
                        for file in ['app.jpeg', 'image_0.png', 'download.png']:
                            src = os.path.join(extracted_dir, file)
                            if os.path.exists(src):
                                shutil.copy2(src, os.path.join(current_dir, file))
                
                shutil.rmtree(temp_dir)
                self.update_progress.set(1.0)
                self.update_status_label.configure(text="Update ready! Restart", text_color=COLORS['accent_green'])
                self.restart_btn.configure(state="normal")
                
            except:
                self.update_progress.set(0)
        
        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()
    
    def restart_app(self):
        if messagebox.askyesno("Restart", "Restart to apply update?"):
            python = sys.executable
            os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    app = App()
    app.mainloop()
