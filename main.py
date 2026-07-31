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
import re

# --- GIT UPDATE FUNCTIONS ---
GITHUB_REPO = "rwandaxcode/gitpushand-dawnlaods"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
GITHUB_ZIP_URL = f"https://github.com/{GITHUB_REPO}/archive/main.zip"

# Colors
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
    """Button isa na macOS/Deepin ihora smooth"""
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
    """Manage Git configuration inside app"""
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser("~"), ".gitpush_config.json")
        self.config = self.load_config()
    
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

class GitSetupWindow(ctk.CTkToplevel):
    """Window yo gushiraho Git name, email na SSH key - all inside app"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.git_config = GitConfig()
        self.title("Git Setup")
        self.geometry("550x700")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_secondary'])
        
        self.setup_complete = False
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=25)
        
        ctk.CTkLabel(
            header,
            text="Git Setup",
            font=ctk.CTkFont(family="Roboto", size=22, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text="Configure Git - All inside app",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(10, 0))
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=25, pady=10)
        
        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Step 1: Name and Email
        step1_label = ctk.CTkLabel(
            content,
            text="Step 1: Configure Git User",
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            text_color=COLORS['text_primary']
        )
        step1_label.pack(anchor="w", pady=(0, 10))
        
        # Name
        name_frame = ctk.CTkFrame(content, fg_color="transparent")
        name_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            name_frame,
            text="Name:",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary'],
            width=60
        ).pack(side="left")
        
        self.name_entry = ctk.CTkEntry(
            name_frame,
            height=35,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="Your full name"
        )
        self.name_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Email
        email_frame = ctk.CTkFrame(content, fg_color="transparent")
        email_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Email:",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary'],
            width=60
        ).pack(side="left")
        
        self.email_entry = ctk.CTkEntry(
            email_frame,
            height=35,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="your.email@example.com"
        )
        self.email_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # GitHub Token (optional but helps avoid terminal prompts)
        token_label = ctk.CTkLabel(
            content,
            text="GitHub Token (optional):",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        )
        token_label.pack(anchor="w", pady=(10, 5))
        
        token_desc = ctk.CTkLabel(
            content,
            text="Create token at: GitHub Settings > Developer settings > Personal access tokens",
            font=ctk.CTkFont(family="Roboto", size=10),
            text_color=COLORS['text_secondary'],
            wraplength=450
        )
        token_desc.pack(anchor="w", pady=(0, 5))
        
        self.token_entry = ctk.CTkEntry(
            content,
            height=35,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="ghp_xxxxxxxxxxxxxxxxxxxx"
        )
        self.token_entry.pack(fill="x", pady=(0, 15))
        
        # Step 2: SSH Key
        step2_label = ctk.CTkLabel(
            content,
            text="Step 2: SSH Key Setup (Inside App)",
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            text_color=COLORS['text_primary']
        )
        step2_label.pack(anchor="w", pady=(15, 10))
        
        # SSH key status
        self.ssh_status_frame = ctk.CTkFrame(content, fg_color=COLORS['bg_primary'], corner_radius=10)
        self.ssh_status_frame.pack(fill="x", pady=5)
        
        self.ssh_status_label = ctk.CTkLabel(
            self.ssh_status_frame,
            text="SSH Key: Not generated",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.ssh_status_label.pack(anchor="w", padx=15, pady=10)
        
        # SSH key display
        self.ssh_key_display = ctk.CTkTextbox(
            content,
            height=80,
            corner_radius=10,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(family="Roboto", size=10)
        )
        self.ssh_key_display.pack(fill="x", pady=5)
        self.ssh_key_display.insert("1.0", "SSH key will appear here after generation...")
        self.ssh_key_display.configure(state="disabled")
        
        # SSH key buttons
        ssh_buttons = ctk.CTkFrame(content, fg_color="transparent")
        ssh_buttons.pack(fill="x", pady=5)
        
        self.generate_ssh_btn = SmoothButton(
            ssh_buttons,
            text="Generate SSH Key",
            width=150,
            height=35,
            command=self.generate_ssh_key
        )
        self.generate_ssh_btn.pack(side="left", padx=(0, 10))
        
        self.copy_ssh_btn = SmoothButton(
            ssh_buttons,
            text="Copy SSH Key",
            width=120,
            height=35,
            fg_color=COLORS['accent_green'],
            command=self.copy_ssh_key
        )
        self.copy_ssh_btn.pack(side="left")
        self.copy_ssh_btn.configure(state="disabled")
        
        # SSH instructions
        self.ssh_instructions = ctk.CTkTextbox(
            content,
            height=80,
            corner_radius=10,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(family="Roboto", size=11)
        )
        self.ssh_instructions.pack(fill="x", pady=10)
        self.ssh_instructions.insert("1.0", "1. Generate SSH key above\n2. Copy the key\n3. Go to GitHub Settings > SSH and GPG keys\n4. Click 'New SSH Key' and paste")
        self.ssh_instructions.configure(state="disabled")
        
        # Step 3: Test Connection
        step3_label = ctk.CTkLabel(
            content,
            text="Step 3: Test Connection (Inside App)",
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            text_color=COLORS['text_primary']
        )
        step3_label.pack(anchor="w", pady=(15, 10))
        
        self.test_btn = SmoothButton(
            content,
            text="Test SSH Connection",
            width=180,
            height=35,
            fg_color=COLORS['accent_orange'],
            command=self.test_ssh_connection
        )
        self.test_btn.pack(side="left", pady=5)
        
        self.test_status = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.test_status.pack(side="left", padx=(15, 0), pady=5)
        
        # Separator
        ctk.CTkFrame(content, height=1, fg_color=COLORS['border_light']).pack(fill="x", pady=15)
        
        # Save & Next button
        self.next_btn = SmoothButton(
            content,
            text="Save & Next -> Push",
            height=40,
            fg_color=COLORS['accent_green'],
            command=self.next_step
        )
        self.next_btn.pack(fill="x", pady=10)
        self.next_btn.configure(state="disabled")
        
        # Store SSH key
        self.ssh_key = None
        self.ssh_generated = False
        
        # Load saved config
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
            self.ssh_status_label.configure(text="SSH Key: Already configured", text_color=COLORS['accent_green'])
            self.copy_ssh_btn.configure(state="normal")
            self.next_btn.configure(state="normal")
            self.ssh_key_display.configure(state="normal")
            self.ssh_key_display.delete("1.0", "end")
            self.ssh_key_display.insert("1.0", self.ssh_key)
            self.ssh_key_display.configure(state="disabled")
    
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
                    self.copy_ssh_btn.configure(state="normal")
                    self.next_btn.configure(state="normal")
                    
                    self.ssh_key_display.configure(state="normal")
                    self.ssh_key_display.delete("1.0", "end")
                    self.ssh_key_display.insert("1.0", self.ssh_key)
                    self.ssh_key_display.configure(state="disabled")
                    
                    self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
                    return
                
                email = self.email_entry.get().strip()
                if not email:
                    email = "user@example.com"
                
                cmd = f'ssh-keygen -t rsa -b 4096 -C "{email}" -f "{key_path}" -N ""'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
                
                with open(f"{key_path}.pub", 'r') as f:
                    self.ssh_key = f.read().strip()
                
                self.ssh_generated = True
                self.ssh_status_label.configure(text="SSH Key: Generated successfully!", text_color=COLORS['accent_green'])
                self.copy_ssh_btn.configure(state="normal")
                self.next_btn.configure(state="normal")
                
                self.ssh_key_display.configure(state="normal")
                self.ssh_key_display.delete("1.0", "end")
                self.ssh_key_display.insert("1.0", self.ssh_key)
                self.ssh_key_display.configure(state="disabled")
                
                self.save_config()
                
                self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
                
            except Exception as e:
                self.ssh_status_label.configure(text=f"Error: {str(e)}", text_color=COLORS['accent_red'])
                self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
                messagebox.showerror("SSH Error", f"Failed to generate SSH key:\n{str(e)}")
        
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
    
    def copy_ssh_key(self):
        if self.ssh_key:
            self.clipboard_clear()
            self.clipboard_append(self.ssh_key)
            self.ssh_status_label.configure(text="SSH Key: Copied to clipboard!", text_color=COLORS['accent_green'])
            messagebox.showinfo("Copied", "SSH key copied to clipboard!")
    
    def test_ssh_connection(self):
        self.test_btn.configure(state="disabled", text="Testing...")
        self.test_status.configure(text="Testing SSH connection...", text_color=COLORS['accent_orange'])
        
        def test():
            try:
                result = subprocess.run(
                    "ssh -T git@github.com -o StrictHostKeyChecking=no -o ConnectTimeout=10",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if "successfully authenticated" in result.stderr or "You've successfully authenticated" in result.stderr:
                    self.test_status.configure(text="SSH connection successful!", text_color=COLORS['accent_green'])
                    self.next_btn.configure(state="normal")
                else:
                    self.test_status.configure(text="SSH connection failed. Please add key to GitHub.", text_color=COLORS['accent_red'])
                    self.next_btn.configure(state="disabled")
                
                self.test_btn.configure(state="normal", text="Test SSH Connection")
                
            except subprocess.TimeoutExpired:
                self.test_status.configure(text="SSH connection timed out", text_color=COLORS['accent_red'])
                self.test_btn.configure(state="normal", text="Test SSH Connection")
            except Exception as e:
                self.test_status.configure(text=f"Error: {str(e)[:50]}", text_color=COLORS['accent_red'])
                self.test_btn.configure(state="normal", text="Test SSH Connection")
                messagebox.showerror("SSH Error", f"SSH connection failed:\n{str(e)}")
        
        thread = threading.Thread(target=test)
        thread.daemon = True
        thread.start()
    
    def save_config(self):
        self.git_config.set_config(
            self.name_entry.get().strip(),
            self.email_entry.get().strip(),
            self.ssh_key,
            self.token_entry.get().strip()
        )
    
    def next_step(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not name or not email:
            messagebox.showwarning("Missing Info", "Please enter your name and email")
            return
        
        if not self.ssh_generated:
            messagebox.showwarning("SSH Key", "Please generate SSH key first")
            return
        
        self.save_config()
        
        self.setup_complete = True
        self.destroy()
        
        self.parent.show_push_window(name, email)

class GitPushWindow(ctk.CTkToplevel):
    """Window yo gukora Git Push - all inside app"""
    def __init__(self, parent, name, email):
        super().__init__(parent)
        
        self.parent = parent
        self.name = name
        self.email = email
        self.git_config = GitConfig()
        self.title("Git Push")
        self.geometry("600x550")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_secondary'])
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=25)
        
        ctk.CTkLabel(
            header,
            text="Git Push",
            font=ctk.CTkFont(family="Roboto", size=22, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=f"User: {name}",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(side="right")
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=25, pady=10)
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Repository URL
        repo_label = ctk.CTkLabel(
            content,
            text="Repository URL:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        )
        repo_label.pack(anchor="w", pady=(0, 5))
        
        self.repo_entry = ctk.CTkEntry(
            content,
            height=40,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="git@github.com:username/repo.git OR https://github.com/username/repo.git"
        )
        self.repo_entry.pack(fill="x", pady=(0, 15))
        
        # Project folder
        folder_label = ctk.CTkLabel(
            content,
            text="Project Folder:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        )
        folder_label.pack(anchor="w", pady=(0, 5))
        
        folder_frame = ctk.CTkFrame(content, fg_color="transparent")
        folder_frame.pack(fill="x", pady=(0, 15))
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            height=40,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="/path/to/your/project"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = SmoothButton(
            folder_frame,
            text="Browse",
            width=80,
            height=35,
            command=self.browse_folder
        )
        self.browse_btn.pack(side="right")
        
        # Options
        options_frame = ctk.CTkFrame(content, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)
        
        self.force_push = ctk.CTkCheckBox(
            options_frame,
            text="Force Push (--force)",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['accent_blue']
        )
        self.force_push.pack(side="left", padx=(0, 20))
        
        self.accept_push = ctk.CTkCheckBox(
            options_frame,
            text="Accept Push (--force-with-lease)",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['accent_blue']
        )
        self.accept_push.pack(side="left")
        
        # Push button
        self.push_btn = SmoothButton(
            content,
            text="Push Now",
            height=45,
            fg_color=COLORS['accent_green'],
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            command=self.execute_push
        )
        self.push_btn.pack(fill="x", pady=15)
        
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
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.push_status.pack(anchor="w", pady=5)
        
        # Output
        self.output_text = ctk.CTkTextbox(
            content,
            height=120,
            corner_radius=10,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(family="Roboto", size=11)
        )
        self.output_text.pack(fill="both", pady=5)
        self.output_text.insert("1.0", "Git operations will appear here...")
        self.output_text.configure(state="disabled")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
    
    def safe_update_ui(self, widget, **kwargs):
        """Safely update UI from thread"""
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
        self.safe_update_ui(self.push_status, text="Initializing push...", text_color=COLORS['accent_orange'])
        self.push_progress.set(0.1)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "=== Git Push Started ===\n")
        self.output_text.insert("end", f"User: {self.name}\n")
        self.output_text.insert("end", f"Email: {self.email}\n")
        self.output_text.insert("end", f"Repository: {repo_url}\n")
        self.output_text.insert("end", f"Folder: {folder}\n")
        self.output_text.insert("end", "-" * 40 + "\n\n")
        
        def push():
            try:
                # Get git token if available
                git_token = self.git_config.get_git_token()
                
                # Step 1: Check if git is initialized
                git_dir = os.path.join(folder, ".git")
                if not os.path.exists(git_dir):
                    self.safe_update_ui(self.push_status, text="Initializing git repository...", text_color=COLORS['accent_orange'])
                    self.push_progress.set(0.2)
                    self.output_text.insert("end", "[1] Initializing git repository...\n")
                    
                    result = subprocess.run(f'cd "{folder}" && git init', shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.output_text.insert("end", "    Git repository initialized\n")
                    else:
                        self.output_text.insert("end", f"    Error: {result.stderr}\n")
                        raise Exception("Git init failed")
                
                # Step 2: Set user config
                self.safe_update_ui(self.push_status, text="Configuring user...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.3)
                self.output_text.insert("end", "[2] Configuring user...\n")
                
                subprocess.run(f'cd "{folder}" && git config user.name "{self.name}"', shell=True, capture_output=True)
                subprocess.run(f'cd "{folder}" && git config user.email "{self.email}"', shell=True, capture_output=True)
                self.output_text.insert("end", f"    User: {self.name} <{self.email}>\n")
                
                # Step 3: Add remote
                self.safe_update_ui(self.push_status, text="Adding remote...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.4)
                self.output_text.insert("end", "[3] Adding remote...\n")
                
                subprocess.run(f'cd "{folder}" && git remote remove origin', shell=True, capture_output=True)
                result = subprocess.run(f'cd "{folder}" && git remote add origin {repo_url}', shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.output_text.insert("end", f"    Remote added: {repo_url}\n")
                else:
                    self.output_text.insert("end", f"    Error: {result.stderr}\n")
                    raise Exception("Remote add failed")
                
                # Step 4: Add all files
                self.safe_update_ui(self.push_status, text="Adding files...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.5)
                self.output_text.insert("end", "[4] Adding files...\n")
                
                result = subprocess.run(f'cd "{folder}" && git add .', shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.output_text.insert("end", "    Files added\n")
                else:
                    self.output_text.insert("end", f"    Error: {result.stderr}\n")
                    raise Exception("Git add failed")
                
                # Step 5: Commit
                self.safe_update_ui(self.push_status, text="Committing...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.6)
                self.output_text.insert("end", "[5] Creating commit...\n")
                
                result = subprocess.run(f'cd "{folder}" && git commit -m "Initial commit"', shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.output_text.insert("end", "    Commit created\n")
                else:
                    self.output_text.insert("end", f"    Note: {result.stderr}\n")
                
                # Step 6: Push - Use SSH or HTTPS with token
                self.safe_update_ui(self.push_status, text="Pushing to GitHub...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.7)
                self.output_text.insert("end", "[6] Pushing to GitHub...\n")
                
                # Prepare environment to avoid terminal prompts
                env = os.environ.copy()
                env['GIT_ASKPASS'] = 'echo'
                env['GIT_AUTHOR_NAME'] = self.name
                env['GIT_AUTHOR_EMAIL'] = self.email
                env['GIT_COMMITTER_NAME'] = self.name
                env['GIT_COMMITTER_EMAIL'] = self.email
                
                # If using HTTPS and token provided, inject credentials
                if 'https://' in repo_url and git_token:
                    # Modify URL to include token
                    repo_url_with_token = repo_url.replace('https://', f'https://{git_token}@')
                    push_cmd = f"git push -u origin main"
                    if self.force_push.get():
                        push_cmd = f"git push -u origin main --force"
                    elif self.accept_push.get():
                        push_cmd = f"git push -u origin main --force-with-lease"
                    
                    # Use the URL with token for push
                    cmd = f'cd "{folder}" && git remote set-url origin {repo_url_with_token} && {push_cmd}'
                    self.output_text.insert("end", f"    Using HTTPS with token\n")
                else:
                    # Use SSH (no token needed)
                    push_cmd = "git push -u origin main"
                    if self.force_push.get():
                        push_cmd = "git push -u origin main --force"
                        self.output_text.insert("end", "    Using --force\n")
                    elif self.accept_push.get():
                        push_cmd = "git push -u origin main --force-with-lease"
                        self.output_text.insert("end", "    Using --force-with-lease\n")
                    else:
                        self.output_text.insert("end", "    Using normal push (SSH)\n")
                    
                    cmd = f'cd "{folder}" && {push_cmd}'
                
                self.output_text.insert("end", f"    Command: {push_cmd}\n")
                
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
                    self.safe_update_ui(self.push_status, text="Push completed successfully!", text_color=COLORS['accent_green'])
                    self.push_progress.set(1.0)
                    self.output_text.insert("end", "\n" + "=" * 40 + "\n")
                    self.output_text.insert("end", "SUCCESS: Push completed successfully!\n")
                    if result.stdout:
                        self.output_text.insert("end", result.stdout)
                    messagebox.showinfo("Success", "Git Push completed successfully!")
                else:
                    self.safe_update_ui(self.push_status, text="Push failed", text_color=COLORS['accent_red'])
                    self.push_progress.set(0)
                    self.output_text.insert("end", "\n" + "=" * 40 + "\n")
                    self.output_text.insert("end", "ERROR: Push failed!\n")
                    self.output_text.insert("end", result.stderr)
                    messagebox.showerror("Push Failed", f"Push failed:\n{result.stderr[:200]}")
                
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.configure(state="disabled")
                
            except subprocess.TimeoutExpired:
                self.safe_update_ui(self.push_status, text="Push timed out", text_color=COLORS['accent_red'])
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.insert("end", "\nERROR: Push timed out\n")
                self.output_text.configure(state="disabled")
                messagebox.showerror("Push Failed", "Push timed out")
                
            except Exception as e:
                self.safe_update_ui(self.push_status, text=f"Error: {str(e)[:50]}", text_color=COLORS['accent_red'])
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.insert("end", f"\nERROR: {str(e)}\n")
                self.output_text.configure(state="disabled")
                messagebox.showerror("Push Failed", f"Push failed:\n{str(e)}")
        
        thread = threading.Thread(target=push)
        thread.daemon = True
        thread.start()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Git & Download Panel Pro")
        self.geometry("900x750")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Variables
        self.current_status = "Ready"
        self.animation_running = False
        self.update_available = False
        self.update_version = ""
        self.update_commit_message = ""
        self.update_ready = False
        self.original_bg_image = None
        self.git_setup_window = None
        self.git_push_window = None
        self.git_config = GitConfig()
        
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        
        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent", height=60)
        self.header_frame.pack(fill="x", pady=(15, 0), padx=20)
        
        self.app_icon = ctk.CTkLabel(self.header_frame, text="", width=12, height=12, corner_radius=6, fg_color=COLORS['accent_blue'])
        self.app_icon.pack(side="left", padx=(0, 10))
        
        self.title_text = ctk.CTkLabel(
            self.header_frame,
            text="Git & Download Panel Pro",
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
            text_color=COLORS['text_primary']
        )
        self.title_text.pack(side="left", expand=True)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.header_frame,
            text="Settings",
            width=80,
            height=36,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_settings
        )
        self.settings_btn.pack(side="right", padx=(0, 8))
        
        self.close_btn = ctk.CTkButton(
            self.header_frame,
            text="X",
            width=30,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.quit
        )
        self.close_btn.pack(side="right", padx=(0, 0))
        
        self.version_badge = ctk.CTkLabel(
            self.header_frame,
            text="v2.0",
            font=ctk.CTkFont(family="Roboto", size=10, weight="normal"),
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['bg_secondary'],
            corner_radius=8,
            padx=8,
            pady=2
        )
        self.version_badge.pack(side="right", padx=(0, 10))
        
        # --- SETTINGS PANEL ---
        self.settings_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS['bg_secondary'],
            corner_radius=20,
            border_width=1,
            border_color=COLORS['border_light']
        )
        self.settings_frame.pack(fill="x", padx=30, pady=(0, 15))
        self.settings_frame.pack_forget()
        
        # Settings header
        settings_header = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        settings_header.pack(fill="x", pady=(20, 10), padx=25)
        
        ctk.CTkLabel(
            settings_header,
            text="Settings",
            font=ctk.CTkFont(family="Roboto", size=22, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkButton(
            settings_header,
            text="X",
            width=30,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.toggle_settings
        ).pack(side="right")
        
        # Separator
        ctk.CTkFrame(self.settings_frame, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=25, pady=5)
        
        # --- UPDATE SECTION ---
        update_section = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        update_section.pack(fill="x", padx=25, pady=15)
        
        update_header = ctk.CTkFrame(update_section, fg_color="transparent")
        update_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            update_header,
            text="Update Application",
            font=ctk.CTkFont(family="Roboto", size=17, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # Update status card
        status_card = ctk.CTkFrame(update_section, fg_color=COLORS['bg_primary'], corner_radius=14)
        status_card.pack(fill="x", pady=5)
        
        status_row = ctk.CTkFrame(status_card, fg_color="transparent")
        status_row.pack(fill="x", padx=18, pady=12)
        
        self.update_status_icon = ctk.CTkLabel(
            status_row,
            text="[i]",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            text_color=COLORS['accent_orange']
        )
        self.update_status_icon.pack(side="left", padx=(0, 12))
        
        status_text_frame = ctk.CTkFrame(status_row, fg_color="transparent")
        status_text_frame.pack(side="left", fill="x", expand=True)
        
        self.update_status_title = ctk.CTkLabel(
            status_text_frame,
            text="Checking for updates...",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        )
        self.update_status_title.pack(anchor="w")
        
        self.update_status_desc = ctk.CTkLabel(
            status_text_frame,
            text="Please wait while we check for the latest version",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.update_status_desc.pack(anchor="w")
        
        # Commit message card
        self.commit_card = ctk.CTkFrame(status_card, fg_color=COLORS['bg_secondary'], corner_radius=10)
        self.commit_card.pack(fill="x", padx=18, pady=(0, 10))
        self.commit_card.pack_forget()
        
        commit_header = ctk.CTkFrame(self.commit_card, fg_color="transparent")
        commit_header.pack(fill="x", padx=12, pady=8)
        
        ctk.CTkLabel(
            commit_header,
            text="[Message]",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            commit_header,
            text="Update Reason",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        self.commit_message_label = ctk.CTkLabel(
            self.commit_card,
            text="",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_primary'],
            wraplength=400
        )
        self.commit_message_label.pack(anchor="w", padx=18, pady=(0, 8))
        
        # Progress bar
        self.update_progress = ctk.CTkProgressBar(
            update_section,
            height=8,
            corner_radius=4,
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['border_light']
        )
        self.update_progress.pack(pady=(10, 15), fill="x")
        self.update_progress.set(0)
        
        # Restart button
        self.restart_btn = ctk.CTkButton(
            update_section,
            text="Restart & Update",
            height=48,
            corner_radius=14,
            fg_color=COLORS['accent_green'],
            hover_color='#2a9d4d',
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            command=self.restart_app
        )
        self.restart_btn.pack(fill="x", pady=5)
        self.restart_btn.configure(state="disabled")
        
        # Separator
        ctk.CTkFrame(self.settings_frame, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=25, pady=5)
        
        # --- ABOUT SECTION ---
        about_section = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        about_section.pack(fill="x", padx=25, pady=15)
        
        about_header = ctk.CTkFrame(about_section, fg_color="transparent")
        about_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            about_header,
            text="About",
            font=ctk.CTkFont(family="Roboto", size=17, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        about_card = ctk.CTkFrame(about_section, fg_color=COLORS['bg_primary'], corner_radius=14)
        about_card.pack(fill="x", pady=5)
        
        about_content = ctk.CTkFrame(about_card, fg_color="transparent")
        about_content.pack(fill="x", padx=18, pady=12)
        
        ctk.CTkLabel(
            about_content,
            text="Git & Download Panel Pro",
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            about_content,
            text="Version 2.0.0",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        ctk.CTkFrame(about_content, height=1, fg_color=COLORS['border_light']).pack(fill="x", pady=8)
        
        # Developer
        dev_frame = ctk.CTkFrame(about_content, fg_color="transparent")
        dev_frame.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            dev_frame,
            text="Developer: Niyibizi Kevin",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['accent_blue']
        ).pack(anchor="w")
        
        # Website
        website_frame = ctk.CTkFrame(about_content, fg_color="transparent")
        website_frame.pack(fill="x", pady=3)
        
        website_link = ctk.CTkLabel(
            website_frame,
            text="niyibizi_kevin.netlify.app",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['accent_blue'],
            cursor="hand2"
        )
        website_link.pack(side="left")
        website_link.bind("<Button-1>", lambda e: self.open_website())
        
        # Year
        year_frame = ctk.CTkFrame(about_content, fg_color="transparent")
        year_frame.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            year_frame,
            text="2024",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        # --- BACKGROUND IMAGE ---
        self.bg_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bg_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.bg_image_label = ctk.CTkLabel(self.bg_frame, text="")
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Load background
        bg_loaded = False
        try:
            if os.path.exists("app.jpeg"):
                self.original_bg_image = Image.open("app.jpeg").resize((860, 700), Image.Resampling.LANCZOS)
                self.bg_photo = ctk.CTkImage(light_image=self.original_bg_image, dark_image=self.original_bg_image, size=(860, 700))
                self.bg_image_label.configure(image=self.bg_photo)
                bg_loaded = True
        except:
            pass
        
        if not bg_loaded:
            self.original_bg_image = Image.new("RGB", (860, 700), color=COLORS['bg_primary'])
            self.bg_frame.configure(fg_color=COLORS['bg_primary'])
        
        def make_blur_crop(box):
            if self.original_bg_image is None:
                return None
            try:
                crop = self.original_bg_image.crop(box)
                blurred = crop.filter(ImageFilter.GaussianBlur(25))
                enhancer = ImageEnhance.Brightness(blurred)
                darkened = enhancer.enhance(0.4)
                return ctk.CTkImage(light_image=darkened, dark_image=darkened, size=(box[2]-box[0], box[3]-box[1]))
            except:
                return None
        
        # --- CARDS ---
        # Git Card
        self.git_blur_img = make_blur_crop((170, 180, 430, 580))
        self.git_card = ctk.CTkFrame(self.bg_frame, corner_radius=20, border_width=1, border_color=COLORS['border_light'], fg_color=COLORS['bg_secondary'])
        self.git_card.place(relx=0.32, rely=0.5, anchor="center", relwidth=0.30, relheight=0.55)
        
        ctk.CTkFrame(self.git_card, fg_color=COLORS['bg_secondary'], corner_radius=20).place(x=0, y=0, relwidth=1, relheight=1)
        
        try:
            if os.path.exists("image_0.png"):
                git_pil = Image.open("image_0.png")
                self.git_photo = ctk.CTkImage(light_image=git_pil, dark_image=git_pil, size=(80, 80))
            else:
                self.git_photo = None
        except:
            self.git_photo = None
        
        self.git_content = ctk.CTkFrame(self.git_card, fg_color="transparent")
        self.git_content.place(relx=0.5, rely=0.5, anchor="center")
        
        if self.git_photo:
            ctk.CTkLabel(self.git_content, image=self.git_photo, text="").pack(pady=(0, 15))
        ctk.CTkLabel(self.git_content, text="Git Push", font=ctk.CTkFont(family="Roboto", size=18, weight="bold"), text_color=COLORS['text_primary']).pack(pady=(0, 5))
        ctk.CTkLabel(self.git_content, text="Push changes to remote repository", font=ctk.CTkFont(family="Roboto", size=12), text_color=COLORS['text_secondary']).pack(pady=(0, 20))
        SmoothButton(self.git_content, text="Execute Push", width=160, height=40, command=self.start_git_setup).pack(pady=(0, 15))
        self.git_progress = ctk.CTkProgressBar(self.git_content, width=160, height=4, corner_radius=2, progress_color=COLORS['accent_blue'], fg_color=COLORS['border_light'])
        self.git_progress.pack()
        self.git_progress.set(0)
        
        # Download Card - Removed, now only Git Push
        # Status bar moved to bottom
        
        # --- STATUS BAR ---
        self.status_bar = ctk.CTkFrame(self.main_container, fg_color=COLORS['bg_secondary'], height=35, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_dot = ctk.CTkLabel(self.status_bar, text="*", font=ctk.CTkFont(family="Roboto", size=10), text_color=COLORS['accent_green'])
        self.status_dot.pack(side="left", padx=(20, 8))
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(family="Roboto", size=12), text_color=COLORS['text_secondary'])
        self.status_label.pack(side="left")
        
        self.shortcuts_label = ctk.CTkLabel(
            self.status_bar,
            text="Ctrl+G: Git | Ctrl+S: Settings",
            font=ctk.CTkFont(family="Roboto", size=10),
            text_color=COLORS['text_secondary']
        )
        self.shortcuts_label.pack(side="right", padx=20)
        
        # Shortcuts
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<Control-g>", lambda e: self.start_git_setup())
        self.bind("<Control-s>", lambda e: self.toggle_settings())
        
        # --- AUTO UPDATE ON START ---
        self.after(1500, self.auto_check_update)
    
    def start_git_setup(self):
        # Check if git is installed
        try:
            subprocess.run("git --version", shell=True, capture_output=True, check=True)
        except:
            messagebox.showerror("Git Not Found", "Git is not installed. Please install Git first.")
            return
        
        # Check if already configured
        if self.git_config.is_configured():
            self.show_push_window(self.git_config.get_name(), self.git_config.get_email())
            return
        
        # Open setup window
        if self.git_setup_window is None or not self.git_setup_window.winfo_exists():
            self.git_setup_window = GitSetupWindow(self)
            self.status_label.configure(text="Git setup started")
        else:
            self.git_setup_window.focus()
    
    def show_push_window(self, name, email):
        if self.git_push_window is None or not self.git_push_window.winfo_exists():
            self.git_push_window = GitPushWindow(self, name, email)
            self.status_label.configure(text="Git push window opened")
        else:
            self.git_push_window.focus()
    
    def open_website(self):
        webbrowser.open("https://niyibizi_kevin.netlify.app")
        self.status_label.configure(text="Opening developer website...")
    
    def toggle_settings(self):
        if self.settings_frame.winfo_ismapped():
            self.settings_frame.pack_forget()
            self.status_label.configure(text="Settings closed")
            self.geometry("900x750")
        else:
            self.settings_frame.pack(fill="x", padx=30, pady=(0, 15), before=self.bg_frame)
            self.status_label.configure(text="Settings opened")
            self.geometry("900x880")
    
    def show_commit_message(self, message):
        self.commit_card.pack(fill="x", padx=18, pady=(0, 10))
        self.commit_message_label.configure(text=message)
    
    def hide_commit_message(self):
        self.commit_card.pack_forget()
    
    def update_ui_status(self, icon, title, desc, progress, color=COLORS['accent_orange']):
        self.update_status_icon.configure(text=icon, text_color=color)
        self.update_status_title.configure(text=title)
        self.update_status_desc.configure(text=desc)
        self.update_progress.set(progress)
    
    def auto_check_update(self):
        self.update_ui_status("[i]", "Checking for updates...", "Please wait while we check for the latest version", 0.1)
        self.status_label.configure(text="Checking for updates...")
        self.hide_commit_message()
        
        def check():
            try:
                response = requests.get(GITHUB_API_URL, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.update_available = True
                    self.update_version = data['sha'][:7]
                    self.update_commit_message = data['commit']['message']
                    
                    self.show_commit_message(self.update_commit_message)
                    self.update_ui_status("[!]", "Update available!", "Downloading update automatically...", 0.2, COLORS['accent_blue'])
                    self.download_update_auto()
                else:
                    self.update_ui_status("[OK]", "No updates available", "You are using the latest version", 1.0, COLORS['accent_green'])
                    self.status_label.configure(text="Ready - Latest version")
                    self.restart_btn.configure(state="disabled")
                    self.hide_commit_message()
                    
            except Exception as e:
                self.update_ui_status("[X]", "Could not check updates", "Check your internet connection", 0, COLORS['accent_red'])
                self.status_label.configure(text="Ready - Update check failed")
                self.hide_commit_message()
        
        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()
    
    def download_update_auto(self):
        def download():
            try:
                response = requests.get(GITHUB_ZIP_URL, stream=True, timeout=30)
                if response.status_code != 200:
                    raise Exception("Failed to download update")
                
                self.update_ui_status("[D]", "Downloading update...", "Please wait while we download the latest version", 0.3)
                
                temp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(temp_dir, "update.zip")
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = 0.3 + (0.4 * (downloaded / total_size))
                            self.update_progress.set(progress)
                
                self.update_ui_status("[E]", "Extracting files...", "Preparing update for installation", 0.7)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                extracted_dir = None
                for item in os.listdir(temp_dir):
                    if item.startswith('gitpushand-dawnlaods-main'):
                        extracted_dir = os.path.join(temp_dir, item)
                        break
                
                if not extracted_dir:
                    raise Exception("Could not find extracted files")
                
                current_dir = os.path.dirname(os.path.abspath(__file__))
                
                main_file = os.path.join(extracted_dir, 'main.py')
                if os.path.exists(main_file):
                    backup_path = os.path.join(current_dir, 'main_backup.py')
                    shutil.copy2(os.path.join(current_dir, 'main.py'), backup_path)
                    shutil.copy2(main_file, os.path.join(current_dir, 'main.py'))
                    
                    for file in ['app.jpeg', 'image_0.png']:
                        src = os.path.join(extracted_dir, file)
                        if os.path.exists(src):
                            shutil.copy2(src, os.path.join(current_dir, file))
                
                shutil.rmtree(temp_dir)
                
                self.update_ui_status("[OK]", "Update ready!", f"Version {self.update_version} is ready to install", 1.0, COLORS['accent_green'])
                self.status_label.configure(text="Update ready! Restart to apply")
                self.restart_btn.configure(state="normal")
                
            except Exception as e:
                self.update_ui_status("[X]", "Update failed", f"Error: {str(e)[:50]}", 0, COLORS['accent_red'])
                self.status_label.configure(text="Update failed")
                self.hide_commit_message()
        
        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()
    
    def restart_app(self):
        if messagebox.askyesno("Restart", "Restart app to apply update?"):
            python = sys.executable
            os.execl(python, python, *sys.argv)
    
    def animate_progress(self, progress_bar, target, duration=1000):
        if self.animation_running:
            return
        self.animation_running = True
        steps = 50
        current = progress_bar.get()
        step_size = (target - current) / steps
        def update_step(step):
            nonlocal current
            if step < steps:
                current += step_size
                progress_bar.set(current)
                self.after(duration // steps, lambda: update_step(step + 1))
            else:
                progress_bar.set(target)
                self.animation_running = False
        update_step(0)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    app = App()
    app.mainloop()
