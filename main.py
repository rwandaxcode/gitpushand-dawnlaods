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

class GitSetupWindow(ctk.CTkToplevel):
    """Window yo gushiraho Git name, email na SSH key"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
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
            text="Configure Git before pushing",
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
        
        # Step 2: SSH Key
        step2_label = ctk.CTkLabel(
            content,
            text="Step 2: SSH Key Setup",
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
            height=100,
            corner_radius=10,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(family="Roboto", size=11)
        )
        self.ssh_instructions.pack(fill="x", pady=10)
        self.ssh_instructions.insert("1.0", "Generate SSH key first, then copy it and add to GitHub:\n\n1. Go to GitHub Settings > SSH and GPG keys\n2. Click 'New SSH Key'\n3. Paste the key and save")
        self.ssh_instructions.configure(state="disabled")
        
        # Step 3: Test Connection
        step3_label = ctk.CTkLabel(
            content,
            text="Step 3: Test Connection",
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
        
        # Next button
        self.next_btn = SmoothButton(
            content,
            text="Next -> Push",
            height=40,
            fg_color=COLORS['accent_green'],
            command=self.next_step
        )
        self.next_btn.pack(fill="x", pady=10)
        self.next_btn.configure(state="disabled")
        
        # Store SSH key
        self.ssh_key = None
        self.ssh_generated = False
        
        # Load saved config if exists
        self.load_saved_config()
    
    def load_saved_config(self):
        """Load saved git config if exists"""
        config_file = os.path.join(os.path.expanduser("~"), ".gitpush_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('name'):
                        self.name_entry.insert(0, config['name'])
                    if config.get('email'):
                        self.email_entry.insert(0, config['email'])
                    if config.get('ssh_key'):
                        self.ssh_key = config['ssh_key']
                        self.ssh_generated = True
                        self.ssh_status_label.configure(text="SSH Key: Already configured", text_color=COLORS['accent_green'])
                        self.copy_ssh_btn.configure(state="normal")
                        self.next_btn.configure(state="normal")
            except:
                pass
    
    def generate_ssh_key(self):
        """Generate SSH key"""
        self.generate_ssh_btn.configure(state="disabled", text="Generating...")
        self.ssh_status_label.configure(text="Generating SSH key...", text_color=COLORS['accent_orange'])
        
        def generate():
            try:
                ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
                if not os.path.exists(ssh_dir):
                    os.makedirs(ssh_dir, mode=0o700)
                
                key_path = os.path.join(ssh_dir, "id_rsa")
                
                # Check if key exists
                if os.path.exists(key_path):
                    # Read existing key
                    with open(f"{key_path}.pub", 'r') as f:
                        self.ssh_key = f.read().strip()
                    self.ssh_generated = True
                    self.ssh_status_label.configure(text="SSH Key: Already exists", text_color=COLORS['accent_green'])
                    self.copy_ssh_btn.configure(state="normal")
                    self.next_btn.configure(state="normal")
                    
                    # Show instructions
                    self.show_ssh_instructions()
                    
                    self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
                    return
                
                # Generate new key
                email = self.email_entry.get().strip()
                if not email:
                    email = "user@example.com"
                
                cmd = f'ssh-keygen -t rsa -b 4096 -C "{email}" -f "{key_path}" -N ""'
                subprocess.run(cmd, shell=True, check=True)
                
                # Read the public key
                with open(f"{key_path}.pub", 'r') as f:
                    self.ssh_key = f.read().strip()
                
                self.ssh_generated = True
                self.ssh_status_label.configure(text="SSH Key: Generated successfully!", text_color=COLORS['accent_green'])
                self.copy_ssh_btn.configure(state="normal")
                self.next_btn.configure(state="normal")
                
                # Show instructions
                self.show_ssh_instructions()
                
                # Save config
                self.save_config()
                
                self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
                
            except Exception as e:
                self.ssh_status_label.configure(text=f"Error: {str(e)}", text_color=COLORS['accent_red'])
                self.generate_ssh_btn.configure(state="normal", text="Generate SSH Key")
        
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
    
    def show_ssh_instructions(self):
        """Show SSH instructions"""
        self.ssh_instructions.configure(state="normal")
        self.ssh_instructions.delete("1.0", "end")
        instructions = """To add SSH key to GitHub:

1. Copy the SSH key using the "Copy SSH Key" button
2. Go to GitHub Settings > SSH and GPG keys
3. Click "New SSH Key"
4. Paste the key and save

