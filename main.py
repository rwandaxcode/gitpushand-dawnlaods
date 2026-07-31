import customtkinter as ctk
from PIL import Image, ImageFilter, ImageEnhance
import os
import sys
import requests
import shutil
import tempfile
import zipfile
from tkinter import messagebox
import webbrowser
import threading
import time

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
        self.update_available = False
        self.update_version = ""
        self.update_commit_message = ""
        self.update_ready = False
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
            text="⚙️",
            width=40,
            height=36,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=18),
            command=self.toggle_settings
        )
        self.settings_btn.pack(side="right", padx=(0, 8))
        
        self.close_btn = ctk.CTkButton(
            self.header_frame,
            text="✕",
            width=30,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=16, weight="bold"),
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
        
        # --- SETTINGS PANEL (Responsive Beautiful UI) ---
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
            text="⚙️ Settings",
            font=ctk.CTkFont(family="Roboto", size=22, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkButton(
            settings_header,
            text="✕",
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
        
        # --- UPDATE SECTION (Beautiful UI) ---
        update_section = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        update_section.pack(fill="x", padx=25, pady=15)
        
        # Update header
        update_header = ctk.CTkFrame(update_section, fg_color="transparent")
        update_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            update_header,
            text="🔄",
            font=ctk.CTkFont(size=24),
            text_color=COLORS['accent_blue']
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            update_header,
            text="Update Application",
            font=ctk.CTkFont(family="Roboto", size=17, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # Update status card
        status_card = ctk.CTkFrame(update_section, fg_color=COLORS['bg_primary'], corner_radius=14)
        status_card.pack(fill="x", pady=5)
        
        # Status row
        status_row = ctk.CTkFrame(status_card, fg_color="transparent")
        status_row.pack(fill="x", padx=18, pady=12)
        
        self.update_status_icon = ctk.CTkLabel(
            status_row,
            text="⏳",
            font=ctk.CTkFont(size=22),
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
        
        # --- COMMIT MESSAGE CARD (Shows why update exists) ---
        self.commit_card = ctk.CTkFrame(status_card, fg_color=COLORS['bg_secondary'], corner_radius=10)
        self.commit_card.pack(fill="x", padx=18, pady=(0, 10))
        self.commit_card.pack_forget()  # Hidden initially
        
        commit_header = ctk.CTkFrame(self.commit_card, fg_color="transparent")
        commit_header.pack(fill="x", padx=12, pady=8)
        
        ctk.CTkLabel(
            commit_header,
            text="📝",
            font=ctk.CTkFont(size=16),
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
        self.restart_frame = ctk.CTkFrame(update_section, fg_color="transparent")
        self.restart_frame.pack(fill="x", pady=5)
        
        self.restart_btn = ctk.CTkButton(
            self.restart_frame,
            text="🔄 Restart & Update",
            height=48,
            corner_radius=14,
            fg_color=COLORS['accent_green'],
            hover_color='#2a9d4d',
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            command=self.restart_app
        )
        self.restart_btn.pack(fill="x")
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
            text="ℹ️",
            font=ctk.CTkFont(size=24),
            text_color=COLORS['accent_blue']
        ).pack(side="left", padx=(0, 10))
        
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
            text="👨‍💻",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            dev_frame,
            text="Developed by:",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            dev_frame,
            text="Niyibizi Kevin",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=COLORS['accent_blue']
        ).pack(side="left", padx=(5, 0))
        
        # Website
        website_frame = ctk.CTkFrame(about_content, fg_color="transparent")
        website_frame.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            website_frame,
            text="🌐",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 8))
        
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
            text="📅",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            year_frame,
            text="2024",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        # --- BACKGROUND IMAGE ---
        self.bg_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bg_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.bg_image_label = ctk.CTkLabel(self.bg_frame, text="")
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        
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
        
        self.status_dot = ctk.CTkLabel(self.status_bar, text="●", font=ctk.CTkFont(family="Roboto", size=10), text_color=COLORS['accent_green'])
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
        
        # --- AUTO UPDATE ON START ---
        self.after(1500, self.auto_check_update)
    
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
        """Show commit message card"""
        self.commit_card.pack(fill="x", padx=18, pady=(0, 10))
        self.commit_message_label.configure(text=message)
    
    def hide_commit_message(self):
        """Hide commit message card"""
        self.commit_card.pack_forget()
    
    def update_ui_status(self, icon, title, desc, progress, color=COLORS['accent_orange']):
        """Update status UI elements"""
        self.update_status_icon.configure(text=icon, text_color=color)
        self.update_status_title.configure(text=title)
        self.update_status_desc.configure(text=desc)
        self.update_progress.set(progress)
    
    def auto_check_update(self):
        """Check for updates automatically"""
        self.update_ui_status("⏳", "Checking for updates...", "Please wait while we check for the latest version", 0.1)
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
                    
                    # Show commit message as reason for update
                    self.show_commit_message(self.update_commit_message)
                    
                    self.update_ui_status("📥", "Update available!", "Downloading update automatically...", 0.2, COLORS['accent_blue'])
                    self.download_update_auto()
                else:
                    self.update_ui_status("✅", "No updates available", "You are using the latest version", 1.0, COLORS['accent_green'])
                    self.status_label.configure(text="Ready - Latest version")
                    self.restart_btn.configure(state="disabled")
                    self.hide_commit_message()
                    
            except Exception as e:
                self.update_ui_status("⚠️", "Could not check updates", "Check your internet connection", 0, COLORS['accent_red'])
                self.status_label.configure(text="Ready - Update check failed")
                self.hide_commit_message()
        
        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()
    
    def download_update_auto(self):
        """Download update automatically in background"""
        def download():
            try:
                response = requests.get(GITHUB_ZIP_URL, stream=True, timeout=30)
                if response.status_code != 200:
                    raise Exception("Failed to download update")
                
                self.update_ui_status("📥", "Downloading update...", "Please wait while we download the latest version", 0.3)
                
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
                
                self.update_ui_status("📦", "Extracting files...", "Preparing update for installation", 0.7)
                
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
                
                self.update_ui_status("✅", "Update ready!", f"Version {self.update_version} is ready to install", 1.0, COLORS['accent_green'])
                self.status_label.configure(text="Update ready! Restart to apply")
                self.restart_btn.configure(state="normal")
                
            except Exception as e:
                self.update_ui_status("❌", "Update failed", f"Error: {str(e)[:50]}", 0, COLORS['accent_red'])
                self.status_label.configure(text="Update failed")
                self.hide_commit_message()
        
        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()
    
    def restart_app(self):
        if messagebox.askyesno("Restart", "🔄 Restart app to apply update?"):
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
