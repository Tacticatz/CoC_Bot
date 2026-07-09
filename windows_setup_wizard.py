import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import webbrowser
import time

class WindowsSetupWizard:
    """Interactive Windows 11 setup wizard with automatic prerequisite installation."""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.app_dir = Path(__file__).parent.resolve()
        self.config_file = self.home_dir / ".coc_bot_setup.json"
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load previous setup state if exists."""
        if self.config_file.exists():
            try:
                return json.load(open(self.config_file, 'r'))
            except:
                pass
        return {}
    
    def _save_state(self):
        """Save setup state for resuming."""
        with open(self.config_file, 'w') as f:
            json.dump(self.state, f, indent=4)
    
    def check_python_version(self) -> bool:
        """Verify Python 3.11+"""
        if sys.version_info >= (3, 11):
            print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")
            return True
        print(f"[ERROR] Python {sys.version_info.major}.{sys.version_info.minor} - Need 3.11+")
        print(f"        Download: https://www.python.org/downloads/")
        return False
    
    def check_adb_installed(self) -> bool:
        """Check if Android Debug Bridge is installed and in PATH."""
        try:
            result = subprocess.run(['adb', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[OK] ADB installed")
                return True
        except FileNotFoundError:
            pass
        
        print("[ERROR] ADB (Android Debug Bridge) not found")
        return False
    
    def check_bluestacks_installed(self) -> Optional[str]:
        """Detect BlueStacks installation path."""
        common_paths = [
            r"C:\Program Files\BlueStacks_nxt\HD-Player.exe",
            r"C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe",
            Path.home() / "AppData" / "Local" / "BlueStacks_nxt" / "HD-Player.exe",
            r"D:\Program Files\BlueStacks_nxt\HD-Player.exe",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                print(f"[OK] BlueStacks found: {path}")
                return str(path)
        
        print("[ERROR] BlueStacks not found in default locations")
        return None
    
    def check_adb_connection(self) -> bool:
        """Test ADB connection to BlueStacks."""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=5)
            if "127.0.0.1:5555" in result.stdout or "emulator" in result.stdout:
                print("[OK] ADB connection works")
                return True
        except Exception as e:
            print(f"[WARNING] ADB connection test failed: {e}")
            return False
        
        print("[ERROR] No Android devices found via ADB")
        return False
    
    def install_adb(self) -> bool:
        """Download and install Android Debug Bridge."""
        print("\n[INFO] Installing Android Debug Bridge...")
        
        try:
            import urllib.request
            
            adb_dir = self.home_dir / "AppData" / "Local" / "adb"
            adb_dir.mkdir(parents=True, exist_ok=True)
            
            url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
            zip_path = adb_dir / "platform-tools.zip"
            
            print(f"        Downloading from {url}...")
            urllib.request.urlretrieve(url, zip_path)
            
            import zipfile
            print("        Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(adb_dir)
            
            zip_path.unlink()
            
            adb_bin = adb_dir / "platform-tools"
            self._add_to_path(str(adb_bin))
            
            print(f"[OK] ADB installed to {adb_bin}")
            self.state['adb_installed'] = True
            self._save_state()
            return True
            
        except Exception as e:
            print(f"[ERROR] ADB installation failed: {e}")
            return False
    
    def _add_to_path(self, path: str):
        """Add directory to Windows PATH environment variable."""
        try:
            import winreg
            
            registry_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as reg:
                with winreg.OpenKey(reg, registry_path, 0, winreg.KEY_READ) as key:
                    path_value, _ = winreg.QueryValueEx(key, "Path")
            
            if path not in path_value:
                new_path = f"{path_value};{path}"
                with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as reg:
                    with winreg.OpenKey(reg, registry_path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"        Added to PATH: {path}")
                os.system('setx TEMP %TEMP%')
        except Exception as e:
            print(f"        [WARNING] Could not auto-add to PATH: {e}")
            print(f"        Manual fix: Add '{path}' to System Environment Variables")
    
    def install_python_deps(self) -> bool:
        """Install Python package dependencies."""
        print("\n[INFO] Installing Python dependencies...")
        
        try:
            venv_path = self.app_dir / '.venv'
            if not venv_path.exists():
                print("        Creating virtual environment...")
                subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
            
            python_exe = venv_path / "Scripts" / "python.exe"
            
            print("        Upgrading pip...")
            subprocess.run([str(python_exe), '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         capture_output=True, check=False)
            
            req_files = [
                self.app_dir / "src" / "requirements.txt",
                self.app_dir / "app" / "requirements.txt",
            ]
            
            for req_file in req_files:
                if req_file.exists():
                    print(f"        Installing {req_file.name}...")
                    subprocess.run([str(python_exe), '-m', 'pip', 'install', '-r', str(req_file)],
                                 check=True)
            
            print("[OK] Python dependencies installed")
            self.state['python_deps_installed'] = True
            self._save_state()
            return True
            
        except Exception as e:
            print(f"[ERROR] Dependency installation failed: {e}")
            return False
    
    def create_config_interactive(self) -> bool:
        """Interactive configuration wizard."""
        print("\n[INFO] Configuration Setup")
        print("=" * 50)
        
        config_path = self.app_dir / "src" / "configs.py"
        
        if config_path.exists():
            response = input("configs.py already exists. Overwrite? (y/n): ").lower()
            if response != 'y':
                print("        Skipping configuration")
                return True
        
        print("\n[STEP 1] Instance Setup")
        instance_id = input("        BlueStacks instance name [main]: ").strip() or "main"
        adb_address = input("        ADB address [127.0.0.1:5555]: ").strip() or "127.0.0.1:5555"
        
        print("\n[STEP 2] Optional Features")
        web_app_url = input("        Web app URL (leave empty to skip): ").strip()
        telegram_token = input("        Telegram bot token (leave empty to skip): ").strip()
        groq_api_key = input("        Groq API key for faster OCR (leave empty to skip): ").strip()
        
        config_content = self._generate_config(
            instance_id=instance_id,
            adb_address=adb_address,
            web_app_url=web_app_url,
            telegram_token=telegram_token,
            groq_api_key=groq_api_key,
        )
        
        config_path.write_text(config_content)
        print(f"[OK] Config saved to {config_path}")
        return True
    
    def _generate_config(self, **kwargs) -> str:
        """Generate configs.py from template with user inputs."""
        template_path = self.app_dir / "src" / "configs.template.py"
        template = template_path.read_text()
        
        replacements = {
            'WEB_APP_URL = ""': f'WEB_APP_URL = "{kwargs["web_app_url"]}"',
            'TELEGRAM_BOT_TOKEN = ""': f'TELEGRAM_BOT_TOKEN = "{kwargs["telegram_token"]}"',
            'GROQ_API_KEY = ""': f'GROQ_API_KEY = "{kwargs["groq_api_key"]}"',
            'INSTANCE_IDS = ["main"]': f'INSTANCE_IDS = ["{kwargs["instance_id"]}"]',
            'ADB_ADDRESSES = ["127.0.0.1:5555"]': f'ADB_ADDRESSES = ["{kwargs["adb_address"]}"]',
        }
        
        for old, new in replacements.items():
            template = template.replace(old, new)
        
        return template
    
    def test_setup(self) -> Tuple[bool, str]:
        """Run comprehensive setup tests."""
        print("\n[INFO] Testing Setup")
        print("=" * 50)
        
        issues = []
        
        if not self.check_python_version():
            issues.append("Python 3.11+ required")
        
        if not self.check_adb_installed():
            issues.append("ADB not installed")
        
        bs_path = self.check_bluestacks_installed()
        if not bs_path:
            issues.append("BlueStacks not found")
        
        if not self.check_adb_connection():
            issues.append("ADB cannot connect to device")
            print("        Hint: Make sure BlueStacks is running and ADB is enabled")
        
        config_path = self.app_dir / "src" / "configs.py"
        if config_path.exists():
            print("[OK] configs.py exists")
        else:
            issues.append("configs.py not found")
        
        if issues:
            return False, "\n".join(f"  [ERROR] {issue}" for issue in issues)
        
        return True, "[OK] All checks passed!"
    
    def launch_web_setup(self):
        """Launch interactive web-based setup GUI."""
        print("\n[INFO] Launching Web Setup Interface...")
        
        from flask import Flask, render_template_string, request, jsonify
        
        app = Flask(__name__)
        wizard = self
        
        HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CoC Bot - Windows 11 Setup Wizard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .content { padding: 40px; }
        .step { margin-bottom: 30px; display: none; }
        .step.active { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .step h2 { font-size: 20px; margin-bottom: 20px; color: #333; }
        .check-item {
            padding: 15px; margin-bottom: 10px; border-radius: 8px;
            display: flex; align-items: center; gap: 12px;
        }
        .check-item.success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .check-item.error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .check-item.warning { background: #fff3cd; border: 1px solid #ffeeba; color: #856404; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
        .input-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; }
        .input-group input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        .input-group small { display: block; margin-top: 4px; color: #999; font-size: 12px; }
        .buttons { display: flex; gap: 12px; justify-content: space-between; margin-top: 30px; }
        button { padding: 12px 24px; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
        .btn-secondary { background: #eee; color: #333; }
        .btn-secondary:hover { background: #ddd; }
        .progress-bar { height: 6px; background: #eee; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); width: 0%; transition: width 0.3s; }
        .alert { padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .alert.success { background: #d4edda; color: #155724; }
        .alert.error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
        <div class="header">
            <h1>CoC Bot Setup</h1>
            <p>Windows 11 Setup Wizard</p>
        </div>
        <div class="content">
            <div class="step active" id="step1">
                <h2>System Checks</h2>
                <div id="checksContainer"></div>
                <div class="buttons"><button class="btn-secondary" onclick="goStep(2)">Next</button></div>
            </div>
            <div class="step" id="step2">
                <h2>Install Prerequisites</h2>
                <div id="installContainer"></div>
                <div class="buttons">
                    <button class="btn-secondary" onclick="goStep(1)">Back</button>
                    <button class="btn-primary" onclick="goStep(3)">Next</button>
                </div>
            </div>
            <div class="step" id="step3">
                <h2>Configuration</h2>
                <div class="input-group">
                    <label>BlueStacks Instance ID</label>
                    <input type="text" id="instanceId" value="main" placeholder="main">
                    <small>Must match your BlueStacks multi-instance name</small>
                </div>
                <div class="input-group">
                    <label>ADB Address</label>
                    <input type="text" id="adbAddress" value="127.0.0.1:5555" placeholder="127.0.0.1:5555">
                    <small>Default BlueStacks ADB port is 5555</small>
                </div>
                <div class="input-group">
                    <label>Telegram Bot Token (Optional)</label>
                    <input type="text" id="telegramToken" placeholder="Leave empty to skip">
                    <small>For bot notifications. Get from @BotFather</small>
                </div>
                <div class="input-group">
                    <label>Groq API Key (Optional)</label>
                    <input type="text" id="groqKey" placeholder="Leave empty to skip">
                    <small>For faster OCR. Free tier available at console.groq.com</small>
                </div>
                <div class="buttons">
                    <button class="btn-secondary" onclick="goStep(2)">Back</button>
                    <button class="btn-primary" onclick="saveConfig()">Save & Test</button>
                </div>
            </div>
            <div class="step" id="step4">
                <h2>Setup Complete</h2>
                <div id="resultContainer"></div>
                <div class="buttons"><button class="btn-primary" onclick="location.reload()">Restart</button></div>
            </div>
        </div>
    </div>
    <script>
        let currentStep = 1;
        function goStep(step) {
            document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
            document.getElementById('step' + step).classList.add('active');
            document.getElementById('progressFill').style.width = (step * 25) + '%';
            currentStep = step;
            if (step === 1) loadChecks();
            if (step === 2) loadInstalls();
        }
        function loadChecks() {
            fetch('/api/checks').then(r => r.json()).then(data => {
                let html = '';
                for (let [name, status] of Object.entries(data)) {
                    const icon = status === true ? '[OK]' : status === false ? '[ERROR]' : '[WARNING]';
                    const cls = status === true ? 'success' : status === false ? 'error' : 'warning';
                    html += `<div class="check-item ${cls}"><span>${icon} ${name}</span></div>`;
                }
                document.getElementById('checksContainer').innerHTML = html;
            });
        }
        function loadInstalls() {
            fetch('/api/install-status').then(r => r.json()).then(data => {
                let html = '';
                for (let [name, installed] of Object.entries(data)) {
                    const btn = !installed ? `<button class="btn-primary" onclick="install('${name}')">Install</button>` : '<span style="color:green">[OK] Done</span>';
                    html += `<div style="display:flex; justify-content:space-between; align-items:center; padding:15px; background:#f5f5f5; border-radius:6px; margin-bottom:10px;"><span>${name}</span>${btn}</div>`;
                }
                document.getElementById('installContainer').innerHTML = html;
            });
        }
        function install(module) {
            fetch(`/api/install/${module}`, {method: 'POST'}).then(r => r.json()).then(data => {
                if (data.success) {
                    alert('[OK] ' + module + ' installed successfully!');
                    loadInstalls();
                } else {
                    alert('[ERROR] Installation failed: ' + data.error);
                }
            });
        }
        function saveConfig() {
            const config = {
                instanceId: document.getElementById('instanceId').value,
                adbAddress: document.getElementById('adbAddress').value,
                telegramToken: document.getElementById('telegramToken').value,
                groqKey: document.getElementById('groqKey').value,
            };
            fetch('/api/save-config', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(config)}).then(r => r.json()).then(data => {
                if (data.success) {
                    fetch('/api/test-setup').then(r => r.json()).then(test => {
                        let html = test.success ? '<div class="alert success">[OK] All tests passed! Ready to run.</div>' : '<div class="alert error">' + test.message + '</div>';
                        document.getElementById('resultContainer').innerHTML = html;
                        goStep(4);
                    });
                } else {
                    alert('[ERROR] Failed to save config: ' + data.error);
                }
            });
        }
        loadChecks();
    </script>
</body>
</html>'''
        
        @app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
        
        @app.route('/api/checks')
        def api_checks():
            return jsonify({
                "Python 3.11+": sys.version_info >= (3, 11),
                "ADB": wizard.check_adb_installed(),
                "BlueStacks": wizard.check_bluestacks_installed() is not None,
                "Config file": (wizard.app_dir / "src" / "configs.py").exists(),
            })
        
        @app.route('/api/install-status')
        def api_install_status():
            return jsonify({
                "Python Dependencies": wizard.state.get('python_deps_installed', False),
                "Android Debug Bridge": wizard.state.get('adb_installed', False),
            })
        
        @app.route('/api/install/<module>', methods=['POST'])
        def api_install(module):
            if module == 'Python Dependencies':
                success = wizard.install_python_deps()
            elif module == 'Android Debug Bridge':
                success = wizard.install_adb()
            else:
                return jsonify({'success': False, 'error': 'Unknown module'})
            return jsonify({'success': success, 'error': '' if success else 'Installation failed'})
        
        @app.route('/api/save-config', methods=['POST'])
        def api_save_config():
            try:
                data = request.json
                wizard.state['instance_id'] = data['instanceId']
                wizard.state['adb_address'] = data['adbAddress']
                wizard._save_state()
                config_content = wizard._generate_config(
                    instance_id=data['instanceId'],
                    adb_address=data['adbAddress'],
                    web_app_url='',
                    telegram_token=data['telegramToken'],
                    groq_api_key=data['groqKey'],
                )
                config_path = wizard.app_dir / "src" / "configs.py"
                config_path.write_text(config_content)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @app.route('/api/test-setup')
        def api_test_setup():
            success, message = wizard.test_setup()
            return jsonify({'success': success, 'message': message})
        
        port = 5555
        url = f"http://localhost:{port}"
        print(f"        Opening {url} in browser...")
        webbrowser.open(url)
        app.run(host='localhost', port=port, debug=False)
    
    def run(self):
        """Run the complete setup wizard."""
        print("\n" + "=" * 50)
        print("CoC Bot - Windows 11 Setup Wizard")
        print("=" * 50)
        
        if not self.check_python_version():
            print("\n[ERROR] Setup aborted: Python 3.11+ is required")
            return False
        
        print("\nSetup Mode:")
        print("1. Automatic (Recommended) - Web GUI with step-by-step guide")
        print("2. Manual - Command line setup")
        print("3. Quick - Skip optional steps")
        
        choice = input("\nSelect mode [1]: ").strip() or "1"
        
        if choice == "1":
            self.launch_web_setup()
        elif choice == "2":
            self._manual_setup()
        elif choice == "3":
            self._quick_setup()
        else:
            print("Invalid choice")
            return False
        
        return True
    
    def _manual_setup(self):
        """Command-line manual setup."""
        print("\nManual Setup\n")
        
        if not self.check_adb_installed():
            if input("Install ADB now? (y/n): ").lower() == 'y':
                self.install_adb()
        
        if not self.check_bluestacks_installed():
            print("Please install BlueStacks manually: https://www.bluestacks.com/")
            input("Press Enter when done...")
        
        if input("Install Python dependencies? (y/n): ").lower() == 'y':
            self.install_python_deps()
        
        if input("Run configuration wizard? (y/n): ").lower() == 'y':
            self.create_config_interactive()
        
        success, message = self.test_setup()
        print("\n" + message)
    
    def _quick_setup(self):
        """Quick setup skipping optional features."""
        print("\nQuick Setup\n")
        
        self.install_python_deps()
        
        config_content = self._generate_config(
            instance_id="main",
            adb_address="127.0.0.1:5555",
            web_app_url="",
            telegram_token="",
            groq_api_key="",
        )
        
        config_path = self.app_dir / "src" / "configs.py"
        config_path.write_text(config_content)
        
        print("[OK] Quick setup complete!")


if __name__ == "__main__":
    wizard = WindowsSetupWizard()
    wizard.run()