Your key fingerprint will be checked automatically."""
        self.ssh_instructions.insert("1.0", instructions)
        self.ssh_instructions.configure(state="disabled")
    
    def copy_ssh_key(self):
        """Copy SSH key to clipboard"""
        if self.ssh_key:
            self.clipboard_clear()
            self.clipboard_append(self.ssh_key)
            self.ssh_status_label.configure(text="SSH Key: Copied to clipboard!", text_color=COLORS['accent_green'])
            messagebox.showinfo("Copied", "SSH key copied to clipboard!")
    
    def test_ssh_connection(self):
        """Test SSH connection to GitHub"""
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
        
        thread = threading.Thread(target=test)
        thread.daemon = True
        thread.start()
    
    def save_config(self):
        """Save config for future use"""
        config = {
            'name': self.name_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'ssh_key': self.ssh_key
        }
        config_file = os.path.join(os.path.expanduser("~"), ".gitpush_config.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def next_step(self):
        """Go to push step"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not name or not email:
            messagebox.showwarning("Missing Info", "Please enter your name and email")
            return
        
        if not self.ssh_generated:
            messagebox.showwarning("SSH Key", "Please generate SSH key first")
            return
        
        # Save config
        self.save_config()
        
        self.setup_complete = True
        self.destroy()
        
        # Open push window
        self.parent.show_push_window(name, email)

class GitPushWindow(ctk.CTkToplevel):
    """Window yo gukora Git Push"""
    def __init__(self, parent, name, email):
        super().__init__(parent)
        
        self.parent = parent
        self.name = name
        self.email = email
        self.title("Git Push")
        self.geometry("600x500")
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
            placeholder_text="git@github.com:username/repo.git"
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
            height=100,
            corner_radius=10,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(family="Roboto", size=11)
        )
        self.output_text.pack(fill="both", pady=5)
        self.output_text.insert("1.0", "Output will appear here...")
        self.output_text.configure(state="disabled")
    
    def browse_folder(self):
        """Browse for folder"""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
    
    def execute_push(self):
        """Execute git push"""
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
        self.push_status.configure(text="Initializing push...", text_color=COLORS['accent_orange'])
        self.push_progress.set(0.1)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        
        def push():
            try:
                # Step 1: Check if git is initialized
                git_dir = os.path.join(folder, ".git")
                if not os.path.exists(git_dir):
                    self.push_status.configure(text="Initializing git repository...", text_color=COLORS['accent_orange'])
                    self.push_progress.set(0.2)
                    self.output_text.insert("end", "Initializing git repository...\n")
                    
                    subprocess.run(f'cd "{folder}" && git init', shell=True, check=True, capture_output=True)
                    self.output_text.insert("end", "Git repository initialized\n")
                
                # Step 2: Set user config
                self.push_status.configure(text="Configuring user...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.3)
                
                subprocess.run(f'cd "{folder}" && git config user.name "{self.name}"', shell=True, check=True)
                subprocess.run(f'cd "{folder}" && git config user.email "{self.email}"', shell=True, check=True)
                self.output_text.insert("end", f"User: {self.name} <{self.email}>\n")
                
                # Step 3: Add remote
                self.push_status.configure(text="Adding remote...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.4)
                
                # Remove existing remote if any
                subprocess.run(f'cd "{folder}" && git remote remove origin', shell=True, capture_output=True)
                subprocess.run(f'cd "{folder}" && git remote add origin {repo_url}', shell=True, check=True)
                self.output_text.insert("end", f"Remote added: {repo_url}\n")
                
                # Step 4: Add all files
                self.push_status.configure(text="Adding files...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.5)
                subprocess.run(f'cd "{folder}" && git add .', shell=True, check=True)
                self.output_text.insert("end", "Files added\n")
                
                # Step 5: Commit
                self.push_status.configure(text="Committing...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.6)
                subprocess.run(f'cd "{folder}" && git commit -m "Initial commit"', shell=True, capture_output=True)
                self.output_text.insert("end", "Commit created\n")
                
                # Step 6: Push
                self.push_status.configure(text="Pushing to GitHub...", text_color=COLORS['accent_orange'])
                self.push_progress.set(0.7)
                
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
                    timeout=120
                )
                
                self.push_progress.set(0.9)
                
                if result.returncode == 0:
                    self.push_status.configure(text="Push completed successfully!", text_color=COLORS['accent_green'])
                    self.push_progress.set(1.0)
                    self.output_text.insert("end", "\n--- Push successful! ---\n")
                    self.output_text.insert("end", result.stdout)
                    messagebox.showinfo("Success", "Git Push completed successfully!")
                else:
                    self.push_status.configure(text="Push failed", text_color=COLORS['accent_red'])
                    self.push_progress.set(0)
                    self.output_text.insert("end", "\n--- Push failed! ---\n")
                    self.output_text.insert("end", result.stderr)
                    messagebox.showerror("Push Failed", f"Push failed:\n{result.stderr[:200]}")
                
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.configure(state="disabled")
                
            except subprocess.TimeoutExpired:
                self.push_status.configure(text="Push timed out", text_color=COLORS['accent_red'])
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.insert("end", "\nPush timed out\n")
                self.output_text.configure(state="disabled")
                
            except Exception as e:
                self.push_status.configure(text=f"Error: {str(e)[:50]}", text_color=COLORS['accent_red'])
                self.push_btn.configure(state="normal", text="Push Now")
                self.output_text.insert("end", f"\nError: {str(e)}\n")
                self.output_text.configure(state="disabled")
        
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
        
        status
