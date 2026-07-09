# Windows 11 Troubleshooting Guide

## Common Issues & Solutions

### Setup Wizard Problems

#### Python not found
```
ERROR: Python not found!
Please install Python 3.11+
```

Solution:
1. Download Python 3.11+: https://www.python.org/downloads/
2. Important: Check "Add Python to PATH" during installation
3. Restart your computer
4. Verify: `python --version`

#### Flask not found / Module not found
```
ModuleNotFoundError: No module named 'flask'
```

Solution:
```batch
.venv\Scripts\activate
pip install flask flask-cors
```

#### Setup wizard crashes

Solution:
```batch
REM Run in manual mode
python windows_setup_wizard.py
REM Select option 2 (Manual)
```

---

### ADB Connection Issues

#### ADB not found
```
ERROR: ADB (Android Debug Bridge) not found
```

Solutions:

Option A: Auto-install (Recommended)
```batch
setup_windows.bat
REM Choose option 1 (Automatic)
REM Select "Install" for Android Debug Bridge
```

Option B: Manual install
```batch
REM Download platform-tools from:
REM https://developer.android.com/tools/releases/platform-tools

REM Extract to:
REM C:\Users\YourUsername\AppData\Local\adb\platform-tools

REM Add to PATH:
REM Settings > System > About > Advanced system settings
REM Environment Variables > New
REM Variable name: ADB_PATH
REM Variable value: C:\Users\YourUsername\AppData\Local\adb\platform-tools

REM Verify:
adb --version
```

#### Cannot connect to ADB / No devices found
```
adb devices
REM (No devices shown)
```

Solutions:
1. Check BlueStacks is running:
   - Launch BlueStacks
   - Wait for full startup (2-3 minutes)

2. Enable Android Debug Bridge in BlueStacks:
   - BlueStacks Menu > Settings > Advanced
   - Toggle "Android Debug Bridge" ON
   - Restart BlueStacks

3. Manual connection:
   ```batch
   adb connect 127.0.0.1:5555
   adb devices
   ```

4. Check firewall:
   - Windows Defender Firewall > Allow app through firewall
   - Find "adb.exe" and enable it
   - Restart command prompt

5. Reset ADB:
   ```batch
   adb kill-server
   adb start-server
   adb connect 127.0.0.1:5555
   ```

---

### BlueStacks Issues

#### BlueStacks not found
```
ERROR: BlueStacks not found in default locations
```

Solution:
1. Install BlueStacks: https://www.bluestacks.com/
2. Or set path in `src/configs.py`:
   ```python
   BLUESTACKS_BIN_PATH = "C:\\path\\to\\HD-Player.exe"
   ```

#### Cannot launch BlueStacks / HD-Player.exe not found

Solutions:
1. Check installation:
   ```batch
   dir "C:\Program Files\BlueStacks_nxt\HD-Player.exe"
   ```

2. Try alternate paths:
   - `C:\Program Files\BlueStacks_nxt\HD-Player.exe`
   - `C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe`
   - `D:\Program Files\BlueStacks_nxt\HD-Player.exe` (if installed on D:)

3. Set manually in configs.py:
   ```python
   BLUESTACKS_BIN_PATH = r"C:\Your\Actual\Path\HD-Player.exe"
   ```

4. Reinstall BlueStacks:
   - Uninstall completely
   - Delete `C:\ProgramData\BlueStacks_nxt`
   - Reinstall from https://www.bluestacks.com/

#### Touch events not working / Bot can't click

Solutions:
1. Check BlueStacks settings:
   - Settings > Engine
   - Resolution: 1920x1080 (not 2560x1440)
   - Frame rate: 60 fps (not 30)
   - Restart BlueStacks

2. Update BlueStacks:
   - Check for updates in BlueStacks
   - Fully update and restart

3. Check input drivers:
   ```batch
   pip install --upgrade pyminitouch
   ```

#### Screen resolution wrong / Bot can't find UI elements

Solutions:
1. Set exact resolution:
   - BlueStacks Settings > Display
   - Resolution: 1920x1080 (exactly)
   - Frame rate: 60
   - Apply & Restart

2. Verify in bot logs:
   - Check `DEBUG = True` in configs.py
   - Look at `debug/frame.png` to see what bot sees

3. Zoom calibration:
   - In Clash of Clans, zoom out completely
   - Bot should see full base

---

### Clash of Clans Issues

#### CoC app won't launch

Solutions:
```batch
REM Force stop CoC
adb shell am force-stop com.supercell.clashofclans

REM Clear cache
adb shell pm clear com.supercell.clashofclans

REM Clear BlueStacks cache
REM BlueStacks > Multi-Instance Manager > Settings > Clear instance data

REM Reinstall CoC from Google Play
```

#### CoC keeps updating / Auto-update failing

Solutions:
1. In Google Play:
   - Settings > System > Auto-update apps > Off

2. Or in bot config:
   ```python
   AUTO_START_BLUESTACKS = False
   ```

3. Manual update:
   - Open CoC manually
   - Let it update
   - Then run bot

#### OCR not working / Bot can't read text

Solutions:
1. Use cloud OCR (Groq):
   - Sign up: https://console.groq.com (free tier available)
   - Get API key
   - Add to configs.py:
     ```python
     GROQ_API_KEY = "your_api_key_here"
     ```

2. Check local OCR:
   - Delete cache: `src/cache.json`
   - Restart bot (will rebuild OCR model)

3. Check GPU support:
   - easyocr uses GPU if available
   - Slow on CPU, faster on GPU
   - Install CUDA for GPU: https://developer.nvidia.com/cuda-downloads

---

### Bot Runtime Issues

#### Bot stops after a few minutes

Solutions:
1. Check Windows power settings:
   ```batch
   powercfg /change monitor-timeout-ac 0
   powercfg /change disk-timeout-ac 0
   ```

