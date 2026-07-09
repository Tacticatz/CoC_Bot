<h1 align="center">Clash of Clans Bot</h1>
<p align="center">
    <a href="https://youtu.be/RTaFCiD5v3o">
        <img src="media/Cover_Image.png" alt="Cover Image" width="25%">
    </a>
    <br>
    <a href="https://youtu.be/RTaFCiD5v3o">Click for Demo Video</a>
</p>

## Automated Features (Both Villages)
* Resource collection
* Hero upgrades
* Building upgrades
* Laboratory upgrades
* Assistant assignment
* Normal attacks
* Full upgrade priority control
* Multiple accounts

## Quality of Life Features
* View bot status on desktop or web app
* Resume / pause bot execution from desktop or web app
* iPhone shortcut to auto resume / pause bot when CoC is opened by user
* Telegram and web app notifications
* Automatic CoC app updates
* Automatic BlueStacks instance launch / shutdown

## Quick Start for Windows 11

### Method 1: Automated Setup (Recommended)

1. Download the repository
2. Double-click `setup_windows.bat`
3. Follow the interactive web GUI setup
4. Done! Start bot with `start_bot.bat`

### Method 2: Manual Setup

See WINDOWS_SETUP.md for detailed instructions

## Dependencies

1. [Android Debug Bridge](https://developer.android.com/tools/releases/platform-tools)
    * Add to system path
        * Verify with: `adb --version`
2. [BlueStacks](https://www.bluestacks.com/)
    * Device profile: Samsung Galaxy S22 Ultra
    * Display resolution: 1920 x 1080
    * Frame rate: 60 (NOTE: Inconsistent touch events at lower fps)
    * Enable Android Debug Bridge
    * In Multi-Instance Manager, rename instances to match instance IDs in `configs.py` (the default ID is main)
    * Install Clash of Clans from Google Play
        * Default troop deployment size
        * Standard or XL scenery

## Default Setup Instructions

1. Install and configure external dependencies
2. Download the latest release for your OS
    * Prebuilt releases are minimally configured and only support standard features
    * Releases are built for MacOS (Apple Silicon) and Windows only
    * GUI and CLI versions are available with each release
3. MacOS users must allow the app/binary to run by going to "Settings > Privacy & Security" and clicking "Open Anyways"

## Custom Setup Instructions (Recommended)

1. Install and configure external dependencies
2. Install python dependencies with setup.py
3. Enter user configurations in `configs.py`
    * setup.py creates `configs.py` from configs.template.py
    * By default, all capabilities are enabled. Many configurations can be overridden in real time if using the desktop or web app
    * If using priority upgrades, instructions for defining upgrade priorities can be found in `configs.py`
    * To configure Telegram notifications, first set up a Telegram bot
    * If local OCR is too slow, you can offload it to groq (https://console.groq.com)

4. Start web app: `python app/app.py`
    * It is recommended to host the web app on pythonanywhere using the provided wsgi.py template
    * If hosting from a personal device, configure port forwarding as necessary
    * Each bot instance can be accessed at `WEB_APP_URL/<instance_id>` (the default instance ID is `main`)

5. Setup iPhone shortcut (optional)
    * Download Scriptable and create a new script named "CoC Bot Script"
    * Open the provided shortcut
    * Enter your `WEB_APP_URL` into the `url` item of the Dictionary
    * Add your instance ids to the `ids` array in the Dictionary
    * Create an Automation task that runs when CoC opens

6. Start the bot: `python src/main.py`
    * By default, the bot is configured to start and stop its BlueStacks instance automatically
    * If this behavior is undesired or causing issues, set `AUTO_START_BLUESTACKS = False`
    * On MacOS, if `DISABLE_DEVICE_SLEEP = True`, user password is required
    * The BlueStacks window can be minimized without disrupting the bot
    * If not using the bot for development, it can be built into an executable using build.sh
    * To run bots for multiple accounts, create additional BlueStacks instances

## Miscellaneous

* Please report issues in the Issues Tab
* For help with setup or usage, open a discussion in Q&A
* Suggest new features in Ideas

## Windows 11 Additional Resources

* See WINDOWS_SETUP.md for detailed Windows 11 setup guide
* See TROUBLESHOOTING.md for Windows-specific troubleshooting
