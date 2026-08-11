<div align="center">

# ⌨️ Auto Typer

### Advanced Edition · v4.0

**A human-like automated typing engine for Windows, with global hotkeys, tunable timing, reusable profiles, and a modern dark UI.**

[![Version](https://img.shields.io/badge/version-4.0-1f6feb?style=for-the-badge)](https://github.com/mrsoulcommunity/Auto-Typer/releases)
[![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#-requirements)
[![UI](https://img.shields.io/badge/UI-CustomTkinter-238636?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/license-MIT-f59e0b?style=for-the-badge)](LICENSE)

[Overview](#-overview) ·
[Features](#-features) ·
[Installation](#-installation) ·
[Usage](#-usage) ·
[Configuration](#-configuration) ·
[Building](#-building-a-standalone-executable) ·
[Troubleshooting](#-troubleshooting) ·
[Contributing](#-contributing)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Interface](#-interface)
- [Requirements](#-requirements)
- [Installation](#-installation)
  - [Option 1 — Prebuilt executable](#option-1--prebuilt-executable-fastest)
  - [Option 2 — From source](#option-2--from-source-recommended-for-development)
  - [Option 3 — One-click launcher](#option-3--one-click-launcher)
- [Usage](#-usage)
  - [Quick start](#quick-start)
  - [Typing modes](#typing-modes)
  - [Hotkeys](#hotkeys)
  - [Profiles](#profiles)
  - [Auto-save & recovery](#auto-save--recovery)
  - [Statistics](#statistics)
  - [Window size modes](#window-size-modes)
- [Configuration](#-configuration)
  - [Timing parameters](#timing-parameters)
  - [Configuration files](#configuration-files)
  - [Editing configuration by hand](#editing-configuration-by-hand)
- [Project structure](#-project-structure)
- [Architecture](#-architecture)
- [Building a standalone executable](#-building-a-standalone-executable)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Privacy & data handling](#-privacy--data-handling)
- [Responsible use](#-responsible-use)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Changelog](#-changelog)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Contact & community](#-contact--community)

---

## 🔎 Overview

**Auto Typer** takes any block of text and replays it into whatever window currently has keyboard focus — one keystroke at a time, at a pace you control.

Unlike a clipboard paste, the target application receives genuine, individually timed key events. And unlike a fixed-interval macro, Auto Typer varies its rhythm the way a person does: it hesitates after punctuation, breathes between words, and occasionally pauses as if thinking. The result is output that reads as typed rather than injected.

**Typical uses**

| Use case | Why Auto Typer helps |
|---|---|
| Filling forms and legacy apps | Fields that reject paste still accept real keystrokes |
| Live demos and screencasts | Reproduce the same flawless typing take, every time |
| Repetitive data entry | Store the text once as a profile, replay it with one hotkey |
| Testing input handling | Drive a UI at a precise, repeatable character rate |
| Code and log playback | Line-by-Line mode sends `Enter` after each line |

Everything runs locally. There is no account, no network service, and no telemetry.

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

#### 🎭 Four typing personalities
Burst, Human, Stealth, and Line-by-Line — each a curated preset of six timing parameters, applied in one click.

#### 🎚️ Fully tunable timing
Base delay, randomness, punctuation pauses, inter-word pauses, thinking probability, and start countdown — all exposed as live sliders.

#### ⌨️ Global hotkeys
Start, pause/resume, and stop from any application, without ever refocusing the Auto Typer window. Fully rebindable.

#### 🛑 Emergency stop
`ESC` halts typing instantly and unconditionally — hardcoded, always listening, and not overridable.

</td>
<td width="50%" valign="top">

#### 📂 Text profiles
Save any number of named snippets and switch between them from a dropdown. Stored as plain JSON.

#### 💾 Auto-save & crash recovery
The editor's contents are persisted on a configurable 2–30 s interval and restored automatically on next launch.

#### 📊 Usage statistics
Sessions run, total characters typed, per-session average, and last-run timestamp — persisted across restarts.

#### 🎨 Modern dark UI
A GitHub-inspired dark theme built on CustomTkinter, with Normal and Small window layouts and a live progress bar.

</td>
</tr>
</table>

**Also included:** live character / word / line counters · load text from `.txt` files · paste from clipboard · completion sound · daily rotating log files · single-file `.exe` build script · zero external services.

---

## 🖥️ Interface

The window is a three-region layout: a header, an editor column, and a settings column.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│  ⌨️  Auto Typer   v4.0 · Advanced Edition          [⚡ Human]  [ Normal ]     │
├───────────────────────────────────────────┬──────────────────────────────────┤
│  Text Editor  │ Profile ▾ │ New Clear     │  Modes │ Timing │ Keys │ Stats │…│
│               │           │ Save Delete   │ ─────────────────────────────────│
│               │           │ Load Paste    │  ○ Burst        Ultra-fast       │
│ ┌───────────────────────────────────────┐ │  ● Human        Natural variation│
│ │                                       │ │  ○ Stealth      Very slow        │
│ │  Your text goes here…                 │ │  ○ Line-by-Line Enter per line   │
│ │                                       │ │                                  │
│ │                                       │ │  ┌────────────────────────────┐  │
│ │                                       │ │  │       Apply Mode           │  │
│ └───────────────────────────────────────┘ │  └────────────────────────────┘  │
│  Chars: 0 │ Lines: 0 │ Words: 0   ● Saved │                                  │
├───────────────────────────────────────────┤                                  │
│      [  START  ]  [  PAUSE  ]  [  STOP  ] │                                  │
│  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔  │                                  │
│  ● READY                    Starting in 3 │                                  │
└───────────────────────────────────────────┴──────────────────────────────────┘
```

| Region | Contents |
|---|---|
| **Header** | Product title, active mode badge, Normal ⇄ Small window toggle |
| **Editor** | Profile selector, text toolbar, editable text area, live counters, save indicator |
| **Controls** | Start / Pause / Stop, progress bar, status line, pre-typing countdown |
| **Settings** | Five tabs — `Modes`, `Timing`, `Keys`, `Stats`, `More` |

---

## 📋 Requirements

| | Requirement | Notes |
|---|---|---|
| **OS** | Windows 10 / 11 | Windows-only: the completion sound uses the `winsound` standard-library module, which does not exist on macOS or Linux |
| **Python** | 3.8 or newer | Only needed when running from source. Verified against CPython 3.13 |
| **Display** | 1200 × 750 minimum | Normal mode opens at 1350 × 850; Small mode needs only 650 × 500 |
| **Privileges** | Standard user | Administrator is required only to type into elevated windows — see [Troubleshooting](#-troubleshooting) |

**Python dependencies** (pinned in [`requirements.txt`](requirements.txt)):

| Package | Version | Role |
|---|---|---|
| [`customtkinter`](https://github.com/TomSchimansky/CustomTkinter) | `5.2.2` | Modern themed widgets on top of Tkinter |
| [`pynput`](https://github.com/moses-palmer/pynput) | `1.7.6` | Synthesises keystrokes and listens for global hotkeys |
| [`pyperclip`](https://github.com/asweigart/pyperclip) | `1.8.2` | Pinned for clipboard support; the current build reads the clipboard through Tk |

> `tkinter` ships with the official python.org Windows installer. If you use a stripped-down or custom Python build, make sure the Tcl/Tk option was included.

---

## 📦 Installation

### Option 1 — Prebuilt executable (fastest)

No Python installation required.

```text
dist\AutoTyper.exe
```

Double-click it and you are running. Keep the `data\` folder alongside the executable so settings, profiles, and statistics persist between runs.

### Option 2 — From source (recommended for development)

```bash
# 1. Clone the repository
git clone https://github.com/mrsoulcommunity/Auto-Typer.git
cd Auto-Typer

# 2. Create an isolated environment (recommended)
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch
python auto_typer.py
```

### Option 3 — One-click launcher

[`run.bat`](run.bat) installs the dependencies and starts the app in a single step:

```bat
run.bat
```

Handy for a fresh machine; for day-to-day development prefer the virtual environment above, since `run.bat` installs into whichever Python is first on `PATH`.

---

## 🚀 Usage

### Quick start

1. **Enter your text.** Type it in the editor, click **Load** to import a `.txt` file, or click **Paste** to pull from the clipboard.
2. **Choose a mode.** Open the `Modes` tab, select one, and click **Apply Mode**.
3. **Focus the destination.** Click into the window you want the text typed into — a browser, an editor, a terminal, anything.
4. **Start.** Press `Alt` + `S` (or click **START** before switching windows).
5. **Wait out the countdown.** A 3-second countdown (configurable, 1–10 s) gives you time to place the cursor.
6. **Watch it type.** The progress bar tracks completion; `Alt` + `P` pauses and resumes, `Alt` + `X` stops, and `ESC` is the emergency brake.

> [!TIP]
> Start with the hotkey rather than the button. Clicking **START** leaves keyboard focus on Auto Typer, so you must still switch windows during the countdown. The hotkey works from inside the destination window, where the cursor is already where you want it.

> [!IMPORTANT]
> Keystrokes always go to whatever window has focus **at that moment** — Auto Typer does not target a specific application. If you click elsewhere mid-run, the rest of the text follows your click. Press `ESC` if that happens.

### Typing modes

Selecting a mode in the `Modes` tab and clicking **Apply Mode** overwrites the five core timing values with that mode's preset:

| Mode | Base delay | Randomness | Punctuation | Between words | Thinking | Approx. speed |
|---|---:|---:|---:|---:|---:|---|
| ⚡ **Burst** | 20 ms | ± 5 ms | 0 ms | 0 ms | 0 % | ≈ 50 chars/s (~600 WPM) |
| 🧑 **Human** | 85 ms | ± 25 ms | 150 ms | 80 ms | 2 % | ≈ 9 chars/s (~95 WPM) |
| 🥷 **Stealth** | 180 ms | ± 50 ms | 250 ms | 150 ms | 5 % | ≈ 4 chars/s (~45 WPM) |
| 📃 **Line-by-Line** | 60 ms | ± 15 ms | 100 ms | 50 ms | 1 % | ≈ 13 chars/s (~140 WPM) |

*Speeds are estimates for ordinary English prose; actual throughput depends on punctuation density and how fast the receiving application accepts input.*

**When to use which**

- **Burst** — trusted local fields, short strings, and anything where speed beats realism. Fast enough that some applications drop characters; if that happens, step up to Line-by-Line or raise the base delay.
- **Human** — the default, and the right answer most of the time. Word and punctuation pauses plus a 2 % chance of a 400 ms "thinking" pause produce a convincingly irregular cadence.
- **Stealth** — deliberately unhurried, for rate-limited inputs or any target that reacts badly to machine-speed entry.
- **Line-by-Line** — types each line, then sends a real `Enter` key and waits `line_break_delay_ms` (200 ms by default) before the next one. The mode to use for code, command sequences, and structured multi-line content.

> [!NOTE]
> Line-by-Line ignores punctuation, inter-word, and thinking delays while typing a line — only base delay and randomness apply within the line, plus the line-break pause between lines. Its progress bar advances per line rather than per character.

### Hotkeys

| Action | Default | Rebindable | Behaviour |
|---|---|:---:|---|
| Start typing | `Alt` + `S` | ✅ | Ignored while a session is already running |
| Pause / Resume | `Alt` + `P` | ✅ | Toggles; only active during a session |
| Stop | `Alt` + `X` | ✅ | Ends the session and resets the progress bar |
| **Emergency stop** | `ESC` | ❌ | Always active, fires on key-down, cannot be reassigned |

Hotkeys are global — they fire regardless of which application has focus.

**Rebinding.** Open the `Keys` tab, type a new combination into the relevant field, and click **Save Hotkeys**. The listener restarts immediately; no application restart is needed.

**Combination syntax**

```text
<modifier>+<key>                  alt+s        ctrl+q        shift+f9
<modifier>+<modifier>+<key>       alt+ctrl+t   ctrl+shift+f5
<key>                             f8           f12
```

Rules worth knowing:

- Supported modifiers: `alt`, `ctrl`, `shift`. Function keys `f1`–`f12` are supported as the final key.
- **Modifiers must be written in alphabetical order** — `alt`, then `ctrl`, then `shift`. `ctrl+alt+t` will never match; write `alt+ctrl+t`.
- Everything is lower-cased and trimmed on save, so `Alt + S` and `alt+s` are equivalent.
- Bindings fire on key **release** (except `ESC`, which fires on press).
- Avoid combinations the destination application already uses — Auto Typer does not swallow the keypress, so both actions will trigger.

**Reset to Default** restores `alt+s` / `alt+p` / `alt+x` in one click.

### Profiles

A profile is a named block of text — a signature, a form response, a snippet of boilerplate, a command sequence.

| Button | Action |
|---|---|
| **New** | Prompts for a name and creates an empty profile (offers to load it if the name already exists) |
| **Save** | Stores the editor's current contents under the selected profile name |
| **Delete** | Removes the selected profile; `Default` is protected |
| **Clear** | Empties the editor after confirmation, leaving saved profiles untouched |
| **Load** | Imports a `.txt` file (UTF-8) into the editor |
| **Paste** | Inserts the clipboard contents at the cursor |

Selecting a profile from the dropdown loads it into the editor immediately. Saving while `Default` is selected auto-names the profile `Profile_1`, `Profile_2`, and so on. All profiles live in `data/profiles_v4.json` — a plain JSON object of `{"name": "text"}` that you can edit, diff, or back up like any other file.

### Auto-save & recovery

The editor's contents are written to `data/last_text_v4.txt` on a repeating timer, and reloaded automatically the next time the app starts — so an unexpected shutdown costs you at most one interval.

Configure it in the `More` tab: **Enable Auto-Save** toggles the timer, and the interval slider covers 2–30 seconds (default 5). Click **Save Settings** to persist the interval.

The indicator in the editor toolbar reports the current state:

| Indicator | Meaning |
|---|---|
| 🔴 `● Unsaved` | The text changed since the last write |
| 🟠 `● Auto-saved` | A write just completed (shown briefly) |
| 🟢 `● Saved` | Everything on disk is current |

Auto-save only writes when the text has actually changed, and the editor is saved once more on exit regardless of the timer.

### Statistics

The `Stats` tab tracks cumulative usage across all runs, persisted in `data/stats_v4.json`:

- 📊 **Total sessions** — completed runs (a stopped run is not counted)
- 📝 **Total characters** — sum of every character typed
- 📈 **Average per session** — total characters ÷ sessions
- 🕒 **Last session** — UTC timestamp and character count of the most recent run

**Refresh** re-reads the values; **Reset Statistics** zeroes them after confirmation.

### Window size modes

The header button toggles between two layouts, and your choice persists across restarts:

| Mode | Geometry | Minimum | Best for |
|---|---|---|---|
| **Normal** | 1350 × 850 | 1200 × 750 | Full workspace — editor and all settings side by side |
| **Small** | 700 × 550 | 650 × 500 | A compact panel that stays out of the way while you work |

---

## ⚙️ Configuration

### Timing parameters

Every value below lives in `data/config_v4.json`. Those marked **UI** are adjustable from the `Timing` tab; the rest are file-only.

| Parameter | Default | Range | UI | Effect |
|---|---:|---|:---:|---|
| `base_delay_ms` | `85` | 20 – 500 | ✅ | Baseline pause after each character. The primary speed control |
| `randomness_ms` | `20` | 0 – 150 | ✅ | Random jitter of ± this many ms per character (clamped so the delay never drops below 1 ms) |
| `typing_mode` | `"Human"` | `Burst` · `Human` · `Stealth` · `LineByLine` | ✅ | Active mode. Note the value is `LineByLine`, without hyphens |
| `punctuation_delay_ms` | `150` | 0 – 300 | ✅ | Extra pause after `. , ! ? ; :` |
| `word_delay_ms` | `80` | 0 – 200 | ✅ | Extra pause on a space that ends a word |
| `thinking_chance` | `0.02` | 0.00 – 0.10 | ✅ | Probability, per character, of an extra hesitation |
| `thinking_duration_ms` | `400` | any | ❌ | Length of that hesitation |
| `countdown_sec` | `3` | 1 – 10 | ✅ | Grace period between pressing start and the first keystroke |
| `line_break_delay_ms` | `200` | any | ❌ | Pause after each `Enter` in Line-by-Line mode |
| `sound_enabled` | `true` | `true` / `false` | ✅ | Two-tone beep on successful completion |
| `auto_save_interval_sec` | `5` | 2 – 30 | ✅ | Auto-save period (in the `More` tab) |
| `size_mode` | `0` | `0` = Normal, `1` = Small | ✅ | Window layout, restored at startup |

> [!NOTE]
> Slider changes are previewed live but only written to disk when you click **Save Settings** in that tab. Applying a mode saves immediately and overwrites the five core timing values.

### Configuration files

All state lives in `data/`, next to the script or the executable:

| File | Contents |
|---|---|
| `config_v4.json` | Timing parameters, sound, auto-save interval, window size mode |
| `hotkeys_v4.json` | Start / pause / stop bindings (created on first save) |
| `profiles_v4.json` | Saved text profiles, as `{"name": "text"}` |
| `stats_v4.json` | Session count, total characters, last-session metadata |
| `last_text_v4.txt` | Auto-saved editor contents, restored at startup |

Logs are written to `logs/app_YYYYMMDD.log`, one file per UTC day, at `INFO` level and mirrored to stdout when run from a console.

### Editing configuration by hand

The JSON files are safe to edit while the app is closed:

```jsonc
{
  "base_delay_ms": 120,          // slower, steadier baseline
  "randomness_ms": 45,           // wider natural variation
  "typing_mode": "Human",
  "line_break_delay_ms": 350,    // longer pause between lines
  "punctuation_delay_ms": 200,
  "word_delay_ms": 90,
  "thinking_chance": 0.03,
  "thinking_duration_ms": 650,   // longer hesitations, file-only
  "countdown_sec": 5,
  "sound_enabled": false,
  "auto_save_interval_sec": 10,
  "size_mode": 0
}
```

Loading is defensive: unknown keys are discarded, and a malformed or unreadable file is logged and replaced with built-in defaults rather than crashing the app. Delete any file in `data/` to reset that piece of state to factory settings.

---

## 📁 Project structure

```text
Auto-Typer/
├── auto_typer.py          # Application — UI, typing engine, hotkeys, persistence
├── requirements.txt       # Pinned Python dependencies
├── run.bat                # Install dependencies and launch
├── build_exe.bat          # One-file PyInstaller build
├── AutoTyper.spec         # PyInstaller build specification
├── LICENSE                # MIT
├── README.md              # This document
├── data/                  # Runtime state (config, hotkeys, profiles, stats, last text)
├── logs/                  # Daily application logs
└── dist/                  # Build output, including AutoTyper.exe
```

`auto_typer.py` is a single ~1,150-line module organised in clear bands:

| Lines | Responsibility |
|---|---|
| `1 – 38` | Imports and the `TypingConfig` / `HotkeyConfig` dataclasses |
| `40 – 189` | Initialisation, logging setup, and all load/save persistence helpers |
| `191 – 602` | UI construction — header, editor, controls, and the five settings tabs |
| `604 – 926` | Event handlers — sliders, modes, profiles, hotkey registration, statistics |
| `928 – 1095` | The typing engine — session lifecycle, character and line-based workers |
| `1097 – 1155` | Size modes, social links, shutdown, and the entry point |

---

## 🏗️ Architecture

### Threading model

The application runs four kinds of thread, all coordinated through Tk's event loop:

```text
┌─────────────────────────────────────────────────────────────────┐
│  Main thread — Tk event loop                                    │
│  Owns every widget. All UI mutations happen here.               │
└───────┬─────────────────────┬────────────────────┬──────────────┘
        │                     │                    │
        │ spawns              │ spawns             │ re-arms
        ▼                     ▼                    ▼
┌───────────────┐   ┌──────────────────┐   ┌──────────────────────┐
│ Typing worker │   │ pynput Listener  │   │ Auto-save timer      │
│ (daemon)      │   │ (daemon)         │   │ (threading.Timer)    │
│               │   │                  │   │                      │
│ Countdown →   │   │ Tracks modifiers │   │ Writes editor text   │
│ per-char or   │   │ Matches combos   │   │ if it changed, then  │
│ per-line loop │   │ Emergency ESC    │   │ schedules the next   │
└───────┬───────┘   └────────┬─────────┘   └──────────┬───────────┘
        │                    │                        │
        └────────────────────┴────────────────────────┘
                   root.after(0, …) — every UI update
                   is marshalled back to the main thread
```

**Key design points**

- **Single UI owner.** Worker threads never touch widgets directly; every update is queued onto the main thread with `root.after(0, …)`, which is the only thread-safe way into Tk.
- **Cooperative cancellation.** Stopping sets a `threading.Event` that the typing loop checks before each character (and inside the pause loop), so a session ends in milliseconds without killing a thread mid-keystroke.
- **Pause without spinning.** A paused worker polls its flag every 100 ms — responsive to the eye, negligible on the CPU.
- **Daemon threads throughout.** Nothing can keep the process alive after the window closes.
- **Guaranteed cleanup.** The typing worker's `finally` block always restores the button states, even if the run ends in an exception.
- **Graceful shutdown.** Closing the window stops any active session, flushes the editor text and config to disk, cancels the auto-save timer, and shuts down the hotkey listener before destroying the root.

### Typing pipeline

For each character, the delay is composed from the configured parts:

```text
delay = base_delay_ms
      + random(-randomness_ms, +randomness_ms)     # clamped to ≥ 1 ms
      + punctuation_delay_ms   if char in . , ! ? ; :
      + word_delay_ms          if char is a word-ending space
      + thinking_duration_ms   with probability thinking_chance
```

Characters are sent through `pynput`'s `Controller.type()`. A character the OS refuses to synthesise is logged as a warning and skipped, so one problem glyph never aborts a run.

---

## 🛠️ Building a standalone executable

### With the helper script

```bat
build_exe.bat
```

It installs dependencies and runs PyInstaller, producing `dist\AutoTyper.exe`.

### Manually

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name AutoTyper auto_typer.py
```

### From the spec file

[`AutoTyper.spec`](AutoTyper.spec) captures the same configuration for reproducible builds:

```bash
pyinstaller AutoTyper.spec
```

| Setting | Value | Rationale |
|---|---|---|
| `--onefile` | enabled | Single self-contained `.exe`, nothing to unpack |
| `--noconsole` | enabled | No console window behind the GUI |
| `upx=True` | enabled | Compresses the binary if UPX is on `PATH` |
| `name` | `AutoTyper` | Output filename |

**Notes**

- Build on the oldest Windows version you intend to support — PyInstaller binaries are not backward compatible across major Windows releases.
- One-file builds unpack to a temporary directory on launch, so the first start is a second or two slower than a one-folder build.
- Ship the `data/` folder next to the executable, or the app will create a fresh one with default settings on first run.
- Fresh PyInstaller executables are unsigned and are sometimes flagged heuristically by antivirus software. Code-sign the binary for distribution.

---

## 🔧 Troubleshooting

<details>
<summary><b>Nothing gets typed into the target application</b></summary>

<br>

Most often a privilege mismatch. Windows blocks a normal-privilege process from sending input to an elevated one.

1. If the destination runs as administrator (Task Manager, some installers, certain IDEs), run Auto Typer as administrator too — right-click → **Run as administrator**.
2. Confirm the destination window actually had focus when the countdown ended.
3. Confirm the destination accepts a text cursor — click into the field first.
4. Some games and anti-cheat-protected applications block synthetic input by design. This is intentional on their side and cannot be worked around.

</details>

<details>
<summary><b>Hotkeys do nothing</b></summary>

<br>

1. **Check the modifier order** — modifiers must be alphabetical (`alt`, `ctrl`, `shift`). `ctrl+alt+t` never matches; write `alt+ctrl+t`.
2. **Check for conflicts** — another application may already own the combination. Try an unused function key such as `f8`.
3. **Elevation again** — a normal-privilege listener does not receive keys typed into an elevated window. Run Auto Typer as administrator.
4. Bindings fire on key *release*; hold the modifier until you have released the main key.
5. Still stuck? Click **Reset to Default** in the `Keys` tab, then restart the app.

</details>

<details>
<summary><b>Characters arrive out of order, doubled, or missing</b></summary>

<br>

The destination cannot keep up with the input rate. Web applications with heavy JavaScript input handlers are the usual culprits.

- Raise `base_delay_ms` — try 100–150 ms.
- Switch from Burst to Human or Stealth.
- For multi-line content, use Line-by-Line so the target gets a natural break between lines.

</details>

<details>
<summary><b>Special characters, accents, or emoji do not appear</b></summary>

<br>

Synthetic keystrokes are subject to the active keyboard layout, and `pynput` cannot express every glyph on every layout. Failures are logged to `logs/app_YYYYMMDD.log` and skipped rather than aborting the run.

- Switch to a layout that contains the characters you need.
- Prefer plain ASCII where the destination allows it.
- For a one-off block of exotic text, the clipboard is more reliable than synthetic typing.

</details>

<details>
<summary><b>ImportError: No module named 'winsound'</b></summary>

<br>

You are not on Windows. `winsound` is a Windows-only standard-library module, and Auto Typer v4.0 targets Windows exclusively. Cross-platform support is on the [roadmap](#-roadmap).

</details>

<details>
<summary><b>ModuleNotFoundError for customtkinter or pynput</b></summary>

<br>

Dependencies were installed into a different interpreter than the one running the app — common when several Pythons share a machine.

```bash
python -m pip install -r requirements.txt
python auto_typer.py
```

Using the same `python` for both commands guarantees they match. A virtual environment removes the ambiguity entirely.

</details>

<details>
<summary><b>Settings or profiles are not remembered</b></summary>

<br>

- The `data/` folder must sit next to `auto_typer.py` (or `AutoTyper.exe`) and be writable. `Program Files` is not writable by a normal user — move the app elsewhere.
- Slider changes require **Save Settings** in that tab; only mode changes save automatically.
- Check `logs/app_YYYYMMDD.log` for a write error.

</details>

<details>
<summary><b>Antivirus flags AutoTyper.exe</b></summary>

<br>

A false positive with two compounding causes: unsigned PyInstaller one-file binaries are a common heuristic trigger, and any program that synthesises keystrokes resembles a keylogger to a scanner. Auto Typer records nothing and sends nothing.

Build from source yourself if you would rather not trust a prebuilt binary, and code-sign the executable if you plan to distribute it.

</details>

---

## ❓ FAQ

<details>
<summary><b>Does Auto Typer record what I type?</b></summary>

<br>

No. The global listener only compares keypresses against your configured hotkey combinations and the emergency `ESC`; nothing about your keystrokes is stored or transmitted. The only text written to disk is what *you* put in the editor, saved locally to `data/`.

</details>

<details>
<summary><b>Can I type into a game?</b></summary>

<br>

Sometimes. Games rendering through DirectInput or protected by anti-cheat commonly reject synthetic input by design. Attempting to defeat those protections is out of scope for this project — see [Responsible use](#-responsible-use).

</details>

<details>
<summary><b>How do I type the same text into many fields?</b></summary>

<br>

Save it as a profile, then in each field press your start hotkey and wait out the countdown. Auto Typer types into whatever holds focus, so you never have to return to its window.

</details>

<details>
<summary><b>Is there a maximum text length?</b></summary>

<br>

No hard limit, but keep it sensible. At Human speed, 10,000 characters take roughly 18 minutes. The progress bar and character counter give you the estimate before you start.

</details>

<details>
<summary><b>Can I run it on macOS or Linux?</b></summary>

<br>

Not as of v4.0. `customtkinter` and `pynput` are both cross-platform, so the main blockers are the `winsound` completion beep and Windows-specific behaviour around global hotkeys. See the [roadmap](#-roadmap).

</details>

<details>
<summary><b>Why does typing continue after I click another window?</b></summary>

<br>

By design — that is what makes it possible to start typing from inside the destination application. Keystrokes always follow focus. Press `ESC` to stop instantly.

</details>

<details>
<summary><b>What is the difference between Stop and Pause?</b></summary>

<br>

**Pause** (`Alt`+`P`) suspends the session and keeps its position, so resuming continues from the exact character where it stopped. **Stop** (`Alt`+`X`) ends the session, resets the progress bar, and is not counted in your statistics. `ESC` behaves like Stop but fires immediately on key-down.

</details>

---

## 🔐 Privacy & data handling

Auto Typer is fully offline by design.

| | |
|---|---|
| **Network access** | None. The only outbound action is opening a browser when you click the GitHub or Telegram button |
| **Telemetry** | None. No analytics, no crash reporting, no update checks |
| **Accounts** | None. Nothing to register or sign in to |
| **Stored data** | Your editor text, profiles, settings, and usage counters — all under `data/`, as plain files you own |
| **Logs** | Operational events only, in `logs/`. Editor content is never logged; a single character can appear in a warning if the OS refuses to type it |
| **Uninstall** | Delete the folder. Nothing is written to the registry, `AppData`, or anywhere else |

---

## ⚖️ Responsible use

Auto Typer is a productivity and accessibility tool. Use it on systems you own or are authorised to use, and in ways that respect the terms of the services you interact with.

**Please do not** use it to circumvent anti-cheat or anti-automation protections, to gain an unfair advantage in games, exams, or competitions, to violate a service's terms of use, to impersonate human activity where a human is required, or to generate spam or abusive automated content.

The authors and contributors provide this software as-is and accept no responsibility for how it is used. See the [LICENSE](LICENSE) for the full disclaimer.

---

## 🗺️ Roadmap

Ideas under consideration for future releases. Nothing here is committed — [feedback](https://github.com/mrsoulcommunity/Auto-Typer/issues) shapes the order.

- [ ] **Cross-platform support** — abstract the completion sound and hotkey layer for macOS and Linux
- [ ] **Interactive hotkey capture** — press a combination instead of typing its name, removing the modifier-ordering pitfall
- [ ] **Per-profile settings** — bind a timing configuration to each saved profile
- [ ] **Typo simulation** — optional realistic mistakes with backspace corrections
- [ ] **Scheduled and repeated runs** — start at a given time, or loop a fixed number of times
- [ ] **CLI mode** — headless operation for scripting
- [ ] **Rich text and macros** — placeholders such as `{date}`, `{clipboard}`, `{tab}`
- [ ] **Light theme** and configurable accent colours
- [ ] **Automated tests** for the delay-composition and hotkey-parsing logic
- [ ] **Localised UI**

---

## 🤝 Contributing

Contributions are welcome — bug reports, features, documentation, and testing on unusual configurations all help.

### Reporting a bug

Open an [issue](https://github.com/mrsoulcommunity/Auto-Typer/issues) with your Windows and Python versions, whether you ran the source or the `.exe`, the steps to reproduce, what you expected versus what happened, and the relevant lines from `logs/app_YYYYMMDD.log`.

### Suggesting a feature

Open an issue describing the problem you are trying to solve — not only the solution you have in mind. The underlying need often has a better answer than the first idea.

### Submitting code

```bash
# 1. Fork, then clone your fork
git clone https://github.com/<your-username>/Auto-Typer.git
cd Auto-Typer

# 2. Branch
git checkout -b feature/short-description

# 3. Set up
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 4. Make your changes, then verify by hand
python auto_typer.py

# 5. Commit and push
git commit -m "feat: add interactive hotkey capture"
git push -u origin feature/short-description
```

Then open a pull request describing what changed and why, with before/after screenshots for any UI work.

### Style guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/); keep the existing four-space indentation and naming conventions.
- Use type hints on new functions, matching the existing code.
- Never touch widgets from a worker thread — marshal every UI update through `root.after(0, …)`.
- Wrap file I/O in `try` / `except` and log failures instead of crashing.
- Keep the colour palette consistent with the constants defined in `__init__`.
- Do not commit build artefacts (`build/`, `dist/`, `__pycache__/`) or personal files from `data/` and `logs/`.
- [Conventional Commits](https://www.conventionalcommits.org/) are preferred: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.

### Testing checklist

Before opening a pull request, confirm that all four typing modes work, hotkeys still bind and fire, profiles save/load/delete correctly, auto-save and recovery survive a restart, both window size modes render, and settings persist across a full close and reopen.

---

## 📝 Changelog

### v4.0 — Advanced Edition

- Rebuilt UI on CustomTkinter with a GitHub-inspired dark theme
- Four typing modes with one-click presets
- Global, rebindable hotkeys plus a hardcoded `ESC` emergency stop
- Named text profiles with JSON persistence
- Configurable auto-save with crash recovery
- Persistent usage statistics
- Normal and Small window layouts, remembered across restarts
- Daily rotating log files
- Standalone one-file Windows executable

---

## 📄 License

Released under the **MIT License** — see [LICENSE](LICENSE) for the full text.

```text
Copyright (c) 2026 MrSoul
```

You are free to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the software, provided the copyright notice and permission notice are included. The software is provided "as is", without warranty of any kind.

---

## 🙏 Acknowledgments

- [**CustomTkinter**](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky — the modern widget toolkit behind the interface
- [**pynput**](https://github.com/moses-palmer/pynput) by Moses Palmér — keyboard control and global hotkey listening
- [**PyInstaller**](https://pyinstaller.org/) — standalone executable packaging
- [**Shields.io**](https://shields.io/) — the badges in this document
- Everyone who has reported an issue, suggested a feature, or tested a build

---

## 📬 Contact & community

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-mrsoulcommunity-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mrsoulcommunity)
[![Telegram](https://img.shields.io/badge/Telegram-mrsoul__community-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/mrsoul_community)

**Found a bug?** [Open an issue](https://github.com/mrsoulcommunity/Auto-Typer/issues) ·
**Have an idea?** [Request a feature](https://github.com/mrsoulcommunity/Auto-Typer/issues/new) ·
**Latest build?** [Releases](https://github.com/mrsoulcommunity/Auto-Typer/releases)

<br>

If Auto Typer saves you time, consider leaving a ⭐ — it genuinely helps.

<br>

**Made with ⌨️ by [MrSoul](https://github.com/mrsoulcommunity)**

<sub><a href="#-auto-typer">Back to top ↑</a></sub>

</div>
