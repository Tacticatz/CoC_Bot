# Windows 11 Setup Guide for CoC Bot

## Quick Start (Recommended)

### Method 1: Automated Setup Wizard

1. Download the repository
   ```bash
   git clone https://github.com/Tacticatz/CoC_Bot.git
   cd CoC_Bot
   ```

2. Run the setup wizard
   - Double-click `setup_windows.bat`
   - Or from command prompt:
   ```batch
   setup_windows.bat
   ```

3. Follow the interactive setup
   - The wizard will automatically:
     - Check Python version (3.11+ required)
     - Install Android Debug Bridge (ADB)
     - Install Python dependencies
     - Create configuration file
     - Test your setup

4. Start the bot
   - Double-click `start_bot.bat`
   - Or manually: `.venv\Scripts\python src\main.py`

---

## System Requirements

### Minimum
- Windows 10/11 (64-bit)
- Python 3.11+
- 8 GB RAM
- BlueStacks 5+
- 3 GB free disk space

### Recommended
- Windows 11 (22H2+)
- Python 3.12+
- 16 GB RAM
- BlueStacks 5.12+
- SSD (faster OCR)

---

## Prerequisites

### 1. Python 3.11+

Download:
- https://www.python.org/downloads/

Installation steps:
1. Download Windows installer
2. Run installer
3. IMPORTANT: Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Restart your computer

Verify:
```batch
python --version
```

### 2. BlueStacks

Download:
- https://www.bluestacks.com/

Setup:
1. Install BlueStacks
2. Launch BlueStacks
3. Settings > Advanced > Enable "Android Debug Bridge"
4. Install Clash of Clans from Google Play
5. Configure:
   - Device profile: Samsung Galaxy S22 Ultra
   - Resolution: 1920x1080
   - Frame rate: 60 fps
   - Default troop size

### 3. Android Debug Bridge (ADB)

Option A: Automatic (Recommended)
- Setup wizard installs ADB automatically

Option B: Manual
1. Download platform-tools: https://developer.android.com/tools/releases/platform-tools
2. Extract to `C:\Users\YourUsername\AppData\Local\adb\platform-tools`
3. Add to PATH:
   - Settings > System > About > Advanced system settings
   - Environment Variables > New
   - Variable name: `ADB_PATH`
   - Variable value: `C:\Users\YourUsername\AppData\Local\adb\platform-tools`

Verify:
```batch
adb --version
adb connect 127.0.0.1:5555
adb devices
```

---

## Setup Wizard Modes

### Mode 1: Automatic (Web GUI) - RECOMMENDED

```batch
setup_windows.bat
REM Select option 1
```

Features:
- Beautiful web interface
- Step-by-step guidance
- One-click installation
- System checks & tests
- Configuration wizard
- Progress tracking

### Mode 2: Manual (Command Line)

```batch
python windows_setup_wizard.py
REM Select option 2
```

For advanced users who want more control over each step.

### Mode 3: Quick Setup

```batch
python windows_setup_wizard.py
REM Select option 3
```

Fast setup skipping optional features (Telegram, Groq).

---

## Configuration

### Basic Configuration

After setup, edit `src/configs.py`:

```python
# Instance Setup
INSTANCE_IDS = ["main"]  # BlueStacks instance name
ADB_ADDRESSES = ["127.0.0.1:5555"]  # BlueStacks ADB port

# Optional Features
WEB_APP_URL = ""  # Leave empty for local only
TELEGRAM_BOT_TOKEN = ""  # Get from @BotFather
GROQ_API_KEY = ""  # From console.groq.com
```

### Advanced Configuration

See `src/configs.template.py` for all available options:
- Upgrade priorities
- Attack settings
- Resource collection
- Hero upgrades
- Lab upgrades

---

## Running the Bot

### Option 1: Simple Launcher (Recommended)

```batch
start_bot.bat
```

### Option 2: Command Line

```batch
.venv\Scripts\activate
python src\main.py
```

### Option 3: GUI (Desktop App)

```batch
python src\gui.py
```

### Option 4: Web Dashboard

```batch
python app\app.py
REM Access at http://localhost:1234
```

---

## Multiple Accounts

### Setup Multiple BlueStacks Instances

1. Create new instance in BlueStacks:
   - Multi-Instance Manager > "+ New Instance"
   - Name: `account2`
   - Settings: Same as main (1920x1080, 60fps)
   - Install CoC

