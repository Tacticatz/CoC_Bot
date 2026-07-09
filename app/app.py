import os
import time
import json
from pathlib import Path
from collections import deque
from flask import Flask, render_template, jsonify, abort, request
from flask_cors import CORS

import sys
from flask import redirect, session, url_for

PATH = Path(__file__).parent
CACHE_PATH = PATH / "data" / "cache.json"
CACHE_PATH.parent.mkdir(exist_ok=True)
NOTIFICATION_CACHE_SIZE = 3

# Load configuration from src folder
sys.path.append(str(PATH.parent / "src"))
try:
    import configs
except ImportError:
    class configs:
        WEB_APP_PASSWORD = "cocbot-default-password"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cocbot-secret-key-12345")
CORS(app)

# Global tracker for running bot script processes
bot_processes = {}

class Instance:
    def __init__(
        self,
        id,
        run_status="",
        end_time=0,
        exclusions=set(),
        notifications=deque(maxlen=NOTIFICATION_CACHE_SIZE),
        adb_address="127.0.0.1:5555",
        bluestacks_name=""
    ):
        self.id = id
        self.run_status = run_status
        self.end_time = end_time
        self.exclusions = exclusions
        self.notifications = notifications
        self.adb_address = adb_address
        self.bluestacks_name = bluestacks_name
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def to_dict(self):
        return {
            "id": self.id,
            "run_status": self.run_status,
            "end_time": self.end_time,
            "exclusions": sorted(list(self.exclusions)),
            "notifications": list(self.notifications),
            "adb_address": self.adb_address,
            "bluestacks_name": self.bluestacks_name
        }
    
    def get_notifications(self, limit=NOTIFICATION_CACHE_SIZE):
        return list(self.notifications)[-limit:]
    
    def add_notification(self, data):
        self.notifications.append({"time_stamp": time.time(), "data": str(data)})
        data = get_cache()
        data.setdefault("known_instances", {})[self.id] = self.to_dict()
        with open(CACHE_PATH, "w") as f:
            json.dump(data, f, indent=4)

instances = {}

def get_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def get_known_instances():
    global instances
    data = get_cache()
    known_instances = data.get("known_instances", {})
    
    # If cache is empty, seed a default 'main' instance
    if not known_instances:
        instances["main"] = Instance("main", adb_address="127.0.0.1:5555", bluestacks_name="Pie64")
        update_known_instances()
        return

    for id in known_instances:
        id = str(id)
        info = known_instances[id]
        instances[id] = Instance(
            id,
            run_status=info.get("run_status", ""),
            end_time=info.get("end_time", 0),
            exclusions=set(info.get("exclusions", [])),
            notifications=deque(info.get("notifications", []), maxlen=NOTIFICATION_CACHE_SIZE),
            adb_address=info.get("adb_address", "127.0.0.1:5555"),
            bluestacks_name=info.get("bluestacks_name", "")
        )

def update_known_instances():
    global instances
    data = get_cache()
    data["known_instances"] = {id: instances[id].to_dict() for id in instances}
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=4)


# Global screenshot storage
screenshots = {}

@app.before_request
def check_auth():
    # Exclude static files and login/logout endpoints
    if request.path.startswith("/static/") or request.endpoint in ("login", "logout"):
        return

    # Check for secret token in API calls
    token = request.headers.get("X-Bot-Token") or request.args.get("token")
    expected_pw = getattr(configs, "WEB_APP_PASSWORD", "cocbot123")
    if token and token == expected_pw:
        return

    # Otherwise check browser session
    if session.get("logged_in"):
        return

    # For API/AJAX endpoints, return 401 Unauthorized
    api_paths = ["/running", "/status", "/exclude", "/notify", "/notifications", "/instances", "/screenshot_upload", "/screenshot"]
    if any(request.path.endswith(path) for path in api_paths):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # Redirect UI visitors to login
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        expected_pw = getattr(configs, "WEB_APP_PASSWORD", "cocbot123")
        if password == expected_pw:
            session["logged_in"] = True
            return redirect(url_for("home"))
        error = "Ungültiges Passwort!"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/<id>/screenshot_upload", methods=["POST"])
def upload_screenshot(id):
    global screenshots
    file = request.files.get("file")
    if file:
        screenshots[id] = file.read()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No file uploaded"}), 400

@app.route("/<id>/screenshot", methods=["GET"])
def get_screenshot(id):
    img_data = screenshots.get(id)
    if not img_data:
        abort(404)
    from flask import make_response
    response = make_response(img_data)
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", ids=sorted(instances.keys()))

@app.route("/<id>", methods=["GET"])
def handle_instance(id):
    instance = instances.get(id)
    if not instance: abort(404)
    return render_template(
        "instance.html",
        id=id,
        end_time=instance.end_time,
        current_time=time.time(),
        notifications=instance.get_notifications(),
        exclusions=list(instance.exclusions),
        run_status=instance.run_status
    )

@app.route("/current_time", methods=["GET"])
def handle_current_time():
    return {"current_time": time.time()}