2. Set in configs.py:
   ```python
   DISABLE_DEVICE_SLEEP = True
   ```

3. Check firewall blocking bot:
   - Windows Defender Firewall > Allow app through
   - Add Python.exe to whitelist

#### Bot running very slowly / High CPU usage

Solutions:
1. Check CHECK_INTERVAL:
   ```python
   CHECK_INTERVAL = 5  # minutes (default)
   # Increase to 10-15 for less CPU usage
   ```

2. Disable debug mode:
   ```python
   DEBUG = False
   ```

3. Allocate more BlueStacks resources:
   - Settings > Engine
   - RAM: 6-8 GB
   - CPU cores: 4-8

4. Check background processes:
   - Task Manager > Performance
   - Close unnecessary apps

#### Bot crashes with error

Solutions:
1. Get full error:
   ```python
   DEBUG = True  # in configs.py
   ```
   - Look at console output
   - Check `src/logs/` directory

2. Common crashes:
   - IndexError: Screen resolution wrong -> check WINDOW_DIMS
   - ADB error: Connection lost -> restart BlueStacks
   - OCR error: easyocr model issue -> delete cache.json

3. Report issue:
   - https://github.com/Tacticatz/CoC_Bot/issues
   - Include: Windows version, Python version, full error log

---

### Configuration Issues

#### configs.py not found

Solution:
```batch
setup_windows.bat
REM Run setup wizard - it creates configs.py automatically

REM Or manually:
copy src\configs.template.py src\configs.py
```

#### Invalid configuration

Check:
```python
REM In src/configs.py

REM Instance ID must exist in INSTANCE_IDS
INSTANCE_IDS = ["main"]  # This must match BlueStacks instance name

REM ADB address must be reachable
ADB_ADDRESSES = ["127.0.0.1:5555"]  # Test with: adb connect 127.0.0.1:5555

REM Python booleans must be capitalized
AUTO_START_BLUESTACKS = True  # Not 'true'
DEBUG = False  # Not 'false'
```

#### Syntax error in configs.py

Solution:
- Don't edit with Notepad (use Notepad++, VS Code, etc.)
- Check for missing quotes or colons
- Validate at: https://www.python.org/shell/

---

### Network & Web App Issues

#### Cannot access web app at localhost:1234

Solutions:
```batch
REM Check if Flask is running
python app\app.py

REM Check if port is already in use
netstat -ano | findstr :1234

REM If port in use, kill process:
taskkill /PID <process_id> /F

REM Or change port in app/app.py:
REM app.run(host="0.0.0.0", port=8888, debug=True)
```

#### Web app not updating bot status

Solution:
- Make sure `WEB_APP_URL` is set correctly in configs.py
- Test connection:
  ```batch
  curl http://localhost:1234
  ```

---

### Advanced Debugging

Enable verbose logging:

```python
REM In src/configs.py
DEBUG = True
```

Logs will be saved to:
- `src/logs/main.log` (bot logs)
- `debug/frame.png` (screenshot each frame)
- `debug/*.png` (UI element detection)

Check system info:

```batch
REM Python version
python --version

REM ADB version
adb --version

REM BlueStacks version
adb shell getprop ro.build.version.release

REM BlueStacks resolution
adb shell wm size

REM BlueStacks density
adb shell wm density

REM Storage space
adb shell df -h
```

Test individual components:

```batch
REM Test ADB
adb connect 127.0.0.1:5555
adb devices
adb shell am start -n com.supercell.clashofclans/com.supercell.titan.GameApp

REM Test OCR
python -c "from easyocr import Reader; reader = Reader(['en']); print(reader.readtext('test_image.jpg'))"

REM Test OpenCV
python -c "import cv2; print(cv2.__version__)"
```

---

## Getting Help

If none of these solutions work:

1. Check existing issues:
   - https://github.com/Tacticatz/CoC_Bot/issues

2. Ask in Q&A:
   - https://github.com/Tacticatz/CoC_Bot/discussions/categories/q-a

3. Include in report:
   - Windows version: `winver`
   - Python version: `python --version`
   - BlueStacks version: (from app menu)
   - Full error message
   - Steps you've already tried
   - Contents of `src/logs/` if available

---

## Windows 11 Specific Issues

### Windows Defender blocking bot

Solution:
1. Windows Defender > Virus & threat protection
2. Manage settings > Add exclusions
3. Add folder: `C:\path\to\CoC_Bot`
4. Add file: `python.exe`

### Admin privileges required

If running with DISABLE_DEVICE_SLEEP = True:
- Right-click `start_bot.bat`
- "Run as administrator"
- Or modify shortcut > Advanced > "Run as administrator"

### High DPI scaling

If using high DPI (125%, 150%, 200%):
- Right-click `start_bot.bat`
- Properties > Compatibility
- Change high DPI settings
- "Override high DPI scaling"

---

## Performance Benchmarks

Expected performance on Windows 11:

| Component | Time | Notes |
|-----------|------|-------|
| Bot startup | 30-60s | First run slower |
| Config loading | 1-2s | |
| CoC app launch | 10-20s | Via BlueStacks |
| First OCR read | 5-10s | easyocr model loading |
| Subsequent OCR | 0.5-2s | Cached model |
| Groq cloud OCR | 1-3s | Requires internet |
| UI element detection | 0.2-1s | Using template matching |
| Attack execution | 30-120s | Depends on troop deployment |
| Full check cycle | 5-15min | Depends on CHECK_INTERVAL |

If slower than expected:
- Check CPU/RAM usage in Task Manager
- Increase BlueStacks RAM allocation
- Close other applications
- Enable GPU acceleration for OCR

---

For latest help: https://github.com/Tacticatz/CoC_Bot
