"""
 Auto Typer v4.0 - Advanced Edition
Features:
- Auto-Save Draft (real-time backup)
- Customizable Hotkeys (any key combination)
- 4 Typing Modes (Burst, Human, Stealth, Line-by-Line)
- Advanced Settings Panel
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import threading
import time
import random
import json
import os
import winsound
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple
from pynput.keyboard import Controller, Key, Listener
from pynput.keyboard import KeyCode


@dataclass
class TypingConfig:
    # Timing
    base_delay_ms: int = 85
    randomness_ms: int = 20
    
    # Modes
    typing_mode: str = "Human"  # Burst, Human, Stealth, LineByLine
    
    # Advanced timing
    line_break_delay_ms: int = 200
    punctuation_delay_ms: int = 150
    word_delay_ms: int = 80
    thinking_chance: float = 0.02
    thinking_duration_ms: int = 400
    
    # General
    countdown_sec: int = 3
    sound_enabled: bool = True
    auto_save_interval_sec: int = 5


@dataclass
class HotkeyConfig:
    start: str = "alt+s"
    pause: str = "alt+p"
    stop: str = "alt+x"


class AutoTyper:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Create logs and data directories first
        self.logs_dir = "logs"
        self.data_dir = "data"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.logs_dir, f"app_{datetime.now(tz=timezone.utc).strftime('%Y%m%d')}.log"), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.root = ctk.CTk()
        self.root.title("⌨️  Auto Typer v4.0")
        self.root.geometry("1350x850")
        self.root.minsize(1200, 750)
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Core states
        self.is_typing = False
        self.is_paused = False
        self.stop_event = threading.Event()
        self.typing_thread: Optional[threading.Thread] = None
        
        # UI size state
        self.size_mode = 0  # 0=Normal, 1=Compact, 2=Mini
        
        # Auto-save
        self.auto_save_timer: Optional[threading.Timer] = None
        self.text_modified = False
        
        # Components
        self.keyboard = Controller()
        self.config = self.load_config()
        self.hotkeys = self.load_hotkeys()
        self.profiles: Dict[str, str] = self.load_profiles()
        self.stats = self.load_stats()
        self.autosave_enabled = tk.BooleanVar(value=True)
        
        # Hotkey state
        self.current_modifiers = set()
        self.hotkey_listener = None
        
        # Build UI
        self.setup_ui()
        self.load_last_text()
        self.start_auto_save()
        self.start_hotkey_listener()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # ==================== FILE OPERATIONS ====================
    def load_config(self) -> TypingConfig:
        config_file = os.path.join(self.data_dir, "config_v4.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                    valid = {k: v for k, v in data.items() if k in TypingConfig.__dataclass_fields__}
                    return TypingConfig(**valid)
            except (json.JSONDecodeError, IOError, TypeError) as e:
                logging.error(f"Failed to load config_v4.json: {e}")
        return TypingConfig()
    
    def save_config(self):
        config_file = os.path.join(self.data_dir, "config_v4.json")
        with open(config_file, "w") as f:
            json.dump(asdict(self.config), f, indent=2)
    
    def load_hotkeys(self) -> HotkeyConfig:
        hotkeys_file = os.path.join(self.data_dir, "hotkeys_v4.json")
        if os.path.exists(hotkeys_file):
            try:
                with open(hotkeys_file, "r") as f:
                    data = json.load(f)
                    valid = {k: v for k, v in data.items() if k in HotkeyConfig.__dataclass_fields__}
                    return HotkeyConfig(**valid)
            except (json.JSONDecodeError, IOError, TypeError) as e:
                logging.error(f"Failed to load hotkeys_v4.json: {e}")
        return HotkeyConfig()
    
    def save_hotkeys(self):
        hotkeys_file = os.path.join(self.data_dir, "hotkeys_v4.json")
        with open(hotkeys_file, "w") as f:
            json.dump(asdict(self.hotkeys), f, indent=2)
    
    def load_profiles(self) -> Dict[str, str]:
        profiles_file = os.path.join(self.data_dir, "profiles_v4.json")
        if os.path.exists(profiles_file):
            try:
                with open(profiles_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON in profiles_v4.json: {e}")
            except IOError as e:
                logging.error(f"Failed to read profiles_v4.json: {e}")
        return {}
    
    def save_profiles(self):
        profiles_file = os.path.join(self.data_dir, "profiles_v4.json")
        with open(profiles_file, "w") as f:
            json.dump(self.profiles, f, indent=2)
    
    def load_stats(self) -> dict:
        stats_file = os.path.join(self.data_dir, "stats_v4.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON in stats_v4.json: {e}")
            except IOError as e:
                logging.error(f"Failed to read stats_v4.json: {e}")
        return {"sessions": 0, "total_chars": 0, "last_session": 0, "last_date": ""}
    
    def save_stats(self):
        stats_file = os.path.join(self.data_dir, "stats_v4.json")
        with open(stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)
    
    def load_last_text(self):
        last_text_file = os.path.join(self.data_dir, "last_text_v4.txt")
        if os.path.exists(last_text_file):
            try:
                with open(last_text_file, "r", encoding="utf-8") as f:
                    self.text_area.insert("0.0", f.read())
                    self.update_char_count()
            except IOError as e:
                logging.error(f"Failed to load last_text_v4.txt: {e}")
    
    def save_last_text(self):
        last_text_file = os.path.join(self.data_dir, "last_text_v4.txt")
        try:
            with open(last_text_file, "w", encoding="utf-8") as f:
                f.write(self.text_area.get("0.0", "end-1c"))
        except IOError as e:
            logging.error(f"Failed to save last_text_v4.txt: {e}")
    
    # ==================== UI SETUP ====================
    def setup_ui(self):
        # Header با گرادیانت (کوچکتر شده)
        header = ctk.CTkFrame(self.root, height=55, corner_radius=0, fg_color=("#1a1a2e", "#0f0f1e"))
        header.pack(fill="x")
        
        # Logo و عنوان (کوچکتر شده)
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=8)
        
        ctk.CTkLabel(
            title_frame,
            text="⌨️",
            font=ctk.CTkFont(size=28)
        ).pack(side="left", padx=(0, 8))
        
        title_container = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_container.pack(side="left")
        
        ctk.CTkLabel(
            title_container, 
            text=" Auto Typer", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#ffffff", "#e0e0e0")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_container, 
            text="v4.0 Advanced Edition", 
            font=ctk.CTkFont(size=9),
            text_color=("#888888", "#666666")
        ).pack(anchor="w")
        
        # Mode tag با رنگ یکدست (Primary Blue)
        mode_frame = ctk.CTkFrame(header, fg_color=("#2196f3", "#1976d2"), corner_radius=15)
        mode_frame.pack(side="right", padx=20)
        
        mode_tag = ctk.CTkLabel(
            mode_frame,
            text=f"⚡ {self.config.typing_mode} Mode",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff"
        )
        mode_tag.pack(padx=15, pady=6)
        self.mode_tag = mode_tag
        
        # Size toggle ساده (فقط دو حالت)
        self.size_btn = ctk.CTkButton(
            header,
            text="💻 Normal",
            command=self.toggle_size,
            width=95,
            height=32,
            corner_radius=8,
            fg_color=("#37474f", "#263238"),
            hover_color=("#546e7a", "#37474f"),
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.size_btn.pack(side="right", padx=12)
        
        # Main container
        main = ctk.CTkFrame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Text (60%)
        left = ctk.CTkFrame(main, width=650)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        left.pack_propagate(False)
        
        # Right panel - Controls (40%)
        right = ctk.CTkFrame(main, width=450)
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))
        right.pack_propagate(False)
        
        self.setup_text_panel(left)
        self.setup_control_panel(left)
        self.setup_advanced_settings(right)
    
    def setup_text_panel(self, parent):
        # Toolbar با shadow effect
        toolbar = ctk.CTkFrame(parent, height=50, corner_radius=10)
        toolbar.pack(fill="x", pady=(0, 8))
        
        # عنوان با آیکون
        title_section = ctk.CTkFrame(toolbar, fg_color="transparent")
        title_section.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            title_section, 
            text="📝 Text Editor", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#2196f3", "#64b5f6")
        ).pack(side="left")
        
        # Divider
        ctk.CTkFrame(toolbar, width=2, height=30, fg_color=("#333333", "#555555")).pack(side="left", padx=15)
        
        ctk.CTkLabel(
            toolbar, 
            text="📂 Profile:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(5, 8))
        self.profile_var = tk.StringVar(value="Default")
        self.profile_dropdown = ctk.CTkComboBox(
            toolbar,
            values=["Default"] + list(self.profiles.keys()),
            variable=self.profile_var,
            width=150,
            height=35,
            corner_radius=8,
            command=self.on_profile_change
        )
        self.profile_dropdown.pack(side="left", padx=5)
        
        # Buttons با رنگ‌های بهتر
        ctk.CTkButton(
            toolbar, 
            text="💾 Save", 
            width=80, 
            height=35,
            corner_radius=8,
            fg_color=("#2196f3", "#1976d2"),
            hover_color=("#1976d2", "#1565c0"),
            command=self.save_current_profile
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            toolbar, 
            text="🗑️ Delete", 
            width=80, 
            height=35,
            corner_radius=8,
            fg_color=("#f44336", "#d32f2f"),
            hover_color=("#d32f2f", "#c62828"),
            command=self.delete_profile
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            toolbar, 
            text="📁 Load", 
            width=80, 
            height=35,
            corner_radius=8,
            fg_color=("#37474f", "#263238"),
            hover_color=("#455a64", "#37474f"),
            command=self.load_from_file
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            toolbar, 
            text="📋 Paste", 
            width=80, 
            height=35,
            corner_radius=8,
            fg_color=("#37474f", "#263238"),
            hover_color=("#455a64", "#37474f"),
            command=self.paste_from_clipboard
        ).pack(side="left", padx=3)
        
        # Save indicator با استایل بهتر
        indicator_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        indicator_frame.pack(side="right", padx=15)
        
        self.save_indicator = ctk.CTkLabel(
            indicator_frame, 
            text="● Saved", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#4caf50", "#66bb6a")
        )
        self.save_indicator.pack()
        
        # Text area با border و shadow
        text_container = ctk.CTkFrame(parent, corner_radius=10)
        text_container.pack(fill="both", expand=True, pady=8)
        
        self.text_area = ctk.CTkTextbox(
            text_container, 
            font=ctk.CTkFont(family="Consolas", size=13),
            wrap="word",
            corner_radius=8,
            border_width=2,
            border_color=("#2196f3", "#1976d2")
        )
        self.text_area.pack(fill="both", expand=True, padx=2, pady=2)
        self.text_area.bind("<KeyRelease>", self.on_text_change)
        
        # Status bar با آیکون‌ها
        status = ctk.CTkFrame(parent, height=40, corner_radius=10)
        status.pack(fill="x", pady=(8, 0))
        
        # Stats با آیکون و رنگ
        self.char_label = ctk.CTkLabel(
            status, 
            text="🔤 Characters: 0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#2196f3", "#64b5f6")
        )
        self.char_label.pack(side="left", padx=15)
        
        self.line_label = ctk.CTkLabel(
            status, 
            text="📄 Lines: 0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#2196f3", "#64b5f6")
        )
        self.line_label.pack(side="left", padx=15)
        
        self.word_label = ctk.CTkLabel(
            status, 
            text="📝 Words: 0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#2196f3", "#64b5f6")
        )
        self.word_label.pack(side="left", padx=15)
        
        # Divider
        ctk.CTkFrame(status, width=2, height=25, fg_color=("#333333", "#555555")).pack(side="right", padx=15)
        
        self.auto_save_label = ctk.CTkLabel(
            status, 
            text="💾 Auto-save: ON",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#4caf50", "#66bb6a")
        )
        self.auto_save_label.pack(side="right", padx=15)
    
    def setup_control_panel(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        # Main buttons با shadow effect
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        self.start_btn = ctk.CTkButton(
            btn_frame, 
            text="▶️ START", 
            command=self.start_typing,
            width=160, 
            height=55, 
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=15,
            fg_color=("#4caf50", "#388e3c"),
            hover_color=("#66bb6a", "#4caf50"),
            border_width=0
        )
        self.start_btn.pack(side="left", padx=10)
        
        self.pause_btn = ctk.CTkButton(
            btn_frame, 
            text="⏸️ PAUSE", 
            command=self.toggle_pause,
            width=160, 
            height=55, 
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=15,
            state="disabled", 
            fg_color=("#37474f", "#263238"),
            hover_color=("#455a64", "#37474f"),
            border_width=0,
            text_color=("#888888", "#777777")
        )
        self.pause_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame, 
            text="⏹️ STOP", 
            command=self.stop_typing,
            width=160, 
            height=55, 
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=15,
            state="disabled", 
            fg_color=("#37474f", "#263238"),
            hover_color=("#455a64", "#37474f"),
            border_width=0,
            text_color=("#888888", "#777777")
        )
        self.stop_btn.pack(side="left", padx=10)
        
        # Progress bar با گرادیانت
        progress_container = ctk.CTkFrame(frame, fg_color="transparent")
        progress_container.pack(fill="x", padx=25, pady=15)
        
        self.progress = ctk.CTkProgressBar(
            progress_container, 
            height=18,
            corner_radius=10,
            border_width=2,
            border_color=("#2196f3", "#1976d2"),
            progress_color=("#4caf50", "#388e3c")
        )
        self.progress.pack(fill="x")
        self.progress.set(0)
        
        # Status با background
        status_frame = ctk.CTkFrame(frame, corner_radius=10, fg_color=("#1a1a2e", "#0f0f1e"))
        status_frame.pack(fill="x", padx=25, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="● READY", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color=("#4caf50", "#66bb6a")
        )
        self.status_label.pack(pady=12)
        
        self.typing_countdown_label = ctk.CTkLabel(
            frame, 
            text="", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=("#2196f3", "#64b5f6")
        )
        self.typing_countdown_label.pack(pady=8)
    
    def setup_advanced_settings(self, parent):
        # Tab view
        tabview = ctk.CTkTabview(parent, segmented_button_fg_color=("#1a1a2e", "#0f0f1e"), 
                                segmented_button_selected_color=("#2196f3", "#1976d2"),
                                segmented_button_selected_hover_color=("#42a5f5", "#2196f3"))
        tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 1: Typing Modes
        modes_tab = tabview.add("⚡ Modes")
        self.setup_modes_tab(modes_tab)
        
        # Tab 2: Timing
        timing_tab = tabview.add("⏱️ Timing")
        self.setup_advanced_timing_tab(timing_tab)
        
        # Tab 3: Hotkeys
        hotkey_tab = tabview.add("⌨️ Keys")
        self.setup_hotkey_tab(hotkey_tab)
        
        # Tab 4: Statistics
        stats_tab = tabview.add("📊 Stats")
        self.setup_stats_tab(stats_tab)
        
        # Tab 5: Settings
        settings_tab = tabview.add("⚙️ More")
        self.setup_autosave_tab(settings_tab)
    
    def setup_modes_tab(self, parent):
        # با scrollable frame
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Typing Modes", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(5, 15))
        
        modes = [
            ("🚀 Burst", "Burst", "Ultra-fast typing, minimal delays.\nBest for passwords and forms."),
            ("👤 Human", "Human", "Natural typing with variations.\nRecommended for ChatGPT/websites."),
            ("🕵️ Stealth", "Stealth", "Very slow with long pauses.\nAvoids bot detection."),
            ("📝 Line-by-Line", "LineByLine", "Types line by line with Enter.\nPerfect for code/terminal."),
        ]
        
        self.mode_var = tk.StringVar(value=self.config.typing_mode)
        
        for title, value, desc in modes:
            # تعیین border color
            border_col = ("#2196f3", "#1976d2") if value == self.config.typing_mode else ("#333333", "#555555")
            
            mode_frame = ctk.CTkFrame(frame, corner_radius=8, border_width=2, border_color=border_col)
            mode_frame.pack(fill="x", pady=5)
            
            ctk.CTkRadioButton(
                mode_frame, text=title, variable=self.mode_var, value=value,
                command=self.on_mode_change, font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", padx=15, pady=(10, 5))
            
            ctk.CTkLabel(mode_frame, text=desc, font=ctk.CTkFont(size=10), 
                        text_color="gray", justify="left").pack(anchor="w", padx=40, pady=(0, 10))
        
        ctk.CTkButton(frame, text="✔ Apply Mode", command=self.apply_mode, 
                     fg_color=("#2196f3", "#1976d2"), hover_color=("#42a5f5", "#2196f3"),
                     height=40, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15, fill="x", padx=20)
    
    def setup_advanced_timing_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Base Delay
        ctk.CTkLabel(frame, text="Base Delay (ms):", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.delay_slider = ctk.CTkSlider(frame, from_=20, to=500)
        self.delay_slider.set(self.config.base_delay_ms)
        self.delay_slider.pack(fill="x", pady=5)
        self.delay_label = ctk.CTkLabel(frame, text=f"Value: {self.config.base_delay_ms} ms")
        self.delay_label.pack(anchor="w")
        self.delay_slider.configure(command=self.on_delay_change)
        
        # Randomness
        ctk.CTkLabel(frame, text="Randomness (ms):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 0))
        self.random_slider = ctk.CTkSlider(frame, from_=0, to=150)
        self.random_slider.set(self.config.randomness_ms)
        self.random_slider.pack(fill="x", pady=5)
        self.random_label = ctk.CTkLabel(frame, text=f"Value: ±{self.config.randomness_ms} ms")
        self.random_label.pack(anchor="w")
        self.random_slider.configure(command=self.on_random_change)
        
        # Punctuation Delay
        ctk.CTkLabel(frame, text="Punctuation Delay (ms):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 0))
        self.punct_slider = ctk.CTkSlider(frame, from_=0, to=300)
        self.punct_slider.set(self.config.punctuation_delay_ms)
        self.punct_slider.pack(fill="x", pady=5)
        self.punct_label = ctk.CTkLabel(frame, text=f"Value: {self.config.punctuation_delay_ms} ms")
        self.punct_label.pack(anchor="w")
        self.punct_slider.configure(command=self.on_punct_change)
        
        # Word Delay
        ctk.CTkLabel(frame, text="Between Words Delay (ms):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 0))
        self.word_slider = ctk.CTkSlider(frame, from_=0, to=200)
        self.word_slider.set(self.config.word_delay_ms)
        self.word_slider.pack(fill="x", pady=5)
        self.word_label = ctk.CTkLabel(frame, text=f"Value: {self.config.word_delay_ms} ms")
        self.word_label.pack(anchor="w")
        self.word_slider.configure(command=self.on_word_change)
        
        # Thinking chance
        ctk.CTkLabel(frame, text="Thinking Chance (%):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 0))
        self.think_slider = ctk.CTkSlider(frame, from_=0, to=10)
        self.think_slider.set(self.config.thinking_chance * 100)
        self.think_slider.pack(fill="x", pady=5)
        self.think_label = ctk.CTkLabel(frame, text=f"Value: {self.config.thinking_chance * 100:.0f}%")
        self.think_label.pack(anchor="w")
        self.think_slider.configure(command=self.on_think_change)
        
        # Countdown
        ctk.CTkLabel(frame, text="Countdown (seconds):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 0))
        self.countdown_slider = ctk.CTkSlider(frame, from_=1, to=10)
        self.countdown_slider.set(self.config.countdown_sec)
        self.countdown_slider.pack(fill="x", pady=5)
        self.countdown_val_label = ctk.CTkLabel(frame, text=f"Value: {self.config.countdown_sec} sec")
        self.countdown_val_label.pack(anchor="w")
        self.countdown_slider.configure(command=self.on_countdown_change)
        
        # Sound
        self.sound_var = tk.BooleanVar(value=self.config.sound_enabled)
        ctk.CTkCheckBox(frame, text="Play sound on completion", variable=self.sound_var).pack(anchor="w", pady=15)
        
        ctk.CTkButton(frame, text="💾 Save All Settings", command=self.save_timing_settings, 
                     fg_color=("#4caf50", "#388e3c"), hover_color=("#66bb6a", "#4caf50"),
                     height=40, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15, fill="x", padx=20)
    
    def setup_hotkey_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Custom Hotkeys", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        ctk.CTkLabel(frame, text="Start Typing:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.start_hotkey_entry = ctk.CTkEntry(frame, width=250, placeholder_text="e.g., alt+s, ctrl+shift+t, f5")
        self.start_hotkey_entry.insert(0, self.hotkeys.start)
        self.start_hotkey_entry.pack(fill="x", pady=5)
        
        ctk.CTkLabel(frame, text="Pause/Resume:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0))
        self.pause_hotkey_entry = ctk.CTkEntry(frame, width=250, placeholder_text="e.g., alt+p")
        self.pause_hotkey_entry.insert(0, self.hotkeys.pause)
        self.pause_hotkey_entry.pack(fill="x", pady=5)
        
        ctk.CTkLabel(frame, text="Stop:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0))
        self.stop_hotkey_entry = ctk.CTkEntry(frame, width=250, placeholder_text="e.g., alt+x")
        self.stop_hotkey_entry.insert(0, self.hotkeys.stop)
        self.stop_hotkey_entry.pack(fill="x", pady=5)
        
        ctk.CTkButton(frame, text="💾 Save Hotkeys", command=self.save_hotkey_settings, 
                     fg_color=("#4caf50", "#388e3c"), hover_color=("#66bb6a", "#4caf50"),
                     height=40, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15, fill="x")
        
        ctk.CTkLabel(
            frame, 
            text="💡 Supported formats:\nalt, ctrl, shift + letter/number\nFunction keys: f1-f12",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            justify="left"
        ).pack(pady=10)
        
        ctk.CTkButton(frame, text="↺ Reset to Default", command=self.reset_hotkeys, 
                     fg_color=("#ff9800", "#f57c00"), hover_color=("#ffb74d", "#ff9800"),
                     height=35).pack(pady=5, fill="x")
    
    def setup_stats_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Usage Statistics", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(5, 15))
        
        stats_card = ctk.CTkFrame(frame, corner_radius=10, border_width=2, 
                                 border_color=("#2196f3", "#1976d2"))
        stats_card.pack(fill="x", pady=10)
        
        self.stats_sessions = ctk.CTkLabel(stats_card, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.stats_sessions.pack(pady=(15, 8))
        
        self.stats_chars = ctk.CTkLabel(stats_card, text="", font=ctk.CTkFont(size=14))
        self.stats_chars.pack(pady=5)
        
        self.stats_avg = ctk.CTkLabel(stats_card, text="", font=ctk.CTkFont(size=13))
        self.stats_avg.pack(pady=5)
        
        self.stats_last = ctk.CTkLabel(stats_card, text="", font=ctk.CTkFont(size=11))
        self.stats_last.pack(pady=(5, 15))
        
        ctk.CTkButton(frame, text="🔄 Refresh", command=self.update_stats_display,
                     fg_color=("#2196f3", "#1976d2"), hover_color=("#42a5f5", "#2196f3"),
                     height=35).pack(pady=10, fill="x")
        ctk.CTkButton(frame, text="🗑️ Reset Statistics", fg_color=("#f44336", "#d32f2f"), 
                     hover_color=("#ef5350", "#f44336"), command=self.reset_stats, height=35).pack(pady=5, fill="x")
        
        self.update_stats_display()
    
    def setup_autosave_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Settings & Info", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(5, 15))
        
        # Auto-save section
        autosave_section = ctk.CTkFrame(frame, corner_radius=10)
        autosave_section.pack(fill="x", pady=5)
        
        ctk.CTkLabel(autosave_section, text="💾 Auto-Save", font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=("#2196f3", "#64b5f6")).pack(pady=(10, 5))
        
        ctk.CTkLabel(autosave_section, text="Interval (seconds):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15)
        self.autosave_slider = ctk.CTkSlider(autosave_section, from_=2, to=30, number_of_steps=28)
        self.autosave_slider.set(self.config.auto_save_interval_sec)
        self.autosave_slider.pack(fill="x", pady=5, padx=15)
        self.autosave_label = ctk.CTkLabel(autosave_section, text=f"Every {self.config.auto_save_interval_sec} seconds")
        self.autosave_label.pack(anchor="w", padx=15)
        self.autosave_slider.configure(command=self.on_autosave_change)
        
        ctk.CTkCheckBox(autosave_section, text="Enable Auto-Save", variable=self.autosave_enabled, 
                       command=self.toggle_autosave).pack(anchor="w", pady=10, padx=15)
        
        ctk.CTkButton(autosave_section, text="💾 Save Settings", command=self.save_autosave_settings, 
                     fg_color=("#4caf50", "#388e3c"), hover_color=("#66bb6a", "#4caf50"),
                     height=35).pack(pady=(5, 15), padx=15, fill="x")
        
        # Files info section
        info_section = ctk.CTkFrame(frame, corner_radius=10)
        info_section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            info_section,
            text="📁 Files Location",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#ff9800", "#ffb74d")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            info_section,
            text="• data/ - Settings & profiles\n• logs/ - Application logs",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        ).pack(pady=(0, 10), padx=15)
        
        # GitHub section
        github_frame = ctk.CTkFrame(frame, corner_radius=10, fg_color=("#1a1a2e", "#0f0f1e"))
        github_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkLabel(
            github_frame,
            text="🌐 Social",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#4caf50", "#66bb6a")
        ).pack(pady=(12, 5))
        
        ctk.CTkLabel(
            github_frame,
            text="Follow for more projects!",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=3)
        
        btn_row = ctk.CTkFrame(github_frame, fg_color="transparent")
        btn_row.pack(padx=15, pady=(5, 12), fill="x")

        github_link = ctk.CTkButton(
            btn_row,
            text="GitHub",
            command=self.open_github,
            fg_color="transparent",
            hover_color=("#1e2d1e", "#1e2d1e"),
            border_width=1,
            border_color=("#4caf50", "#388e3c"),
            text_color=("#4caf50", "#66bb6a"),
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        github_link.pack(side="left", expand=True, fill="x", padx=(0, 5))

        telegram_link = ctk.CTkButton(
            btn_row,
            text="Telegram",
            command=self.open_telegram,
            fg_color="transparent",
            hover_color=("#0d1e2d", "#0d1e2d"),
            border_width=1,
            border_color=("#0088cc", "#0077b5"),
            text_color=("#0088cc", "#29a8e0"),
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        telegram_link.pack(side="left", expand=True, fill="x", padx=(5, 0))
    
    # ==================== MODE HANDLERS ====================
    def on_mode_change(self):
        mode = self.mode_var.get()
        self.mode_tag.configure(text=f"⚡ Mode: {mode}")
        
        # Update sliders based on mode
        if mode == "Burst":
            self.delay_slider.set(20)
            self.random_slider.set(5)
        elif mode == "Human":
            self.delay_slider.set(85)
            self.random_slider.set(25)
        elif mode == "Stealth":
            self.delay_slider.set(180)
            self.random_slider.set(50)
        elif mode == "LineByLine":
            self.delay_slider.set(60)
            self.random_slider.set(15)
    
    def apply_mode(self):
        self.config.typing_mode = self.mode_var.get()
        
        if self.config.typing_mode == "Burst":
            self.config.base_delay_ms = 20
            self.config.randomness_ms = 5
            self.config.punctuation_delay_ms = 0
            self.config.word_delay_ms = 0
            self.config.thinking_chance = 0
        elif self.config.typing_mode == "Human":
            self.config.base_delay_ms = 85
            self.config.randomness_ms = 25
            self.config.punctuation_delay_ms = 150
            self.config.word_delay_ms = 80
            self.config.thinking_chance = 0.02
        elif self.config.typing_mode == "Stealth":
            self.config.base_delay_ms = 180
            self.config.randomness_ms = 50
            self.config.punctuation_delay_ms = 250
            self.config.word_delay_ms = 150
            self.config.thinking_chance = 0.05
        elif self.config.typing_mode == "LineByLine":
            self.config.base_delay_ms = 60
            self.config.randomness_ms = 15
            self.config.punctuation_delay_ms = 100
            self.config.word_delay_ms = 50
            self.config.thinking_chance = 0.01
        
        # Update UI
        self.delay_slider.set(self.config.base_delay_ms)
        self.random_slider.set(self.config.randomness_ms)
        self.punct_slider.set(self.config.punctuation_delay_ms)
        self.word_slider.set(self.config.word_delay_ms)
        self.think_slider.set(self.config.thinking_chance * 100)
        
        self.delay_label.configure(text=f"Value: {self.config.base_delay_ms} ms")
        self.random_label.configure(text=f"Value: ±{self.config.randomness_ms} ms")
        self.punct_label.configure(text=f"Value: {self.config.punctuation_delay_ms} ms")
        self.word_label.configure(text=f"Value: {self.config.word_delay_ms} ms")
        self.think_label.configure(text=f"Value: {self.config.thinking_chance * 100:.0f}%")
        
        self.mode_tag.configure(text=f"⚡ {self.config.typing_mode} Mode")
        self.save_config()
        messagebox.showinfo("Success", f"Mode changed to {self.config.typing_mode}")
    
    # ==================== TIMING CALLBACKS ====================
    def on_delay_change(self, value):
        self.delay_label.configure(text=f"Value: {int(value)} ms")
    
    def on_random_change(self, value):
        self.random_label.configure(text=f"Value: ±{int(value)} ms")
    
    def on_punct_change(self, value):
        self.punct_label.configure(text=f"Value: {int(value)} ms")
    
    def on_word_change(self, value):
        self.word_label.configure(text=f"Value: {int(value)} ms")
    
    def on_think_change(self, value):
        self.think_label.configure(text=f"Value: {int(value)}%")
    
    def on_countdown_change(self, value):
        self.countdown_val_label.configure(text=f"Value: {int(value)} sec")
    
    def on_autosave_change(self, value):
        self.autosave_label.configure(text=f"Every {int(value)} seconds")
    
    def save_timing_settings(self):
        self.config.base_delay_ms = int(self.delay_slider.get())
        self.config.randomness_ms = int(self.random_slider.get())
        self.config.punctuation_delay_ms = int(self.punct_slider.get())
        self.config.word_delay_ms = int(self.word_slider.get())
        self.config.thinking_chance = int(self.think_slider.get()) / 100
        self.config.countdown_sec = int(self.countdown_slider.get())
        self.config.sound_enabled = self.sound_var.get()
        self.save_config()
        messagebox.showinfo("Success", "Timing settings saved!")
    
    def save_autosave_settings(self):
        self.config.auto_save_interval_sec = int(self.autosave_slider.get())
        self.save_config()
        
        if self.autosave_enabled.get():
            self.start_auto_save()
        
        messagebox.showinfo("Success", f"Auto-save interval set to {self.config.auto_save_interval_sec} seconds")
    
    def toggle_autosave(self):
        if self.autosave_enabled.get():
            self.start_auto_save()
            self.auto_save_label.configure(text="⏳ Auto-save: ON", text_color="#4caf50")
        else:
            if self.auto_save_timer:
                self.auto_save_timer.cancel()
            self.auto_save_label.configure(text="⏳ Auto-save: OFF", text_color="gray")
    
    # ==================== AUTO-SAVE ====================
    def start_auto_save(self):
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
        if self.autosave_enabled.get():
            self.auto_save_timer = threading.Timer(self.config.auto_save_interval_sec, self.auto_save_callback)
            self.auto_save_timer.daemon = True
            self.auto_save_timer.start()
    
    def auto_save_callback(self):
        if self.text_modified:
            self.save_last_text()
            self.text_modified = False
            self.save_indicator.configure(text="● Auto-saved", text_color="orange")
            self.root.after(1000, lambda: self.save_indicator.configure(text="● Saved", text_color="green"))
        
        self.start_auto_save()
    
    def on_text_change(self, event=None):
        self.update_char_count()
        self.text_modified = True
        self.save_indicator.configure(text="● Unsaved", text_color="red")
    
    def update_char_count(self):
        text = self.text_area.get("0.0", "end-1c")
        chars = len(text)
        lines = len(text.split("\n"))
        words = len(text.split()) if text.strip() else 0
        
        self.char_label.configure(text=f"🔤 Characters: {chars}")
        self.line_label.configure(text=f"📄 Lines: {lines}")
        self.word_label.configure(text=f"📝 Words: {words}")
    
    # ==================== PROFILES & FILES ====================
    def on_profile_change(self, choice):
        if choice in self.profiles:
            self.text_area.delete("0.0", "end")
            self.text_area.insert("0.0", self.profiles[choice])
            self.update_char_count()
    
    def save_current_profile(self):
        name = self.profile_var.get()
        text = self.text_area.get("0.0", "end-1c")

        if not text.strip():
            messagebox.showwarning("Warning", "Cannot save empty profile")
            return

        if name == "Default":
            name = f"Profile_{len(self.profiles) + 1}"

        self.profiles[name] = text
        self.save_profiles()
        self.update_profile_dropdown()
        self.profile_var.set(name)
        self.profile_dropdown.set(name)
        messagebox.showinfo("Success", f"Profile '{name}' saved!")
    
    def delete_profile(self):
        name = self.profile_var.get()
        if name == "Default":
            messagebox.showwarning("Warning", "Cannot delete Default profile")
            return
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()
            self.profile_var.set("Default")
            self.update_profile_dropdown()
            messagebox.showinfo("Success", f"Profile '{name}' deleted")
    
    def update_profile_dropdown(self):
        values = ["Default"] + list(self.profiles.keys())
        self.profile_dropdown.configure(values=values)
    
    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.text_area.delete("0.0", "end")
                    self.text_area.insert("0.0", content)
                    self.update_char_count()
                    messagebox.showinfo("Success", f"Loaded {len(content)} characters from file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def paste_from_clipboard(self):
        try:
            content = self.root.clipboard_get()
            if content:
                self.text_area.insert("insert", content)
                self.update_char_count()
            else:
                messagebox.showinfo("Info", "Clipboard is empty")
        except tk.TclError:
            messagebox.showinfo("Info", "Clipboard is empty")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {e}")
    
    # ==================== HOTKEY HANDLERS ====================
    def save_hotkey_settings(self):
        self.hotkeys.start = self.start_hotkey_entry.get().lower().strip()
        self.hotkeys.pause = self.pause_hotkey_entry.get().lower().strip()
        self.hotkeys.stop = self.stop_hotkey_entry.get().lower().strip()
        self.save_hotkeys()
        self.restart_hotkey_listener()
        messagebox.showinfo("Success", "Hotkeys saved! Restart may be needed.")
    
    def reset_hotkeys(self):
        self.hotkeys = HotkeyConfig()
        self.start_hotkey_entry.delete(0, "end")
        self.start_hotkey_entry.insert(0, self.hotkeys.start)
        self.pause_hotkey_entry.delete(0, "end")
        self.pause_hotkey_entry.insert(0, self.hotkeys.pause)
        self.stop_hotkey_entry.delete(0, "end")
        self.stop_hotkey_entry.insert(0, self.hotkeys.stop)
        self.save_hotkeys()
        self.restart_hotkey_listener()
        messagebox.showinfo("Success", "Hotkeys reset to default")
    
    def on_press(self, key):
        try:
            key_name = str(key).replace("Key.", "").lower()
            if key_name in ["alt", "ctrl", "shift", "alt_l", "alt_r", "ctrl_l", "ctrl_r", "shift_l", "shift_r"]:
                self.current_modifiers.add(key_name.replace("_l", "").replace("_r", ""))
            elif key_name == "esc":
                # Emergency stop
                self.root.after(0, self.stop_typing)
        except Exception as e:
            logging.error(f"Hotkey press error: {e}")
    
    def on_release(self, key):
        try:
            key_name = str(key).replace("Key.", "").lower()
            is_modifier = key_name.replace("_l", "").replace("_r", "") in ["alt", "ctrl", "shift"]

            if not is_modifier:
                if hasattr(key, 'char') and key.char:
                    pressed_key = key.char.lower()
                else:
                    pressed_key = key_name

                # Build combo matching the saved hotkey format: modifiers sorted + key
                parts = sorted(self.current_modifiers) + [pressed_key]
                combo = "+".join(parts)

                if combo == self.hotkeys.start and not self.is_typing:
                    self.root.after(0, self.start_typing)
                elif combo == self.hotkeys.pause and self.is_typing:
                    self.root.after(0, self.toggle_pause)
                elif combo == self.hotkeys.stop and self.is_typing:
                    self.root.after(0, self.stop_typing)

            # Remove modifier if released
            if is_modifier:
                self.current_modifiers.discard(key_name.replace("_l", "").replace("_r", ""))

        except Exception as e:
            logging.error(f"Hotkey release error: {e}")
    
    def start_hotkey_listener(self):
        self.hotkey_listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()
    
    def restart_hotkey_listener(self):
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        self.start_hotkey_listener()
    
    # ==================== STATS ====================
    def update_stats_display(self):
        self.stats_sessions.configure(text=f"📊 Total Sessions: {self.stats['sessions']}")
        self.stats_chars.configure(text=f"📝 Total Characters: {self.stats['total_chars']:,}")
        avg = self.stats['total_chars'] // self.stats['sessions'] if self.stats['sessions'] > 0 else 0
        self.stats_avg.configure(text=f"📈 Average per Session: {avg:,}")
        self.stats_last.configure(text=f"🕒 Last Session: {self.stats['last_date']} ({self.stats['last_session']} chars)")
    
    def reset_stats(self):
        if messagebox.askyesno("Confirm", "Reset all statistics?"):
            self.stats = {"sessions": 0, "total_chars": 0, "last_session": 0, "last_date": ""}
            self.save_stats()
            self.update_stats_display()
    
    # ==================== TYPING LOGIC ====================
    def start_typing(self):
        text = self.text_area.get("0.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("Warning", "Text area is empty!")
            return
        
        if self.is_typing:
            return
        
        self.is_typing = True
        self.is_paused = False
        self.stop_event.clear()
        
        self.start_btn.configure(state="disabled", fg_color=("#37474f", "#263238"), text_color=("#888888", "#777777"))
        self.pause_btn.configure(state="normal", fg_color=("#2196f3", "#1976d2"), hover_color=("#1976d2", "#1565c0"), text_color=("#ffffff", "#ffffff"))
        self.stop_btn.configure(state="normal", fg_color=("#f44336", "#d32f2f"), hover_color=("#ef5350", "#f44336"), text_color=("#ffffff", "#ffffff"))
        
        self.typing_thread = threading.Thread(target=self.type_text_worker, args=(text,), daemon=True)
        self.typing_thread.start()
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.configure(text="▶️ RESUME", fg_color=("#4caf50", "#388e3c"), hover_color=("#66bb6a", "#4caf50"))
            self.status_label.configure(text="⏸ PAUSED", text_color=("#2196f3", "#64b5f6"))
        else:
            self.pause_btn.configure(text="⏸️ PAUSE", fg_color=("#2196f3", "#1976d2"), hover_color=("#1976d2", "#1565c0"))
            self.status_label.configure(text="⚡ TYPING...", text_color=("#2196f3", "#64b5f6"))
    
    def stop_typing(self):
        self.stop_event.set()
        self.is_typing = False
        self.is_paused = False
        
        self.start_btn.configure(state="normal", fg_color=("#4caf50", "#388e3c"), text_color=("#ffffff", "#ffffff"))
        self.pause_btn.configure(
            state="disabled", 
            text="⏸️ PAUSE",
            fg_color=("#37474f", "#263238"),
            hover_color=("#455a64", "#37474f"),
            text_color=("#888888", "#777777")
        )
        self.stop_btn.configure(
            state="disabled",
            fg_color=("#37474f", "#263238"),
            hover_color=("#455a64", "#37474f"),
            text_color=("#888888", "#777777")
        )
        
        self.status_label.configure(text="⏹ STOPPED", text_color=("#f44336", "#ef5350"))
        self.progress.set(0)
    
    def type_text_worker(self, text):
        try:
            for i in range(self.config.countdown_sec, 0, -1):
                if self.stop_event.is_set():
                    return
                self.root.after(0, lambda sec=i: self.typing_countdown_label.configure(text=f"Starting in {sec}..."))
                self.root.after(0, lambda sec=i: self.status_label.configure(text=f"⏳ COUNTDOWN: {sec}", text_color="#2196f3"))
                time.sleep(1)
            
            self.root.after(0, lambda: self.typing_countdown_label.configure(text=""))
            self.root.after(0, lambda: self.status_label.configure(text="⚡ TYPING...", text_color="#2196f3"))
            
            if self.config.typing_mode == "LineByLine":
                self.type_line_by_line(text)
            else:
                self.type_character_by_character(text)
            
            if not self.stop_event.is_set():
                self.stats["sessions"] += 1
                self.stats["total_chars"] += len(text)
                self.stats["last_session"] = len(text)
                self.stats["last_date"] = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
                self.save_stats()
                
                self.root.after(0, lambda: self.status_label.configure(text="✅ COMPLETED", text_color="#4caf50"))
                self.root.after(0, lambda: self.progress.set(1))
                
                if self.config.sound_enabled:
                    winsound.Beep(800, 200)
                    time.sleep(0.1)
                    winsound.Beep(1000, 200)
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Typing error: {e}"))
        
        finally:
            self.is_typing = False
            self.root.after(0, lambda: self.start_btn.configure(state="normal", fg_color=("#4caf50", "#388e3c"), text_color=("#ffffff", "#ffffff")))
            self.root.after(0, lambda: self.pause_btn.configure(
                state="disabled", 
                text="⏸️ PAUSE",
                fg_color=("#37474f", "#263238"),
                hover_color=("#455a64", "#37474f"),
                text_color=("#888888", "#777777")
            ))
            self.root.after(0, lambda: self.stop_btn.configure(
                state="disabled",
                fg_color=("#37474f", "#263238"),
                hover_color=("#455a64", "#37474f"),
                text_color=("#888888", "#777777")
            ))
    
    def type_character_by_character(self, text):
        total = len(text)
        prev_char = ''
        
        for i, char in enumerate(text):
            while self.is_paused:
                if self.stop_event.is_set():
                    return
                time.sleep(0.1)
            
            if self.stop_event.is_set():
                return
            
            try:
                self.keyboard.type(char)
            except (OSError, RuntimeError) as e:
                logging.warning(f"Typing error for char '{char}': {e}")
            
            rand_range = min(self.config.randomness_ms, self.config.base_delay_ms - 1)
            delay = self.config.base_delay_ms + random.randint(-rand_range, rand_range)
            delay = max(1, delay)

            if char in '.,!?;:':
                delay += self.config.punctuation_delay_ms

            if char == ' ' and prev_char not in ' \n':
                delay += self.config.word_delay_ms

            if random.random() < self.config.thinking_chance:
                delay += self.config.thinking_duration_ms

            time.sleep(delay / 1000.0)
            
            progress = (i + 1) / total
            self.root.after(0, lambda p=progress: self.progress.set(p))
            
            prev_char = char
    
    def type_line_by_line(self, text):
        lines = text.split('\n')
        total_lines = len(lines)
        
        for i, line in enumerate(lines):
            while self.is_paused:
                if self.stop_event.is_set():
                    return
                time.sleep(0.1)
            
            if self.stop_event.is_set():
                return
            
            for char in line:
                if self.stop_event.is_set():
                    return
                
                try:
                    self.keyboard.type(char)
                except (OSError, RuntimeError) as e:
                    logging.warning(f"Typing error for char '{char}': {e}")
                
                delay = self.config.base_delay_ms + random.randint(-self.config.randomness_ms, self.config.randomness_ms)
                delay = max(1, delay)
                time.sleep(delay / 1000.0)
            
            if i < total_lines - 1:
                try:
                    self.keyboard.press(Key.enter)
                    self.keyboard.release(Key.enter)
                    time.sleep(self.config.line_break_delay_ms / 1000.0)
                except (OSError, RuntimeError) as e:
                    logging.warning(f"Enter key error: {e}")
            
            progress = (i + 1) / total_lines
            self.root.after(0, lambda p=progress: self.progress.set(p))
    
    def toggle_size(self):
        """Cycle through: Normal -> Compact -> Small -> Normal"""
        self.size_mode = (self.size_mode + 1) % 3
        
        if self.size_mode == 0:
            # Normal mode - Large window
            self.root.minsize(1200, 750)
            self.root.geometry("1350x850")
            self.size_btn.configure(text="💻 Normal")
            self.show_size_notification("Normal Size", "Full workspace")
            
        elif self.size_mode == 1:
            # Compact mode - Medium window
            self.root.minsize(850, 600)
            self.root.geometry("900x650")
            self.size_btn.configure(text="📱 Compact")
            self.show_size_notification("Compact Size", "Optimized layout")
            
        else:
            # Small mode - Small window
            self.root.minsize(650, 500)
            self.root.geometry("700x550")
            self.size_btn.configure(text="📱 Small")
            self.show_size_notification("Small Size", "Minimal workspace")
    
    def show_size_notification(self, title, message):
        """Show a temporary notification for size change"""
        # Create notification label
        notif = ctk.CTkLabel(
            self.root,
            text=f"✨ {title}\n{message}",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#1a1a2e", "#0f0f1e"),
            corner_radius=10,
            padx=20,
            pady=15
        )
        notif.place(relx=0.5, rely=0.95, anchor="center")
        
        # Auto-hide after 2 seconds
        self.root.after(2000, notif.destroy)
    
    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/mrsoulcommunity")

    def open_telegram(self):
        import webbrowser
        webbrowser.open("https://t.me/mrsoul_community")
    
    # ==================== CLEANUP ====================
    def on_closing(self):
        self.stop_typing()
        self.save_last_text()
        self.save_config()
        
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
        
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AutoTyper()
    app.run()