@app.route("/<id>/end_time", methods=["GET", "POST"])
def handle_end_time(id):
    global instances
    instance = instances.get(id)
    if not instance: abort(404)
    if request.method == "POST":
        data = request.json.get("time", 0)
        instance.end_time = int(data) * 60 + time.time()
        update_known_instances()
    
    return {"end_time": instance.end_time}

@app.route("/<id>/running", methods=["GET"])
def handle_running(id):
    instance = instances.get(id)
    if not instance: abort(404)
    return {"running": instance.end_time == 0 or instance.end_time < time.time()}

@app.route("/<id>/status", methods=["GET", "POST"])
def handle_status(id):
    global instances
    instance = instances.get(id)
    if not instance: abort(404)
    if request.method == "POST":
        data = request.json
        instance.run_status = data.get("status", "")
        update_known_instances()

    return {"status": instance.run_status}

@app.route("/<id>/exclude", methods=["GET", "POST"])
def handle_exclude(id):
    global instances
    instance = instances.get(id)
    if not instance: abort(404)
    if request.method == "POST":
        data = request.json
        action = data.get("action", "")
        item = data.get("item", "")
        if action == "add":
            instance.exclusions.add(item)
        elif action == "remove":
            instance.exclusions.discard(item)
    return {"exclusions": sorted(list(instance.exclusions))}

@app.route("/<id>/notify", methods=["POST"])
def handle_notify(id):
    global instances
    data = request.json
    instance = instances.get(id)
    if not instance: abort(404)
    instance.add_notification(data)
    return jsonify({"status": "success", "received": data})

@app.route("/<id>/notifications", methods=["POST"])
def handle_notifications(id):
    n = request.json
    instance = instances.get(id)
    if not instance: abort(404)
    return jsonify(instance.get_notifications(n))

@app.route("/instances", methods=["GET", "POST"])
def handle_instances():
    global instances
    if request.method == "POST":
        data = request.json
        id = str(data.get("id", "")).strip()
        adb = str(data.get("adb_address", "127.0.0.1:5555")).strip()
        bs_name = str(data.get("bluestacks_name", "")).strip()
        if id == "":
            return jsonify({"status": "error", "message": "Invalid ID"}), 400
        if id not in instances:
            instances[id] = Instance(id, adb_address=adb, bluestacks_name=bs_name)
            update_known_instances()
        else:
            # Update existing parameters
            instances[id].adb_address = adb
            instances[id].bluestacks_name = bs_name
            update_known_instances()
        return jsonify({"status": "success", "id": id})

    adb_addresses = {id: instances[id].adb_address for id in instances}
    return jsonify({
        "ids": sorted(instances.keys()),
        "adb_addresses": adb_addresses
    })

@app.route("/<id>/delete", methods=["POST"])
def delete_instance(id):
    global instances
    if id in instances:
        del instances[id]
        update_known_instances()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Instance not found"}), 404

@app.route("/api/settings", methods=["GET", "POST"])
def handle_settings():
    data = get_cache()
    settings = data.setdefault("settings", {})
    if request.method == "POST":
        new_settings = request.json
        for key, val in new_settings.items():
            settings[key] = val
        update_known_instances()
        return jsonify({"status": "success", "settings": settings})
    return jsonify({"settings": settings})