2. Update configs.py:

```python
INSTANCE_IDS = ["main", "account2"]
ADB_ADDRESSES = ["127.0.0.1:5555", "127.0.0.1:5557"]
DEFAULT_INSTANCE_ID = INSTANCE_IDS[0]
```

3. Run multiple bots:

```batch
python src\main.py --id main
python src\main.py --id account2
```

---

## Troubleshooting

### Python Issues

Python not found
- Install Python 3.11+: https://www.python.org/downloads/
- Make sure "Add Python to PATH" is checked
- Restart computer after installation
- Run `python --version` to verify

Module not found (after setup)
- Activate virtual environment: `.venv\Scripts\activate`
- Reinstall: `pip install -r src\requirements.txt`

### ADB Issues

ADB not found
- Run setup wizard: `setup_windows.bat`
- Or manually add to PATH (see Prerequisites section)

Cannot connect to ADB
- Check BlueStacks is running
- Settings > Advanced > Android Debug Bridge = ON
- Test: `adb connect 127.0.0.1:5555`
- Check firewall isn't blocking port 5555

### BlueStacks Issues

BlueStacks not found
- Install from https://www.bluestacks.com/
- Or set `BLUESTACKS_BIN_PATH` in configs.py

Touch events not working
- Check frame rate is 60 fps (not lower)
- Resolution should be 1920x1080
- Try: Settings > Game Settings > Reset to default

Screen resolution wrong
- Settings > Display > Resolution = 1920x1080
- Frame rate = 60
- Restart BlueStacks

### CoC App Issues

CoC app won't launch
- Force stop: `adb shell am force-stop com.supercell.clashofclans`
- Clear cache: `adb shell pm clear com.supercell.clashofclans`
- Reinstall CoC from Google Play

Auto-update failing
- Disable auto-update in Google Play
- Or set `AUTO_START_BLUESTACKS = False` in configs.py

For more troubleshooting, see TROUBLESHOOTING.md

---

## Performance Tips

### For Faster OCR

1. Use Groq (Cloud OCR):
   - Sign up: https://console.groq.com
   - Get free API key
   - Add to configs.py: `GROQ_API_KEY = "your_key"`

2. Use GPU for local OCR:
   - Install GPU support: `pip install torch torchvision torchaudio`
   - easyocr will automatically use GPU

### For Smoother Gameplay

1. Allocate more RAM to BlueStacks:
   - Settings > Engine > RAM = 6-8 GB
   - CPU cores = 4-8

2. Disable unnecessary BlueStacks features:
   - Ecosystem > Disable unused apps
   - Settings > Gaming > Enable "Performance Mode"

### For Reliable Attacks

1. Reduce CHECK_INTERVAL in configs.py:
   - Default: 5 minutes
   - For faster farming: 2-3 minutes
   - But uses more CPU

2. Enable local cache:
   - Bot automatically caches UI elements
   - First run is slower, subsequent runs faster

---

## Windows 11 Specific Features

### Developer Mode (Optional)

Enable for better debugging:
1. Settings > Privacy & Security > Developer settings
2. Toggle "Developer Mode" ON
3. Allows more detailed error logs

### Power Settings

Bot automatically manages:
- Screen doesn't sleep during farming
- PC doesn't hibernate
- Settings restored after bot stops

If issues, manually set:
```batch
powercfg /change monitor-timeout-ac 0
powercfg /change disk-timeout-ac 0
```

Restore:
```batch
powercfg /change monitor-timeout-ac 10
powercfg /change disk-timeout-ac 20
```

---

## Getting Help

- Issues: https://github.com/Tacticatz/CoC_Bot/issues
- Q&A: https://github.com/Tacticatz/CoC_Bot/discussions
- Ideas: https://github.com/Tacticatz/CoC_Bot/discussions/categories/ideas

---

## Advanced: Manual Installation

If setup wizard doesn't work:

```batch
REM 1. Create virtual environment
python -m venv .venv

REM 2. Activate it
.venv\Scripts\activate

REM 3. Install dependencies
pip install --upgrade pip
pip install -r src\requirements.txt
pip install -r app\requirements.txt

REM 4. Copy config template
copy src\configs.template.py src\configs.py

REM 5. Edit configs.py with your settings
REM (Use Notepad or your editor)

REM 6. Test connection
adb devices

REM 7. Run bot
python src\main.py
```
