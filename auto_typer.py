import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
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
from typing import Dict, Optional
from pynput.keyboard import Controller, Key, Listener


@dataclass
class TypingConfig:
    base_delay_ms: int = 85
    randomness_ms: int = 20
    typing_mode: str = "Human"
    line_break_delay_ms: int = 200
    punctuation_delay_ms: int = 150
    word_delay_ms: int = 80
    thinking_chance: float = 0.02
    thinking_duration_ms: int = 400
    countdown_sec: int = 3
    sound_enabled: bool = True
    auto_save_interval_sec: int = 5
    size_mode: int = 0


@dataclass
class HotkeyConfig:
    start: str = "alt+s"
    pause: str = "alt+p"
    stop: str = "alt+x"


class AutoTyper:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.logs_dir = "logs"
        self.data_dir = "data"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

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
        self.root.minsize(1200, 750)

        w, h = 1350, 850
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.is_typing = False
        self.is_paused = False
        self.stop_event = threading.Event()
        self.typing_thread: Optional[threading.Thread] = None
        self.size_mode = 0
        self.auto_save_timer: Optional[threading.Timer] = None
        self.text_modified = False

        self.keyboard = Controller()
        self.config = self.load_config()
        self.size_mode = self.config.size_mode
        self.hotkeys = self.load_hotkeys()
        self.profiles: Dict[str, str] = self.load_profiles()
        self.stats = self.load_stats()
        self.autosave_enabled = tk.BooleanVar(value=True)

        self.bg_color = "#070b14"
        self.card_color = "#111827"
        self.panel_color = "#111f2f"
        self.border_color = "#1f2937"
        self.primary_text = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.accent_color = "#60a5fa"
        self.success_color = "#3fb950"
        self.warning_color = "#f59e0b"
        self.error_color = "#f85149"
        self.disabled_text = "#484f58"

        self.current_modifiers = set()
        self.hotkey_listener = None

        self.setup_ui()
        self.apply_size_mode()
        self.load_last_text()
        self.start_auto_save()
        self.start_hotkey_listener()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Failed to load profiles_v4.json: {e}")
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
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Failed to load stats_v4.json: {e}")
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

    def setup_ui(self):
        self.root.configure(fg_color=self.bg_color)

        header = ctk.CTkFrame(self.root, height=74, corner_radius=0, fg_color=self.card_color)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=24, pady=0)
        title_frame.pack_propagate(False)

        ctk.CTkLabel(title_frame, text="⌨️", font=ctk.CTkFont(size=28)).pack(side="left", padx=(0, 12))

        title_container = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_container.pack(side="left")

        ctk.CTkLabel(title_container, text="Auto Typer", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color=self.primary_text).pack(anchor="w")
        ctk.CTkLabel(title_container, text="v4.0  ·  Advanced Edition", font=ctk.CTkFont(size=10), text_color=self.secondary_text).pack(anchor="w")

        right_header = ctk.CTkFrame(header, fg_color="transparent")
        right_header.pack(side="right", padx=20, pady=12)

        mode_tag = ctk.CTkLabel(
            right_header,
            text=f"⚡ {self.config.typing_mode}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.accent_color,
            fg_color=self.panel_color,
            corner_radius=10,
            padx=14, pady=6
        )
        mode_tag.pack(side="right", padx=(0, 8))
        self.mode_tag = mode_tag

        self.size_btn = ctk.CTkButton(
            right_header, text="Normal", command=self.toggle_size,
            width=100, height=34, corner_radius=10,
            fg_color=self.bg_color, hover_color=self.panel_color,
            border_width=1, border_color=self.border_color,
            text_color=self.primary_text, font=ctk.CTkFont(size=11, weight="bold")
        )
        self.size_btn.pack(side="right", padx=(8, 0))

        mode_tag.pack(side="right", padx=(8, 0))
        self.mode_tag = mode_tag

        sep = ctk.CTkFrame(self.root, height=1, corner_radius=0, fg_color=self.border_color)
        sep.pack(fill="x")

        main = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        main.pack(fill="both", expand=True, padx=12, pady=12)

        left = ctk.CTkFrame(main, width=660, fg_color=self.bg_color)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        left.pack_propagate(False)

        right = ctk.CTkFrame(main, width=440, fg_color=self.bg_color)
        right.pack(side="right", fill="both", expand=True, padx=(6, 0))
        right.pack_propagate(False)

        self.setup_text_panel(left)
        self.setup_control_panel(left)
        self.setup_advanced_settings(right)

    def setup_text_panel(self, parent):
        toolbar = ctk.CTkFrame(parent, height=46, corner_radius=8, fg_color=self.card_color, border_width=1, border_color=self.border_color)
        toolbar.pack(fill="x", pady=(0, 8))
        toolbar.pack_propagate(False)

        ctk.CTkLabel(toolbar, text="Text Editor", font=ctk.CTkFont(size=13, weight="bold"), text_color="#e6edf3").pack(side="left", padx=16)

        ctk.CTkFrame(toolbar, width=1, height=24, fg_color="#30363d").pack(side="left", padx=10)

        ctk.CTkLabel(toolbar, text="Profile", font=ctk.CTkFont(size=11), text_color="#8b949e").pack(side="left", padx=(4, 6))
        self.profile_var = tk.StringVar(value="Default")
        self.profile_dropdown = ctk.CTkComboBox(
            toolbar, values=["Default"] + list(self.profiles.keys()),
            variable=self.profile_var, width=140, height=30, corner_radius=6,
            fg_color="#21262d", border_color="#30363d", button_color="#30363d",
            button_hover_color="#388bfd", text_color="#c9d1d9",
            command=self.on_profile_change
        )
        self.profile_dropdown.pack(side="left", padx=(0, 6))

        for text, cmd, color, hcolor in [
            ("New",    self.new_profile,         "#0f172a", "#1e293b"),
            ("Clear",  self.clear_text,           "#0f172a", "#1e293b"),
            ("Save",   self.save_current_profile, "#1f6feb", "#388bfd"),
            ("Delete", self.delete_profile,        "#da3633", "#f85149"),
            ("Load",   self.load_from_file,        "#21262d", "#30363d"),
            ("Paste",  self.paste_from_clipboard,  "#21262d", "#30363d"),
        ]:
            ctk.CTkButton(toolbar, text=text, width=70, height=30, corner_radius=6,
                fg_color=color, hover_color=hcolor,
                text_color="#e6edf3", font=ctk.CTkFont(size=11),
                command=cmd).pack(side="left", padx=2)

        self.save_indicator = ctk.CTkLabel(toolbar, text="● Saved",
            font=ctk.CTkFont(size=11), text_color="#3fb950")
        self.save_indicator.pack(side="right", padx=16)

        text_container = ctk.CTkFrame(parent, corner_radius=8, fg_color=self.card_color, border_width=1, border_color=self.border_color)
        text_container.pack(fill="both", expand=True, pady=(0, 8))

        self.text_area = ctk.CTkTextbox(
            text_container,
            font=ctk.CTkFont(family="Consolas", size=13),
            wrap="word", corner_radius=8,
            fg_color="#0d1117", text_color="#c9d1d9",
            border_width=0
        )
        self.text_area.pack(fill="both", expand=True, padx=6, pady=6)
        self.text_area.bind("<KeyRelease>", self.on_text_change)

        status = ctk.CTkFrame(parent, height=36, corner_radius=8, fg_color=self.card_color, border_width=1, border_color=self.border_color)
        status.pack(fill="x")
        status.pack_propagate(False)

        self.char_label = ctk.CTkLabel(status, text="Chars: 0", font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.char_label.pack(side="left", padx=14)

        ctk.CTkFrame(status, width=1, height=16, fg_color="#30363d").pack(side="left", padx=6)

        self.line_label = ctk.CTkLabel(status, text="Lines: 0", font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.line_label.pack(side="left", padx=6)

        ctk.CTkFrame(status, width=1, height=16, fg_color="#30363d").pack(side="left", padx=6)

        self.word_label = ctk.CTkLabel(status, text="Words: 0", font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.word_label.pack(side="left", padx=6)

        self.auto_save_label = ctk.CTkLabel(status, text="Auto-save: ON", font=ctk.CTkFont(size=11), text_color="#3fb950")
        self.auto_save_label.pack(side="right", padx=14)

    def setup_control_panel(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=8, fg_color="#161b22", border_width=1, border_color="#21262d")
        frame.pack(fill="x", pady=(8, 0))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=14)

        self.start_btn = ctk.CTkButton(
            btn_frame, text="START", command=self.start_typing,
            width=150, height=44, font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8, fg_color="#238636", hover_color="#2ea043",
            text_color="#ffffff", border_width=0
        )
        self.start_btn.pack(side="left", padx=8)

        self.pause_btn = ctk.CTkButton(
            btn_frame, text="PAUSE", command=self.toggle_pause,
            width=150, height=44, font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8, state="disabled",
            fg_color="#21262d", hover_color="#30363d",
            border_width=1, border_color="#30363d",
            text_color="#484f58"
        )
        self.pause_btn.pack(side="left", padx=8)

        self.stop_btn = ctk.CTkButton(
            btn_frame, text="STOP", command=self.stop_typing,
            width=150, height=44, font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8, state="disabled",
            fg_color="#21262d", hover_color="#30363d",
            border_width=1, border_color="#30363d",
            text_color="#484f58"
        )
        self.stop_btn.pack(side="left", padx=8)

        progress_container = ctk.CTkFrame(frame, fg_color="transparent")
        progress_container.pack(fill="x", padx=20, pady=(0, 10))

        self.progress = ctk.CTkProgressBar(progress_container, height=4, corner_radius=2,
            border_width=0, fg_color="#21262d", progress_color="#1f6feb")
        self.progress.pack(fill="x")
        self.progress.set(0)

        bottom_row = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_row.pack(fill="x", padx=20, pady=(0, 14))

        self.status_label = ctk.CTkLabel(bottom_row, text="● READY",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#3fb950")
        self.status_label.pack(side="left")

        self.typing_countdown_label = ctk.CTkLabel(bottom_row, text="",
            font=ctk.CTkFont(size=13), text_color="#58a6ff")
        self.typing_countdown_label.pack(side="right")

    def setup_advanced_settings(self, parent):
        tabview = ctk.CTkTabview(parent,
            fg_color="#161b22",
            segmented_button_fg_color="#161b22",
            segmented_button_selected_color="#21262d",
            segmented_button_selected_hover_color="#30363d",
            segmented_button_unselected_color="#161b22",
            segmented_button_unselected_hover_color="#1c2128",
            text_color="#8b949e",
            text_color_disabled="#484f58",
            border_width=1, border_color="#21262d",
            corner_radius=8)
        tabview.pack(fill="both", expand=True)

        self.setup_modes_tab(tabview.add("Modes"))
        self.setup_advanced_timing_tab(tabview.add("Timing"))
        self.setup_hotkey_tab(tabview.add("Keys"))
        self.setup_stats_tab(tabview.add("Stats"))
        self.setup_autosave_tab(tabview.add("More"))

    def setup_modes_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", scrollbar_button_color="#21262d")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Typing Mode", font=ctk.CTkFont(size=14, weight="bold"), text_color="#e6edf3").pack(anchor="w", pady=(0, 12))

        modes = [
            ("Burst",        "Burst",      "Ultra-fast, minimal delays"),
            ("Human",        "Human",      "Natural typing with variations"),
            ("Stealth",      "Stealth",    "Very slow, avoids detection"),
            ("Line-by-Line", "LineByLine", "Types line by line with Enter"),
        ]

        self.mode_var = tk.StringVar(value=self.config.typing_mode)

        for title, value, desc in modes:
            is_active = value == self.config.typing_mode
            bc = "#1f6feb" if is_active else "#21262d"
            mode_frame = ctk.CTkFrame(frame, corner_radius=6, fg_color="#1c2128", border_width=1, border_color=bc)
            mode_frame.pack(fill="x", pady=4)

            row = ctk.CTkFrame(mode_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=10)

            ctk.CTkRadioButton(row, text=title, variable=self.mode_var, value=value,
                command=self.on_mode_change,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#e6edf3",
                fg_color="#1f6feb", hover_color="#388bfd"
            ).pack(side="left")
            ctk.CTkLabel(row, text=desc, font=ctk.CTkFont(size=10), text_color="#6e7681").pack(side="right")

        ctk.CTkButton(frame, text="Apply Mode", command=self.apply_mode,
            fg_color="#1f6feb", hover_color="#388bfd",
            text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"),
            height=38, corner_radius=6).pack(pady=(16, 0), fill="x")

    def _slider_row(self, parent, label, slider_attr, label_attr, from_, to, val, label_text, cmd):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color="#c9d1d9").pack(anchor="w", pady=(10, 2))
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        s = ctk.CTkSlider(row, from_=from_, to=to, fg_color="#21262d", progress_color="#1f6feb", button_color="#58a6ff", button_hover_color="#79c0ff")
        s.set(val)
        s.pack(side="left", fill="x", expand=True, pady=3)
        lbl = ctk.CTkLabel(row, text=label_text, font=ctk.CTkFont(size=10), text_color="#6e7681", width=72, anchor="e")
        lbl.pack(side="right", padx=(8, 0))
        setattr(self, slider_attr, s)
        setattr(self, label_attr, lbl)
        s.configure(command=cmd)

    def setup_advanced_timing_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", scrollbar_button_color="#21262d")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Timing", font=ctk.CTkFont(size=14, weight="bold"), text_color="#e6edf3").pack(anchor="w", pady=(0, 4))

        self._slider_row(frame, "Base Delay", "delay_slider", "delay_label", 20, 500, self.config.base_delay_ms, f"{self.config.base_delay_ms} ms", self.on_delay_change)
        self._slider_row(frame, "Randomness", "random_slider", "random_label", 0, 150, self.config.randomness_ms, f"±{self.config.randomness_ms} ms", self.on_random_change)
        self._slider_row(frame, "Punctuation Delay", "punct_slider", "punct_label", 0, 300, self.config.punctuation_delay_ms, f"{self.config.punctuation_delay_ms} ms", self.on_punct_change)
        self._slider_row(frame, "Between Words Delay", "word_slider", "word_label", 0, 200, self.config.word_delay_ms, f"{self.config.word_delay_ms} ms", self.on_word_change)
        self._slider_row(frame, "Thinking Chance", "think_slider", "think_label", 0, 10, self.config.thinking_chance * 100, f"{self.config.thinking_chance * 100:.0f}%", self.on_think_change)
        self._slider_row(frame, "Countdown", "countdown_slider", "countdown_val_label", 1, 10, self.config.countdown_sec, f"{self.config.countdown_sec} sec", self.on_countdown_change)

        self.sound_var = tk.BooleanVar(value=self.config.sound_enabled)
        ctk.CTkCheckBox(frame, text="Play sound on completion", variable=self.sound_var,
            text_color="#c9d1d9", fg_color="#1f6feb", hover_color="#388bfd",
            checkmark_color="#ffffff", border_color="#30363d").pack(anchor="w", pady=(14, 0))

        ctk.CTkButton(frame, text="Save Settings", command=self.save_timing_settings,
            fg_color="#238636", hover_color="#2ea043",
            text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"),
            height=38, corner_radius=6).pack(pady=(16, 0), fill="x")

    def setup_hotkey_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", scrollbar_button_color="#21262d")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Hotkeys", font=ctk.CTkFont(size=14, weight="bold"), text_color="#e6edf3").pack(anchor="w", pady=(0, 12))

        entry_style = dict(fg_color="#1c2128", border_color="#30363d", text_color="#c9d1d9", placeholder_text_color="#484f58")

        for label, attr, placeholder in [
            ("Start Typing",  "start_hotkey_entry", "e.g., alt+s"),
            ("Pause/Resume",  "pause_hotkey_entry", "e.g., alt+p"),
            ("Stop",          "stop_hotkey_entry",  "e.g., alt+x"),
        ]:
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11), text_color="#8b949e").pack(anchor="w", pady=(8, 2))
            e = ctk.CTkEntry(frame, placeholder_text=placeholder, height=34, corner_radius=6, **entry_style)
            e.insert(0, getattr(self.hotkeys, attr.replace("_hotkey_entry", "").replace("start", "start").replace("pause", "pause").replace("stop", "stop")))
            e.pack(fill="x")
            setattr(self, attr, e)

        self.start_hotkey_entry.delete(0, "end")
        self.start_hotkey_entry.insert(0, self.hotkeys.start)
        self.pause_hotkey_entry.delete(0, "end")
        self.pause_hotkey_entry.insert(0, self.hotkeys.pause)
        self.stop_hotkey_entry.delete(0, "end")
        self.stop_hotkey_entry.insert(0, self.hotkeys.stop)

        ctk.CTkButton(frame, text="Save Hotkeys", command=self.save_hotkey_settings,
            fg_color="#238636", hover_color="#2ea043",
            text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"),
            height=38, corner_radius=6).pack(pady=(14, 0), fill="x")

        ctk.CTkLabel(frame, text="Supported: alt / ctrl / shift + key  ·  f1–f12",
            font=ctk.CTkFont(size=10), text_color="#484f58").pack(anchor="w", pady=(10, 0))

        ctk.CTkButton(frame, text="Reset to Default", command=self.reset_hotkeys,
            fg_color="#21262d", hover_color="#30363d",
            border_width=1, border_color="#30363d",
            text_color="#8b949e", font=ctk.CTkFont(size=12),
            height=34, corner_radius=6).pack(pady=(8, 0), fill="x")

    def setup_stats_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", scrollbar_button_color="#21262d")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Statistics", font=ctk.CTkFont(size=14, weight="bold"), text_color="#e6edf3").pack(anchor="w", pady=(0, 12))

        stats_card = ctk.CTkFrame(frame, corner_radius=8, fg_color="#1c2128", border_width=1, border_color="#21262d")
        stats_card.pack(fill="x")

        self.stats_sessions = ctk.CTkLabel(stats_card, text="", font=ctk.CTkFont(size=13, weight="bold"), text_color="#e6edf3")
        self.stats_sessions.pack(anchor="w", padx=16, pady=(14, 4))

        self.stats_chars = ctk.CTkLabel(stats_card, text="", font=ctk.CTkFont(size=12), text_color="#8b949e")
        self.stats_chars.pack(anchor="w", padx=16, pady=3)

        self.stats_avg = ctk.CTkLabel(stats_card, text="", font=ctk.CTkFont(size=12), text_color="#8b949e")
        self.stats_avg.pack(anchor="w", padx=16, pady=3)

        self.stats_last = ctk.CTkLabel(stats_card, text="", font=ctk.CTkFont(size=11), text_color="#6e7681")
        self.stats_last.pack(anchor="w", padx=16, pady=(3, 14))

        ctk.CTkButton(frame, text="Refresh", command=self.update_stats_display,
            fg_color="#1f6feb", hover_color="#388bfd",
            text_color="#ffffff", height=36, corner_radius=6,
            font=ctk.CTkFont(size=12)).pack(pady=(12, 4), fill="x")

        ctk.CTkButton(frame, text="Reset Statistics", command=self.reset_stats,
            fg_color="#21262d", hover_color="#da3633",
            border_width=1, border_color="#da3633",
            text_color="#f85149", height=34, corner_radius=6,
            font=ctk.CTkFont(size=12)).pack(fill="x")

        self.update_stats_display()

    def setup_autosave_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", scrollbar_button_color="#21262d")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Settings", font=ctk.CTkFont(size=14, weight="bold"), text_color="#e6edf3").pack(anchor="w", pady=(0, 12))

        autosave_card = ctk.CTkFrame(frame, corner_radius=8, fg_color="#1c2128", border_width=1, border_color="#21262d")
        autosave_card.pack(fill="x")

        ctk.CTkLabel(autosave_card, text="Auto-Save", font=ctk.CTkFont(size=12, weight="bold"), text_color="#c9d1d9").pack(anchor="w", padx=14, pady=(12, 6))

        ctk.CTkLabel(autosave_card, text="Interval (seconds)", font=ctk.CTkFont(size=11), text_color="#8b949e").pack(anchor="w", padx=14)
        row = ctk.CTkFrame(autosave_card, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=4)
        self.autosave_slider = ctk.CTkSlider(row, from_=2, to=30, number_of_steps=28,
            fg_color="#21262d", progress_color="#1f6feb", button_color="#58a6ff", button_hover_color="#79c0ff")
        self.autosave_slider.set(self.config.auto_save_interval_sec)
        self.autosave_slider.pack(side="left", fill="x", expand=True)
        self.autosave_label = ctk.CTkLabel(row, text=f"Every {self.config.auto_save_interval_sec}s", font=ctk.CTkFont(size=10), text_color="#6e7681", width=60, anchor="e")
        self.autosave_label.pack(side="right", padx=(8, 0))
        self.autosave_slider.configure(command=self.on_autosave_change)

        ctk.CTkCheckBox(autosave_card, text="Enable Auto-Save", variable=self.autosave_enabled,
            command=self.toggle_autosave, text_color="#c9d1d9",
            fg_color="#1f6feb", hover_color="#388bfd", checkmark_color="#ffffff",
            border_color="#30363d").pack(anchor="w", padx=14, pady=(6, 12))

        ctk.CTkButton(frame, text="Save Settings", command=self.save_autosave_settings,
            fg_color="#238636", hover_color="#2ea043",
            text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"),
            height=38, corner_radius=6).pack(pady=(10, 0), fill="x")

        ctk.CTkFrame(frame, height=1, fg_color="#21262d").pack(fill="x", pady=16)

        ctk.CTkLabel(frame, text="• data/  —  settings & profiles\n• logs/   —  application logs",
            font=ctk.CTkFont(size=10), text_color="#484f58", justify="left").pack(anchor="w")

        ctk.CTkFrame(frame, height=1, fg_color="#21262d").pack(fill="x", pady=16)

        ctk.CTkLabel(frame, text="Social", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8b949e").pack(anchor="w", pady=(0, 8))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(btn_row, text="GitHub", command=self.open_github,
            fg_color="#21262d", hover_color="#30363d",
            border_width=1, border_color="#30363d",
            text_color="#c9d1d9", height=36, corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))

        ctk.CTkButton(btn_row, text="Telegram", command=self.open_telegram,
            fg_color="#21262d", hover_color="#30363d",
            border_width=1, border_color="#30363d",
            text_color="#c9d1d9", height=36, corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", expand=True, fill="x", padx=(4, 0))

    def on_mode_change(self):
        mode = self.mode_var.get()
        self.mode_tag.configure(text=f"⚡ {mode}")

        presets = {
            "Burst":      (20,  5),
            "Human":      (85,  25),
            "Stealth":    (180, 50),
            "LineByLine": (60,  15),
        }
        if mode in presets:
            d, r = presets[mode]
            self.delay_slider.set(d)
            self.random_slider.set(r)
            self.delay_label.configure(text=f"Value: {d} ms")
            self.random_label.configure(text=f"Value: ±{r} ms")

    def apply_mode(self):
        self.config.typing_mode = self.mode_var.get()

        presets = {
            "Burst":      (20, 5, 0, 0, 0),
            "Human":      (85, 25, 150, 80, 0.02),
            "Stealth":    (180, 50, 250, 150, 0.05),
            "LineByLine": (60, 15, 100, 50, 0.01),
        }
        d, r, p, w, t = presets[self.config.typing_mode]
        self.config.base_delay_ms = d
        self.config.randomness_ms = r
        self.config.punctuation_delay_ms = p
        self.config.word_delay_ms = w
        self.config.thinking_chance = t

        self.delay_slider.set(d)
        self.random_slider.set(r)
        self.punct_slider.set(p)
        self.word_slider.set(w)
        self.think_slider.set(t * 100)

        self.delay_label.configure(text=f"Value: {d} ms")
        self.random_label.configure(text=f"Value: ±{r} ms")
        self.punct_label.configure(text=f"Value: {p} ms")
        self.word_label.configure(text=f"Value: {w} ms")
        self.think_label.configure(text=f"Value: {t * 100:.0f}%")

        self.mode_tag.configure(text=f"⚡ {self.config.typing_mode}")
        self.save_config()
        messagebox.showinfo("Success", f"Mode changed to {self.config.typing_mode}")

    def on_delay_change(self, value):
        self.delay_label.configure(text=f"{int(value)} ms")

    def on_random_change(self, value):
        self.random_label.configure(text=f"±{int(value)} ms")

    def on_punct_change(self, value):
        self.punct_label.configure(text=f"{int(value)} ms")

    def on_word_change(self, value):
        self.word_label.configure(text=f"{int(value)} ms")

    def on_think_change(self, value):
        self.think_label.configure(text=f"{int(value)}%")

    def on_countdown_change(self, value):
        self.countdown_val_label.configure(text=f"{int(value)} sec")

    def on_autosave_change(self, value):
        self.autosave_label.configure(text=f"Every {int(value)}s")

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
        self.char_label.configure(text=f"Chars: {chars}")
        self.line_label.configure(text=f"Lines: {lines}")
        self.word_label.configure(text=f"Words: {words}")

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
            self.profile_dropdown.set("Default")
            self.update_profile_dropdown()
            self.text_area.delete("0.0", "end")
            self.update_char_count()
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
                    self.text_modified = True
                    self.save_indicator.configure(text="● Unsaved", text_color=self.error_color)
                    messagebox.showinfo("Success", f"Loaded {len(content)} characters from file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def new_profile(self):
        name = simpledialog.askstring("New Profile", "Enter a new profile name:", parent=self.root)
        if not name:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Warning", "Profile name cannot be empty.")
            return
        if name in self.profiles:
            if not messagebox.askyesno("Confirm", f"Profile '{name}' already exists. Load it?"):
                return
            self.text_area.delete("0.0", "end")
            self.text_area.insert("0.0", self.profiles[name])
        else:
            self.profiles[name] = ""
            self.save_profiles()
            self.update_profile_dropdown()
            self.text_area.delete("0.0", "end")

        self.profile_var.set(name)
        self.profile_dropdown.set(name)
        self.update_char_count()
        self.text_modified = True
        self.save_indicator.configure(text="● Unsaved", text_color=self.error_color)

    def clear_text(self):
        if messagebox.askyesno("Confirm", "Clear all text from the editor?"):
            self.text_area.delete("0.0", "end")
            self.update_char_count()
            self.text_modified = True
            self.save_indicator.configure(text="● Unsaved", text_color=self.error_color)

    def show_help(self):
        messagebox.showinfo("Help", "Auto Typer Help:\n\n- Use the buttons or hotkeys to control typing.\n- Load text from a file or paste from clipboard.\n- Save and manage profiles from the toolbar.\n- Use File → New Profile to create a blank profile.\n- Toggle size mode with the top button.")

    def show_about(self):
        messagebox.showinfo("About", "Auto Typer v4.0\nAdvanced Edition\nBuilt with Python and customtkinter.")

    def paste_from_clipboard(self):
        try:
            content = self.root.clipboard_get()
            if content:
                self.text_area.insert("insert", content)
                self.update_char_count()
                self.text_modified = True
                self.save_indicator.configure(text="● Unsaved", text_color=self.error_color)
            else:
                messagebox.showinfo("Info", "Clipboard is empty")
        except tk.TclError:
            messagebox.showinfo("Info", "Clipboard is empty")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {e}")

    def save_hotkey_settings(self):
        start_key = self.start_hotkey_entry.get().lower().strip()
        pause_key = self.pause_hotkey_entry.get().lower().strip()
        stop_key = self.stop_hotkey_entry.get().lower().strip()

        if not start_key or not pause_key or not stop_key:
            messagebox.showwarning("Warning", "Please enter valid hotkeys for all actions.")
            return

        self.hotkeys.start = start_key
        self.hotkeys.pause = pause_key
        self.hotkeys.stop = stop_key
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
                self.root.after(0, self.stop_typing)
        except Exception as e:
            logging.error(f"Hotkey press error: {e}")

    def on_release(self, key):
        try:
            key_name = str(key).replace("Key.", "").lower()
            is_modifier = key_name.replace("_l", "").replace("_r", "") in ["alt", "ctrl", "shift"]

            if not is_modifier:
                pressed_key = key.char.lower() if hasattr(key, 'char') and key.char else key_name
                combo = "+".join(sorted(self.current_modifiers) + [pressed_key])

                if combo == self.hotkeys.start and not self.is_typing:
                    self.root.after(0, self.start_typing)
                elif combo == self.hotkeys.pause and self.is_typing:
                    self.root.after(0, self.toggle_pause)
                elif combo == self.hotkeys.stop and self.is_typing:
                    self.root.after(0, self.stop_typing)

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

        self.start_btn.configure(state="disabled", fg_color="#21262d", text_color="#484f58")
        self.pause_btn.configure(state="normal", fg_color="#1f6feb", hover_color="#388bfd", border_width=0, text_color="#ffffff")
        self.stop_btn.configure(state="normal", fg_color="#da3633", hover_color="#f85149", border_width=0, text_color="#ffffff")

        self.typing_thread = threading.Thread(target=self.type_text_worker, args=(text,), daemon=True)
        self.typing_thread.start()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.configure(text="RESUME", fg_color="#238636", hover_color="#2ea043")
            self.status_label.configure(text="● PAUSED", text_color="#58a6ff")
        else:
            self.pause_btn.configure(text="PAUSE", fg_color="#1f6feb", hover_color="#388bfd")
            self.status_label.configure(text="● TYPING...", text_color="#58a6ff")

    def stop_typing(self):
        if not self.is_typing:
            return
        self.stop_event.set()
        self.is_typing = False
        self.is_paused = False

        self.start_btn.configure(state="normal", fg_color="#238636", hover_color="#2ea043", text_color="#ffffff")
        self.pause_btn.configure(state="disabled", text="PAUSE",
            fg_color="#21262d", hover_color="#30363d", border_width=1, border_color="#30363d", text_color="#484f58")
        self.stop_btn.configure(state="disabled",
            fg_color="#21262d", hover_color="#30363d", border_width=1, border_color="#30363d", text_color="#484f58")

        self.status_label.configure(text="● STOPPED", text_color="#f85149")
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

                self.root.after(0, lambda: self.status_label.configure(text="● DONE", text_color="#3fb950"))
                self.root.after(0, lambda: self.progress.set(1))
                self.root.after(3000, lambda: self.status_label.configure(text="● READY", text_color="#3fb950"))

                if self.config.sound_enabled:
                    winsound.Beep(800, 200)
                    time.sleep(0.1)
                    winsound.Beep(1000, 200)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Typing error: {e}"))

        finally:
            self.is_typing = False
            self.root.after(0, lambda: self.start_btn.configure(state="normal", fg_color="#238636", hover_color="#2ea043", text_color="#ffffff"))
            self.root.after(0, lambda: self.pause_btn.configure(
                state="disabled", text="PAUSE",
                fg_color="#21262d", hover_color="#30363d", border_width=1, border_color="#30363d", text_color="#484f58"
            ))
            self.root.after(0, lambda: self.stop_btn.configure(
                state="disabled",
                fg_color="#21262d", hover_color="#30363d", border_width=1, border_color="#30363d", text_color="#484f58"
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

                rand_range = min(self.config.randomness_ms, self.config.base_delay_ms - 1)
                delay = self.config.base_delay_ms + random.randint(-rand_range, rand_range)
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

    def apply_size_mode(self, show_notification: bool = False):
        if self.size_mode == 0:
            self.root.minsize(1200, 750)
            self.root.geometry("1350x850")
            self.size_btn.configure(text="Normal")
            if show_notification:
                self.show_size_notification("Normal", "Full workspace")
        else:
            self.root.minsize(650, 500)
            self.root.geometry("700x550")
            self.size_btn.configure(text="Small")
            if show_notification:
                self.show_size_notification("Small", "Minimal workspace")

    def toggle_size(self):
        self.size_mode = 1 - self.size_mode
        self.config.size_mode = self.size_mode
        self.save_config()
        self.apply_size_mode(show_notification=True)

    def show_size_notification(self, title, message):
        notif = ctk.CTkLabel(
            self.root, text=f"{title}  ·  {message}",
            font=ctk.CTkFont(size=11),
            fg_color="#161b22", text_color="#8b949e",
            corner_radius=6, padx=16, pady=8
        )
        notif.place(relx=0.5, rely=0.97, anchor="center")
        self.root.after(2000, notif.destroy)

    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/mrsoulcommunity")

    def open_telegram(self):
        import webbrowser
        webbrowser.open("https://t.me/mrsoul_community")

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