@app.route("/api/instances/clone", methods=["POST"])
def clone_instance():
    data = request.json
    source_id = data.get("source_id", "main")
    new_id = str(data.get("new_id", "")).strip()
    
    if not new_id:
        return jsonify({"status": "error", "message": "Invalid new ID"}), 400
        
    import json
    from pathlib import Path
    import subprocess
    import re
    
    mim_path = r"C:\ProgramData\BlueStacks_nxt\Engine\UserData\MimMetaData.json"
    if not Path(mim_path).exists():
        return jsonify({"status": "error", "message": "MimMetaData.json not found"}), 500
        
    try:
        mim_data = json.loads(Path(mim_path).read_text(encoding="utf-8"))
        instances_map = {inst['Name']: inst["InstanceName"] for inst in mim_data["Organization"]}
        internal_source = instances_map.get(source_id)
        if not internal_source:
            internal_source = "Pie64"
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed reading MimMetaData: {str(e)}"}), 500
        
    manager_path = r"C:\Program Files\BlueStacks_nxt\HD-MultiInstanceManager.exe"
    if not Path(manager_path).exists():
        return jsonify({"status": "error", "message": "BlueStacks Multi-Instance Manager not found"}), 500
        
    try:
        proc = subprocess.run(
            [manager_path, "clone", "--source", internal_source, "--name", new_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if proc.returncode != 0:
            return jsonify({"status": "error", "message": f"Clone command failed: {proc.stderr}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed executing clone: {str(e)}"}), 500
        
    # Wait briefly for metadata to update
    time.sleep(2)
    
    try:
        mim_data = json.loads(Path(mim_path).read_text(encoding="utf-8"))
        instances_map = {inst['Name']: inst["InstanceName"] for inst in mim_data["Organization"]}
        internal_new = instances_map.get(new_id)
        if not internal_new:
            return jsonify({"status": "error", "message": "Cloned instance not found in metadata"}), 500
            
        conf_path = Path(r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf")
        adb_port = 5555
        if conf_path.exists():
            content = conf_path.read_text(encoding="utf-8", errors="ignore")
            for _ in range(5):
                match = re.search(rf'bst\.instance\.{internal_new}\.status\.adb_port="(\d+)"', content)
                if match:
                    adb_port = int(match.group(1))
                    break
                time.sleep(1)
                content = conf_path.read_text(encoding="utf-8", errors="ignore")
                
        adb_address = f"127.0.0.1:{adb_port}"
        instances[new_id] = Instance(new_id, adb_address=adb_address, bluestacks_name=internal_new)
        update_known_instances()
        
        return jsonify({"status": "success", "id": new_id, "adb_address": adb_address})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed registering cloned instance: {str(e)}"}), 500

@app.route("/<id>/click", methods=["POST"])
def remote_click(id):
    instance = instances.get(id)
    if not instance: abort(404)
    data = request.json
    x_rel = float(data.get("x"))
    y_rel = float(data.get("y"))
    x_px = int(x_rel * 1920)
    y_px = int(y_rel * 1080)
    
    import subprocess
    adb_addr = instance.adb_address
    subprocess.run(["adb", "-s", adb_addr, "shell", "input", "tap", str(x_px), str(y_px)])
    return jsonify({"status": "success"})

@app.route("/<id>/type", methods=["POST"])
def remote_type(id):
    instance = instances.get(id)
    if not instance: abort(404)
    text = request.json.get("text", "")
    safe_text = text.replace(" ", "%s").replace("'", "\\'")
    
    import subprocess
    adb_addr = instance.adb_address
    subprocess.run(["adb", "-s", adb_addr, "shell", "input", "text", safe_text])
    return jsonify({"status": "success"})

@app.route("/<id>/keyevent", methods=["POST"])
def remote_keyevent(id):
    instance = instances.get(id)
    if not instance: abort(404)
    key = int(request.json.get("key", 67))
    
    import subprocess
    adb_addr = instance.adb_address
    subprocess.run(["adb", "-s", adb_addr, "shell", "input", "keyevent", str(key)])
    return jsonify({"status": "success"})

@app.route("/<id>/start_bot", methods=["POST"])
def start_bot(id):
    global bot_processes
    if id not in instances: abort(404)
    
    # Check if already running
    proc, _ = bot_processes.get(id, (None, None))
    if proc is not None and proc.poll() is None:
        return jsonify({"status": "error", "message": "Bot is already running"}), 400
        
    import subprocess, sys
    python_path = str(PATH.parent / ".venv" / "Scripts" / "python.exe")
    if sys.platform != "win32":
        python_path = str(PATH.parent / ".venv" / "bin" / "python")
        
    main_py = str(PATH.parent / "src" / "main.py")
    
    log_dir = PATH.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file_path = log_dir / f"{id}.log"
    
    # Clear old log files to keep them readable
    try:
        if log_file_path.exists():
            log_file_path.write_text("")
    except:
        pass
        
    try:
        log_file = open(log_file_path, "a", encoding="utf-8")
        
        # Start bot as a decoupled subprocess
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        new_proc = subprocess.Popen(
            [python_path, main_py, "--id", id, "--gui", "False"],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=str(PATH.parent),
            creationflags=creation_flags
        )
        bot_processes[id] = (new_proc, log_file)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to start process: {str(e)}"}), 500

@app.route("/<id>/stop_bot", methods=["POST"])
def stop_bot(id):
    global bot_processes
    proc, log_file = bot_processes.pop(id, (None, None))
    if proc:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            try: proc.kill()
            except: pass
        if log_file:
            try: log_file.close()
            except: pass
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Bot is not running"}), 400

@app.route("/<id>/bot_status", methods=["GET"])
def get_bot_status(id):
    proc, _ = bot_processes.get(id, (None, None))
    is_running = proc is not None and proc.poll() is None
    return jsonify({"running": is_running})

@app.route("/<id>/bot_log", methods=["GET"])
def get_bot_log(id):
    log_path = PATH.parent / "logs" / f"{id}.log"
    if not log_path.exists():
        return jsonify({"log": "Kein Log vorhanden. Starte den Bot zuerst!"})
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        # Return last 45 lines to keep payload clean
        return jsonify({"log": "".join(lines[-45:])})
    except Exception as e:
        return jsonify({"log": f"Log-Fehler: {str(e)}"})

import atexit
def cleanup_bot_processes():
    global bot_processes
    for id in list(bot_processes.keys()):
        proc, log_file = bot_processes.pop(id, (None, None))
        if proc:
            try:
                proc.terminate()
                if log_file: log_file.close()
            except:
                pass
atexit.register(cleanup_bot_processes)

@app.after_request
def add_cache_headers(response):
    if request.path.startswith("/static/"):
        # Cache static files for 30 days
        response.headers["Cache-Control"] = "public, max-age=2592000"
        response.headers.pop("Pragma", None)
        response.headers.pop("Expires", None)
    else:
        # No caching for dynamic routes
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

get_known_instances()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234, debug=True)