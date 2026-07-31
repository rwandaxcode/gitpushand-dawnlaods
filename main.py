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
from urllib.parse import urlparse

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

class DownloadWindow(ctk.CTkToplevel):
    """Window yo gukurura website, repo, cyangwa YouTube video"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.title("Download")
        self.geometry("650x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_secondary'])
        
        # Variables
        self.download_type = "website"  # website, repo, youtube
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=25)
        
        ctk.CTkLabel(
            header,
            text="Download",
            font=ctk.CTkFont(family="Roboto", size=22, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text="Download website, repo or YouTube video",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(10, 0))
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=25, pady=10)
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Download type selection
        type_label = ctk.CTkLabel(
            content,
            text="Select download type:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        )
        type_label.pack(anchor="w", pady=(0, 10))
        
        type_frame = ctk.CTkFrame(content, fg_color="transparent")
        type_frame.pack(fill="x", pady=(0, 15))
        
        # Website button
        self.website_btn = ctk.CTkButton(
            type_frame,
            text="Website",
            width=120,
            height=35,
            corner_radius=8,
            fg_color=COLORS['accent_blue'],
            hover_color='#0a7eff',
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            command=lambda: self.set_download_type("website")
        )
        self.website_btn.pack(side="left", padx=(0, 10))
        
        # Repo button
        self.repo_btn = ctk.CTkButton(
            type_frame,
            text="Repository",
            width=120,
            height=35,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            hover_color=COLORS['bg_primary'],
            font=ctk.CTkFont(family="Roboto", size=12),
            command=lambda: self.set_download_type("repo")
        )
        self.repo_btn.pack(side="left", padx=(0, 10))
        
        # YouTube button
        self.youtube_btn = ctk.CTkButton(
            type_frame,
            text="YouTube Video",
            width=120,
            height=35,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            hover_color=COLORS['bg_primary'],
            font=ctk.CTkFont(family="Roboto", size=12),
            command=lambda: self.set_download_type("youtube")
        )
        self.youtube_btn.pack(side="left")
        
        # Separator
        ctk.CTkFrame(content, height=1, fg_color=COLORS['border_light']).pack(fill="x", pady=10)
        
        # URL input
        url_label = ctk.CTkLabel(
            content,
            text="URL:",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        )
        url_label.pack(anchor="w", pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(
            content,
            height=40,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            placeholder_text="https://example.com or https://github.com/user/repo or https://youtube.com/watch?v=xxx"
        )
        self.url_entry.pack(fill="x", pady=(0, 15))
        
        # Folder selection
        folder_label = ctk.CTkLabel(
            content,
            text="Save to:",
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
            placeholder_text="/path/to/save"
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
        
        # Download button
        self.download_btn = SmoothButton(
            content,
            text="Download",
            height=45,
            fg_color=COLORS['accent_green'],
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            command=self.execute_download
        )
        self.download_btn.pack(fill="x", pady=15)
        
        # Progress
        self.download_progress = ctk.CTkProgressBar(
            content,
            height=6,
            corner_radius=3,
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['border_light']
        )
        self.download_progress.pack(fill="x", pady=5)
        self.download_progress.set(0)
        
        # Status
        self.download_status = ctk.CTkLabel(
            content,
            text="Ready to download",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.download_status.pack(anchor="w", pady=5)
        
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
        self.output_text.insert("1.0", "Output will appear here...")
        self.output_text.configure(state="disabled")
        
        # Set default download type
        self.set_download_type("website")
    
    def set_download_type(self, type_name):
        """Change download type"""
        self.download_type = type_name
        
        # Reset all buttons
        for btn in [self.website_btn, self.repo_btn, self.youtube_btn]:
            btn.configure(
                fg_color=COLORS['bg_primary'],
                text_color=COLORS['text_secondary'],
                font=ctk.CTkFont(family="Roboto", size=12)
            )
        
        # Highlight selected
        if type_name == "website":
            self.website_btn.configure(fg_color=COLORS['accent_blue'], text_color=COLORS['text_primary'], font=ctk.CTkFont(family="Roboto", size=12, weight="bold"))
            self.url_entry.configure(placeholder_text="https://example.com")
            self.download_status.configure(text="Enter website URL to download")
        elif type_name == "repo":
            self.repo_btn.configure(fg_color=COLORS['accent_blue'], text_color=COLORS['text_primary'], font=ctk.CTkFont(family="Roboto", size=12, weight="bold"))
            self.url_entry.configure(placeholder_text="https://github.com/username/repository")
            self.download_status.configure(text="Enter repository URL to clone")
        elif type_name == "youtube":
            self.youtube_btn.configure(fg_color=COLORS['accent_blue'], text_color=COLORS['text_primary'], font=ctk.CTkFont(family="Roboto", size=12, weight="bold"))
            self.url_entry.configure(placeholder_text="https://youtube.com/watch?v=xxx or https://youtu.be/xxx")
            self.download_status.configure(text="Enter YouTube video URL to download")
    
    def browse_folder(self):
        """Browse for folder"""
        folder = filedialog.askdirectory(title="Select save folder")
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
    
    def execute_download(self):
        """Execute download based on type"""
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a URL")
            return
        
        if not folder:
            messagebox.showwarning("Missing Folder", "Please select save folder")
            return
        
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except:
                messagebox.showerror("Invalid Folder", "Could not create folder")
                return
        
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.download_status.configure(text="Starting download...", text_color=COLORS['accent_orange'])
        self.download_progress.set(0.1)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        
        # Start download in thread
        if self.download_type == "website":
            thread = threading.Thread(target=self.download_website, args=(url, folder))
        elif self.download_type == "repo":
            thread = threading.Thread(target=self.download_repo, args=(url, folder))
        elif self.download_type == "youtube":
            thread = threading.Thread(target=self.download_youtube, args=(url, folder))
        else:
            thread = threading.Thread(target=self.download_website, args=(url, folder))
        
        thread.daemon = True
        thread.start()
    
    def download_website(self, url, folder):
        """Download website using wget or httrack"""
        try:
            self.output_text.insert("end", f"Downloading website: {url}\n")
            self.output_text.insert("end", f"Save to: {folder}\n\n")
            self.download_status.configure(text="Downloading website...", text_color=COLORS['accent_orange'])
            self.download_progress.set(0.2)
            
            # Try using wget first
            try:
                self.output_text.insert("end", "Using wget to download...\n")
                cmd = f'wget -r -l 5 -np -k -P "{folder}" "{url}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.download_status.configure(text="Website downloaded successfully!", text_color=COLORS['accent_green'])
                    self.download_progress.set(1.0)
                    self.output_text.insert("end", "\n--- Download complete! ---\n")
                    self.output_text.insert("end", f"Website saved to: {folder}\n")
                    messagebox.showinfo("Success", "Website downloaded successfully!")
                else:
                    raise Exception("wget failed")
                    
            except:
                # Fallback to simple download using requests
                self.output_text.insert("end", "wget not available, using requests...\n")
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    # Save HTML
                    html_file = os.path.join(folder, "index.html")
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    self.download_status.configure(text="Website downloaded successfully!", text_color=COLORS['accent_green'])
                    self.download_progress.set(1.0)
                    self.output_text.insert("end", "\n--- Download complete! ---\n")
                    self.output_text.insert("end", f"Website saved to: {html_file}\n")
                    messagebox.showinfo("Success", "Website downloaded successfully!")
                else:
                    raise Exception(f"Failed to download: {response.status_code}")
            
        except Exception as e:
            self.download_status.configure(text=f"Error: {str(e)[:50]}", text_color=COLORS['accent_red'])
            self.download_progress.set(0)
            self.output_text.insert("end", f"\nError: {str(e)}\n")
            messagebox.showerror("Download Failed", f"Failed to download website:\n{str(e)}")
        
        self.download_btn.configure(state="normal", text="Download")
        self.output_text.configure(state="disabled")
    
    def download_repo(self, url, folder):
        """Download repository using git clone"""
        try:
            self.output_text.insert("end", f"Cloning repository: {url}\n")
            self.output_text.insert("end", f"Save to: {folder}\n\n")
            self.download_status.configure(text="Cloning repository...", text_color=COLORS['accent_orange'])
            self.download_progress.set(0.2)
            
            # Check if git is installed
            try:
                subprocess.run("git --version", shell=True, capture_output=True, check=True)
            except:
                # Fallback to download zip from GitHub
                self.output_text.insert("end", "Git not found, downloading zip from GitHub...\n")
                self.download_github_zip(url, folder)
                return
            
            # Extract repo name from URL
            repo_name = url.rstrip('/').split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            
            repo_path = os.path.join(folder, repo_name)
            
            cmd = f'git clone "{url}" "{repo_path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.download_status.configure(text="Repository cloned successfully!", text_color=COLORS['accent_green'])
                self.download_progress.set(1.0)
                self.output_text.insert("end", "\n--- Clone complete! ---\n")
                self.output_text.insert("end", f"Repository saved to: {repo_path}\n")
                messagebox.showinfo("Success", "Repository cloned successfully!")
            else:
                # Try to download zip as fallback
                self.output_text.insert("end", "Git clone failed, trying zip download...\n")
                self.download_github_zip(url, folder)
            
        except Exception as e:
            self.download_status.configure(text=f"Error: {str(e)[:50]}", text_color=COLORS['accent_red'])
            self.download_progress.set(0)
            self.output_text.insert("end", f"\nError: {str(e)}\n")
            messagebox.showerror("Download Failed", f"Failed to clone repository:\n{str(e)}")
        
        self.download_btn.configure(state="normal", text="Download")
        self.output_text.configure(state="disabled")
    
    def download_github_zip(self, url, folder):
        """Download GitHub repo as zip"""
        try:
            self.output_text.insert("end", "Downloading zip from GitHub...\n")
            self.download_progress.set(0.3)
            
            # Convert github.com URL to zip URL
            # https://github.com/username/repo -> https://github.com/username/repo/archive/main.zip
            if 'github.com' in url:
                parts = url.rstrip('/').split('/')
                if len(parts) >= 5:
                    username = parts[-2]
                    repo = parts[-1]
                    if repo.endswith('.git'):
                        repo = repo[:-4]
                    zip_url = f"https://github.com/{username}/{repo}/archive/main.zip"
                    
                    self.output_text.insert("end", f"Downloading: {zip_url}\n")
                    
                    response = requests.get(zip_url, stream=True, timeout=60)
                    if response.status_code == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded = 0
                        
                        # Save zip
                        zip_path = os.path.join(folder, f"{repo}.zip")
                        with open(zip_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress = 0.3 + (0.5 * (downloaded / total_size))
                                    self.download_progress.set(progress)
                        
                        # Extract zip
                        self.output_text.insert("end", "Extracting files...\n")
                        self.download_progress.set(0.8)
                        
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(folder)
                        
                        os.remove(zip_path)
                        
                        self.download_status.configure(text="Repository downloaded successfully!", text_color=COLORS['accent_green'])
                        self.download_progress.set(1.0)
                        self.output_text.insert("end", "\n--- Download complete! ---\n")
                        self.output_text.insert("end", f"Repository saved to: {folder}\n")
                        messagebox.showinfo("Success", "Repository downloaded successfully!")
                    else:
                        raise Exception(f"Failed to download: {response.status_code}")
                else:
                    raise Exception("Invalid GitHub URL")
            else:
                raise Exception("Not a GitHub URL")
                
        except Exception as e:
            self.download_status.configure(text=f"Error: {str(e)[:50]}", text_color=COLORS['accent_red'])
            self.download_progress.set(0)
            self.output_text.insert("end", f"\nError: {str(e)}\n")
            messagebox.showerror("Download Failed", f"Failed to download repository:\n{str(e)}")
            raise
    
    def download_youtube(self, url, folder):
        """Download YouTube video"""
        try:
            self.output_text.insert("end", f"Downloading YouTube video: {url}\n")
            self.output_text.insert("end", f"Save to: {folder}\n\n")
            self.download_status.configure(text="Downloading YouTube video...", text_color=COLORS['accent_orange'])
            self.download_progress.set(0.1)
            
            # Try using yt-dlp (recommended)
            try:
                self.output_text.insert("end", "Using yt-dlp to download...\n")
                
                # Check if yt-dlp is installed
                try:
                    subprocess.run("yt-dlp --version", shell=True, capture_output=True, check=True)
                except:
                    self.output_text.insert("end", "yt-dlp not found, trying youtube-dl...\n")
                    try:
                        subprocess.run("youtube-dl --version", shell=True, capture_output=True, check=True)
                        downloader = "youtube-dl"
                    except:
                        raise Exception("Neither yt-dlp nor youtube-dl found. Please install: pip install yt-dlp")
                else:
                    downloader = "yt-dlp"
                
                self.output_text.insert("end", f"Using {downloader}\n")
                
                # Download video
                cmd = f'{downloader} -f bestvideo+bestaudio --merge-output-format mp4 -o "{folder}/%(title)s.%(ext)s" "{url}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    self.download_status.configure(text="YouTube video downloaded successfully!", text_color=COLORS['accent_green'])
                    self.download_progress.set(1.0)
                    self.output_text.insert("end", "\n--- Download complete! ---\n")
                    self.output_text.insert("end", f"Video saved to: {folder}\n")
                    messagebox.showinfo("Success", "YouTube video downloaded successfully!")
                else:
                    self.output_text.insert("end", f"Error: {result.stderr}\n")
                    raise Exception(f"{downloader} failed")
                    
            except Exception as e:
                # Fallback: Show instructions
                self.output_text.insert("end", f"\nError: {str(e)}\n")
                self.output_text.insert("end", "\nPlease install yt-dlp:\n")
                self.output_text.insert("end", "  pip install yt-dlp\n\n")
                self.output_text.insert("end", "Or use an online YouTube downloader.\n")
                self.download_status.configure(text="yt-dlp not installed", text_color=COLORS['accent_red'])
                self.download_progress.set(0)
                messagebox.showerror("Download Failed", f"Failed to download YouTube video:\n{str(e)}\n\nPlease install: pip install yt-dlp")
            
        except Exception as e:
            self.download_status.configure(text=f"Error: {str(e)[:50]}", text_color=COLORS['accent_red'])
            self.download_progress.set(0)
            self.output_text.insert("end", f"\nError: {str(e)}\n")
            messagebox.showerror("Download Failed", f"Failed to download YouTube video:\n{str(e)}")
        
        self.download_btn.configure(state="normal", text="Download")
        self.output_text.configure(state="disabled")

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
                if os.path.exists(key_path + ".pub"):
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
        self.download_window = None
        
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
        
        # Download Card
        self.download_blur_img = make_blur_crop((430, 180, 690, 580))
        self.download_card = ctk.CTkFrame(self.bg_frame, corner_radius=20, border_width=1, border_color=COLORS['border_light'], fg_color=COLORS['bg_secondary'])
        self.download_card.place(relx=0.68, rely=0.5, anchor="center", relwidth=0.30, relheight=0.55)
        
        ctk.CTkFrame(self.download_card, fg_color=COLORS['bg_secondary'], corner_radius=20).place(x=0, y=0, relwidth=1, relheight=1)
        
        try:
            if os.path.exists("ytb.png"):
                download_pil = Image.open("ytb.png")
                self.download_photo = ctk.CTkImage(light_image=download_pil, dark_image=download_pil, size=(80, 80))
            else:
                self.download_photo = None
        except:
            self.download_photo = None
        
        self.download_content = ctk.CTkFrame(self.download_card, fg_color="transparent")
        self.download_content.place(relx=0.5, rely=0.5, anchor="center")
        
        if self.download_photo:
            ctk.CTkLabel(self.download_content, image=self.download_photo, text="").pack(pady=(0, 15))
        ctk.CTkLabel(self.download_content, text="Download", font=ctk.CTkFont(family="Roboto", size=18, weight="bold"), text_color=COLORS['text_primary']).pack(pady=(0, 5))
        ctk.CTkLabel(self.download_content, text="Download website, repo or YouTube", font=ctk.CTkFont(family="Roboto", size=12), text_color=COLORS['text_secondary']).pack(pady=(0, 20))
        SmoothButton(self.download_content, text="Start Download", width=160, height=40, fg_color=COLORS['accent_green'], command=self.start_download).pack(pady=(0, 15))
        self.download_progress = ctk.CTkProgressBar(self.download_content, width=160, height=4, corner_radius=2, progress_color=COLORS['accent_green'], fg_color=COLORS['border_light'])
        self.download_progress.pack()
        self.download_progress.set(0)
        
        # --- STATUS BAR ---
        self.status_bar = ctk.CTkFrame(self.main_container, fg_color=COLORS['bg_secondary'], height=35, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_dot = ctk.CTkLabel(self.status_bar, text="*", font=ctk.CTkFont(family="Roboto", size=10), text_color=COLORS['accent_green'])
        self.status_dot.pack(side="left", padx=(20, 8))
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(family="Roboto", size=12), text_color=COLORS['text_secondary'])
        self.status_label.pack(side="left")
        
        self.shortcuts_label = ctk.CTkLabel(
            self.status_bar,
            text="Ctrl+G: Git | Ctrl+D: Download | Ctrl+S: Settings",
            font=ctk.CTkFont(family="Roboto", size=10),
            text_color=COLORS['text_secondary']
        )
        self.shortcuts_label.pack(side="right", padx=20)
        
        # Shortcuts
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<Control-g>", lambda e: self.start_git_setup())
        self.bind("<Control-d>", lambda e: self.start_download())
        self.bind("<Control-s>", lambda e: self.toggle_settings())
        
        # --- AUTO UPDATE ON START ---
        self.after(1500, self.auto_check_update)
    
    def start_download(self):
        """Open download window"""
        if self.download_window is None or not self.download_window.winfo_exists():
            self.download_window = DownloadWindow(self)
            self.status_label.configure(text="Download window opened")
        else:
            self.download_window.focus()
    
    def start_git_setup(self):
        """Start Git setup process"""
        # Check if git is installed
        try:
            subprocess.run("git --version", shell=True, capture_output=True, check=True)
        except:
            messagebox.showerror("Git Not Found", "Git is not installed. Please install Git first.")
            return
        
        # Check if setup already done
        config_file = os.path.join(os.path.expanduser("~"), ".gitpush_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('name') and config.get('email') and config.get('ssh_key'):
                        # Setup already done, go directly to push
                        self.show_push_window(config['name'], config['email'])
                        return
            except:
                pass
        
        # Open setup window
        if self.git_setup_window is None or not self.git_setup_window.winfo_exists():
            self.git_setup_window = GitSetupWindow(self)
            self.status_label.configure(text="Git setup started")
        else:
            self.git_setup_window.focus()
    
    def show_push_window(self, name, email):
        """Show push window"""
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
                    
                    for file in ['app.jpeg', 'image_0.png', 'ytb.png']:
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
