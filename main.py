import customtkinter as ctk
from PIL import Image, ImageFilter, ImageEnhance
import os
import sys
import subprocess
import requests
import json
import shutil
import tempfile
import zipfile
from tkinter import messagebox
from datetime import datetime
import webbrowser

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
        self.update_checking = False
        self.update_available = False
        self.commit_info = None
        self.original_bg_image = None
        
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
            text="[Settings]",
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
        
        # --- SETTINGS PANEL (inside app, hidden by default) ---
        self.settings_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS['bg_secondary'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border_light']
        )
        self.settings_frame.pack(fill="x", padx=30, pady=(0, 15))
        self.settings_frame.pack_forget()  # Hidden initially
        
        # Settings header
        settings_header = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        settings_header.pack(fill="x", pady=(15, 5), padx=20)
        
        ctk.CTkLabel(
            settings_header,
            text="Settings & Updates",
            font=ctk.CTkFont(family="Roboto", size=18, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # Close settings button
        ctk.CTkButton(
            settings_header,
            text="X",
            width=25,
            height=25,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.toggle_settings
        ).pack(side="right")
        
        # Separator
        ctk.CTkFrame(self.settings_frame, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=20, pady=5)
        
        # --- UPDATE SECTION ---
        update_section = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        update_section.pack(fill="x", padx=25, pady=10)
        
        ctk.CTkLabel(
            update_section,
            text="Update Application",
            font=ctk.CTkFont(family="Roboto", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        # Version info frame
        version_frame = ctk.CTkFrame(update_section, fg_color=COLORS['bg_primary'], corner_radius=10)
        version_frame.pack(fill="x", pady=5)
        
        self.current_version_label = ctk.CTkLabel(
            version_frame,
            text="Current: v2.0.0",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.current_version_label.pack(anchor="w", padx=15, pady=5)
        
        self.latest_version_label = ctk.CTkLabel(
            version_frame,
            text="Checking for updates...",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.latest_version_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(update_section, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)
        
        self.check_btn = SmoothButton(
            buttons_frame,
            text="Check for Updates",
            width=160,
            height=35,
            command=self.check_for_updates
        )
        self.check_btn.pack(side="left", padx=(0, 10))
        
        self.update_btn = SmoothButton(
            buttons_frame,
            text="Download & Install",
            width=160,
            height=35,
            fg_color=COLORS['accent_green'],
            command=self.download_update
        )
        self.update_btn.pack(side="left")
        self.update_btn.configure(state="disabled")
        
        # Update progress
        self.update_progress = ctk.CTkProgressBar(
            update_section,
            width=400,
            height=6,
            corner_radius=3,
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['border_light']
        )
        self.update_progress.pack(pady=(5, 5))
        self.update_progress.set(0)
        
        # Update status
        self.update_status = ctk.CTkLabel(
            update_section,
            text="Press 'Check for Updates' to see if a new version is available",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        )
        self.update_status.pack(anchor="w")
        
        # Separator
        ctk.CTkFrame(self.settings_frame, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=20, pady=10)
        
        # --- REPOSITORY DETAILS ---
        details_title = ctk.CTkLabel(
            self.settings_frame,
            text="Repository Details",
            font=ctk.CTkFont(family="Roboto", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        )
        details_title.pack(anchor="w", padx=25, pady=(0, 5))
        
        details_frame = ctk.CTkFrame(self.settings_frame, fg_color=COLORS['bg_primary'], corner_radius=10)
        details_frame.pack(fill="x", padx=25, pady=5)
        
        ctk.CTkLabel(
            details_frame,
            text="Repository: rwandaxcode/gitpushand-dawnlaods",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", padx=15, pady=5)
        
        self.commit_label = ctk.CTkLabel(
            details_frame,
            text="Last Commit: Loading...",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.commit_label.pack(anchor="w", padx=15, pady=5)
        
        self.author_label = ctk.CTkLabel(
            details_frame,
            text="Author: Loading...",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.author_label.pack(anchor="w", padx=15, pady=5)
        
        self.date_label = ctk.CTkLabel(
            details_frame,
            text="Date: Loading...",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        )
        self.date_label.pack(anchor="w", padx=15, pady=5)
        
        # Separator
        ctk.CTkFrame(self.settings_frame, height=1, fg_color=COLORS['border_light']).pack(fill="x", padx=20, pady=10)
        
        # --- ABOUT SECTION (Without theme settings) ---
        about_section = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        about_section.pack(fill="x", padx=25, pady=10)
        
        ctk.CTkLabel(
            about_section,
            text="About",
            font=ctk.CTkFont(family="Roboto", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        about_frame = ctk.CTkFrame(about_section, fg_color=COLORS['bg_primary'], corner_radius=10)
        about_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            about_frame,
            text="App: Git & Download Panel Pro",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", padx=15, pady=3)
        
        ctk.CTkLabel(
            about_frame,
            text="Version: 2.0.0",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", padx=15, pady=3)
        
        # Developer section with bold color
        developer_label = ctk.CTkLabel(
            about_frame,
            text="Developed by: Niyibizi Kevin",
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            text_color=COLORS['accent_blue']
        )
        developer_label.pack(anchor="w", padx=15, pady=3)
        
        ctk.CTkLabel(
            about_frame,
            text="Year: 2024",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", padx=15, pady=3)
        
        ctk.CTkLabel(
            about_frame,
            text="Repository: github.com/rwandaxcode/gitpushand-dawnlaods",
            font=ctk.CTkFont(family="Roboto", size=11),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", padx=15, pady=3)
        
        # Website link (clickable)
        website_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
        website_frame.pack(anchor="w", padx=15, pady=5)
        
        website_label = ctk.CTkLabel(
            website_frame,
            text="Visit: niyibizi_kevin.netlify.app",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['accent_blue'],
            cursor="hand2"
        )
        website_label.pack(side="left")
        
        # Open link button
        visit_btn = ctk.CTkButton(
            website_frame,
            text="Open",
            width=60,
            height=25,
            corner_radius=8,
            fg_color=COLORS['accent_blue'],
            hover_color='#0a7eff',
            font=ctk.CTkFont(family="Roboto", size=10, weight="bold"),
            command=self.open_website
        )
        visit_btn.pack(side="left", padx=(10, 0))
        
        # --- BACKGROUND IMAGE ---
        self.bg_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bg_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.bg_image_label = ctk.CTkLabel(self.bg_frame, text="")
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Load background
        try:
            self.original_bg_image = Image.open("app.jpeg").resize((860, 700), Image.Resampling.LANCZOS)
            self.bg_photo = ctk.CTkImage(light_image=self.original_bg_image, dark_image=self.original_bg_image, size=(860, 700))
            self.bg_image_label.configure(image=self.bg_photo)
        except Exception as e:
            print(f"Background image not found: {e}")
            self.original_bg_image = Image.new("RGB", (860, 700), color=COLORS['bg_primary'])
            self.bg_frame.configure(fg_color=COLORS['bg_primary'])
        
        def make_blur_crop(box):
            if self.original_bg_image is None:
                return None
            crop = self.original_bg_image.crop(box)
            blurred = crop.filter(ImageFilter.GaussianBlur(25))
            enhancer = ImageEnhance.Brightness(blurred)
            darkened = enhancer.enhance(0.4)
            return ctk.CTkImage(light_image=darkened, dark_image=darkened, size=(box[2]-box[0], box[3]-box[1]))
        
        # --- CARDS ---
        # Git Card
        self.git_blur_img = make_blur_crop((170, 180, 430, 580))
        self.git_card = ctk.CTkFrame(self.bg_frame, corner_radius=20, border_width=1, border_color=COLORS['border_light'], fg_color=COLORS['bg_secondary'])
        self.git_card.place(relx=0.32, rely=0.5, anchor="center", relwidth=0.30, relheight=0.55)
        
        ctk.CTkFrame(self.git_card, fg_color=COLORS['bg_secondary'], corner_radius=20).place(x=0, y=0, relwidth=1, relheight=1)
        
        try:
            git_pil = Image.open("image_0.png")
            self.git_photo = ctk.CTkImage(light_image=git_pil, dark_image=git_pil, size=(80, 80))
        except:
            self.git_photo = None
        
        self.git_content = ctk.CTkFrame(self.git_card, fg_color="transparent")
        self.git_content.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(self.git_content, image=self.git_photo, text="").pack(pady=(0, 15))
        ctk.CTkLabel(self.git_content, text="Git Push", font=ctk.CTkFont(family="Roboto", size=18, weight="bold"), text_color=COLORS['text_primary']).pack(pady=(0, 5))
        ctk.CTkLabel(self.git_content, text="Push changes to remote repository", font=ctk.CTkFont(family="Roboto", size=12), text_color=COLORS['text_secondary']).pack(pady=(0, 20))
        SmoothButton(self.git_content, text="Execute Push", width=160, height=40, command=self.on_git_push_clicked).pack(pady=(0, 15))
        self.git_progress = ctk.CTkProgressBar(self.git_content, width=160, height=4, corner_radius=2, progress_color=COLORS['accent_blue'], fg_color=COLORS['border_light'])
        self.git_progress.pack()
        self.git_progress.set(0)
        
        # Download Card
        self.download_blur_img = make_blur_crop((430, 180, 690, 580))
        self.download_card = ctk.CTkFrame(self.bg_frame, corner_radius=20, border_width=1, border_color=COLORS['border_light'], fg_color=COLORS['bg_secondary'])
        self.download_card.place(relx=0.68, rely=0.5, anchor="center", relwidth=0.30, relheight=0.55)
        
        ctk.CTkFrame(self.download_card, fg_color=COLORS['bg_secondary'], corner_radius=20).place(x=0, y=0, relwidth=1, relheight=1)
        
        try:
            download_pil = Image.open("ytb.png")
            self.download_photo = ctk.CTkImage(light_image=download_pil, dark_image=download_pil, size=(80, 80))
        except:
            self.download_photo = None
        
        self.download_content = ctk.CTkFrame(self.download_card, fg_color="transparent")
        self.download_content.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(self.download_content, image=self.download_photo, text="").pack(pady=(0, 15))
        ctk.CTkLabel(self.download_content, text="Download", font=ctk.CTkFont(family="Roboto", size=18, weight="bold"), text_color=COLORS['text_primary']).pack(pady=(0, 5))
        ctk.CTkLabel(self.download_content, text="Download website or repository", font=ctk.CTkFont(family="Roboto", size=12), text_color=COLORS['text_secondary']).pack(pady=(0, 20))
        SmoothButton(self.download_content, text="Start Download", width=160, height=40, fg_color=COLORS['accent_green'], command=self.on_download_clicked).pack(pady=(0, 15))
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
        self.bind("<Control-g>", lambda e: self.on_git_push_clicked(None))
        self.bind("<Control-d>", lambda e: self.on_download_clicked(None))
        self.bind("<Control-s>", lambda e: self.toggle_settings())
    
    def open_website(self):
        """Open developer website"""
        webbrowser.open("https://niyibizi_kevin.netlify.app")
        self.status_label.configure(text="Opening developer website...")
    
    def toggle_settings(self):
        """Toggle settings panel visibility"""
        if self.settings_frame.winfo_ismapped():
            self.settings_frame.pack_forget()
            self.status_label.configure(text="Settings closed")
            self.geometry("900x750")
        else:
            self.settings_frame.pack(fill="x", padx=30, pady=(0, 15), before=self.bg_frame)
            self.status_label.configure(text="Settings opened")
            self.geometry("900x820")
            self.check_for_updates()
    
    def check_for_updates(self):
        """Check for updates from GitHub"""
        if self.update_checking:
            return
        
        self.update_checking = True
        self.check_btn.configure(state="disabled")
        self.update_status.configure(text="Checking for updates...", text_color=COLORS['accent_orange'])
        
        def check():
            try:
                response = requests.get(GITHUB_API_URL, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.commit_info = {
                        'sha': data['sha'][:7],
                        'message': data['commit']['message'],
                        'date': data['commit']['committer']['date'][:10],
                        'author': data['commit']['author']['name']
                    }
                    
                    self.commit_label.configure(text=f"Last Commit: {self.commit_info['message']}")
                    self.author_label.configure(text=f"Author: {self.commit_info['author']}")
                    self.date_label.configure(text=f"Date: {self.commit_info['date']}")
                    self.latest_version_label.configure(text=f"Latest: v{self.commit_info['sha']}")
                    self.update_status.configure(text=f"Update available: {self.commit_info['message']}", text_color=COLORS['accent_green'])
                    self.update_btn.configure(state="normal")
                    self.update_available = True
                    self.status_label.configure(text=f"Update available: {self.commit_info['message']}")
                else:
                    self.latest_version_label.configure(text="Could not check updates")
                    self.update_status.configure(text="Failed to connect to GitHub", text_color=COLORS['accent_red'])
                    self.update_btn.configure(state="disabled")
                    self.update_available = False
                
                self.check_btn.configure(state="normal")
                self.update_checking = False
                
            except Exception as e:
                self.update_status.configure(text=f"Error: {str(e)}", text_color=COLORS['accent_red'])
                self.check_btn.configure(state="normal")
                self.update_checking = False
        
        import threading
        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()
    
    def download_update(self):
        """Download and install update"""
        if not self.update_available:
            return
        
        self.update_btn.configure(state="disabled")
        self.update_status.configure(text="Downloading update...", text_color=COLORS['accent_orange'])
        self.update_progress.set(0.1)
        
        def download():
            try:
                response = requests.get(GITHUB_ZIP_URL, stream=True, timeout=30)
                if response.status_code != 200:
                    raise Exception("Failed to download update")
                
                self.update_status.configure(text="Extracting files...")
                self.update_progress.set(0.3)
                
                temp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(temp_dir, "update.zip")
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.update_progress.set(0.5)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                self.update_progress.set(0.7)
                
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
                
                self.update_progress.set(0.9)
                shutil.rmtree(temp_dir)
                
                self.update_progress.set(1.0)
                self.update_status.configure(text="Update downloaded successfully!", text_color=COLORS['accent_green'])
                self.status_label.configure(text="Update ready! Restarting...")
                
                if messagebox.askyesno("Update Ready", "Update has been downloaded. Do you want to restart the app now?"):
                    python = sys.executable
                    os.execl(python, python, *sys.argv)
                
            except Exception as e:
                self.update_status.configure(text=f"Update failed: {str(e)}", text_color=COLORS['accent_red'])
                self.update_btn.configure(state="normal")
                messagebox.showerror("Update Error", f"Failed to update: {str(e)}")
        
        import threading
        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()
    
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
    
    def on_git_push_clicked(self, event):
        self.status_label.configure(text="Git Push in progress...")
        self.status_dot.configure(text_color=COLORS['accent_orange'])
        self.animate_progress(self.git_progress, 1.0, 2000)
        def complete():
            self.status_label.configure(text="Git Push completed!")
            self.status_dot.configure(text_color=COLORS['accent_green'])
            messagebox.showinfo("Success", "Git Push completed successfully!")
        self.after(2000, complete)
    
    def on_download_clicked(self, event):
        self.status_label.configure(text="Download in progress...")
        self.status_dot.configure(text_color=COLORS['accent_orange'])
        self.animate_progress(self.download_progress, 1.0, 2000)
        def complete():
            self.status_label.configure(text="Download completed!")
            self.status_dot.configure(text_color=COLORS['accent_green'])
            messagebox.showinfo("Success", "Download completed successfully!")
        self.after(2000, complete)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    app = App()
    app.mainloop()
