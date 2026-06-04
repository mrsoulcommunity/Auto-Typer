# ⌨️ Auto Typer v4.0

A polished auto-typing utility with human-like typing, hotkey control, profiles, and a modern dark UI.

---

## 🚀 What’s new
- Dark-styled UI with Small / Normal window modes
- Built-in profile management for saving text snippets
- Hotkeys for start / pause / stop typing
- Auto-save and recovery of text content
- Standalone Windows executable available in `dist/AutoTyper.exe`

---

## 📥 Requirements
- Windows
- Python 3.8+
- `customtkinter`, `pynput`, `pyperclip`

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## ▶️ Run the app
### From source
```bash
python auto_typer.py
```

### Shortcut
Double-click `run.bat`.

### Executable
Use the ready-made build:
```text
dist\AutoTyper.exe
```

---

## 🛠️ Build a new executable
A helper batch file is available:
```bash
build_exe.bat
```

It installs dependencies and runs PyInstaller to create a one-file executable.

---

## ⚡ Typing Modes
| Mode | Description |
|------|-------------|
| **Burst** | Ultra-fast typing with minimal delay. Good for simple text fields and short input. |
| **Human** | Natural typing behavior with delay variation. Best for realistic typing. |
| **Stealth** | Slow typing with longer pauses to avoid automated detection. |
| **Line-by-Line** | Types text one line at a time and presses Enter after each line. Useful for code or multi-line output. |

---

## ⚙️ Settings Overview
### ⏱️ Timing
| Option | Description |
|--------|-------------|
| **Base Delay** | Delay between each character (ms) |
| **Randomness** | Variation added to delay for more natural typing |
| **Punctuation Delay** | Extra pause after punctuation marks |
| **Between Words Delay** | Pause between words |
| **Thinking Chance** | Random pause chance to simulate thinking |
| **Countdown** | Delay before typing starts |

### ⌨️ Hotkeys
| Hotkey | Default | Action |
|--------|---------|--------|
| Start | `Alt+S` | Start typing |
| Pause | `Alt+P` | Pause / resume |
| Stop | `Alt+X` | Stop typing |
| Emergency | `ESC` | Force stop |

> Hotkeys can be changed in the **Keys** tab. Supported modifiers: `alt`, `ctrl`, `shift`, plus any key or `f1`–`f12`.

### 📂 Profiles
Save text snippets as profiles and switch quickly from the dropdown menu.

### 💾 Auto-Save
Auto-save runs on a configurable interval and prevents text loss. Adjust the interval in the **More** tab.

---

## 📊 Statistics
View usage stats in the **Stats** tab:
- Total sessions
- Total characters typed
- Average characters per session
- Last session timestamp

---

## 📁 Project structure
- `auto_typer.py` — main application file
- `requirements.txt` — dependency list
- `run.bat` — launch script
- `build_exe.bat` — create standalone exe
- `data/` — saved settings, profiles, last text, and stats
- `logs/` — application logs
- `dist/` — built executable output

---

## 💡 Notes
- If the app is packaged as `AutoTyper.exe`, keep the `data/` folder next to it for settings persistence.
- Use the `Small`/`Normal` toggle to switch window layouts quickly.

---

## 🌐 Social
- GitHub: [github.com/mrsoulcommunity](https://github.com/mrsoulcommunity)
- Telegram: [t.me/mrsoul_community](https://t.me/mrsoul_community)
