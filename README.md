# ⌨️ Auto Typer v4.0

A smart auto-typing tool with human-like behavior, hotkeys, and multiple typing modes.

---

## 📥 Download & Run

**Requirements:**
- Python 3.8+
- Install dependencies:
```bash
pip install -r requirements.txt
```

**Run:**
```bash
python auto_typer.py
```

Or just double-click `run.bat`

---

## ⚡ Typing Modes

| Mode | Description |
|------|-------------|
| **Burst** | Ultra-fast typing with minimal delay. Best for forms and passwords. |
| **Human** | Natural typing with random variations. Recommended for websites and ChatGPT. |
| **Stealth** | Very slow with long pauses. Avoids bot detection. |
| **Line-by-Line** | Types one line at a time and presses Enter. Perfect for code and terminal. |

---

## ⚙️ Options

### ⏱️ Timing
| Option | Description |
|--------|-------------|
| **Base Delay** | Delay between each character (ms) |
| **Randomness** | Random variation added to delay for natural feel |
| **Punctuation Delay** | Extra pause after `.` `,` `!` `?` etc |
| **Between Words Delay** | Extra pause between words |
| **Thinking Chance** | Random chance to simulate a thinking pause |
| **Countdown** | Seconds to wait before typing starts |

### ⌨️ Hotkeys
| Hotkey | Default | Action |
|--------|---------|--------|
| Start | `Alt + S` | Start typing |
| Pause | `Alt + P` | Pause / Resume |
| Stop | `Alt + X` | Stop typing |
| Emergency | `ESC` | Force stop |

> You can change hotkeys from the **Keys** tab. Supported: `alt`, `ctrl`, `shift` + any letter/number or `f1`-`f12`

### 📂 Profiles
Save different texts as profiles and switch between them quickly from the dropdown.

### 💾 Auto-Save
Text is automatically saved every few seconds so you never lose your work. Interval is adjustable from the **More** tab.

---

## 📊 Stats
Track your total sessions, characters typed, and average per session from the **Stats** tab.

---

## 🌐 Social
- GitHub: [github.com/mrsoulcommunity](https://github.com/mrsoulcommunity)
- Telegram: [t.me/mrsoul_community](https://t.me/mrsoul_community)
