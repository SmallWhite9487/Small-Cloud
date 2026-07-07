from flask import Flask, send_file, request, jsonify
from waitress import serve
import os
import secrets
from dotenv import load_dotenv
from .whitelist import WhitelistManager
from .file_manager import FileManager

modules_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(modules_dir)
base_dir = os.environ.get("SMALLCLOUD_BASE_DIR") or server_dir
base_dir = os.path.abspath(base_dir)
os.environ["SMALLCLOUD_BASE_DIR"] = base_dir
# Do not change cwd here; main should already set it to APP_BASE_DIR

env_path = os.path.join(base_dir, '.env')

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print(f"[Server] Successfully loaded configuration from .env: {env_path}")
else:
    print(f"[Server][Warning] .env file not found at {env_path}. Safe fallback activated.")

SERVER_SECRET_TOKEN = os.getenv("SERVER_SECRET_TOKEN")
if not SERVER_SECRET_TOKEN:
    SERVER_SECRET_TOKEN = secrets.token_hex(24)
    print(f"[Server][Warning] No static token found in .env. Generated a temporary random token for this session.")

app = Flask(__name__)

whitelist_manager = WhitelistManager()
file_manager = FileManager()

def is_request_authorized(req):
    ua = req.headers.get("User-Agent", "").lower()
    if "curl" in ua:
        return False

    hwid = req.headers.get("X-HWID")
    if not hwid or not whitelist_manager.is_authorized(hwid):
        return False

    token = req.headers.get("X-Secret-Token")
    if token != SERVER_SECRET_TOKEN:
        return False

    return True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "404 Not Found", 404

    if request.method == 'POST':
        hwid = request.get_json(silent=True)
        if hwid is None:
            hwid = request.get_data(as_text=True)
            
        client_ip = request.remote_addr
        print(f"[Server] Received Auth Request from IP: {client_ip}")

        if not hwid:
            return "Bad Request", 400

        if whitelist_manager.is_authorized(hwid):
            print(f"├── HWID: {hwid}\n└── Status: Authorized (200)")
            return jsonify({"status": "success", "token": SERVER_SECRET_TOKEN}), 200
        else:
            print(f"├── HWID: {hwid}\n└── Status: Denied (403)")
            whitelist_manager.record_pending_hwid(hwid, client_ip)
            return "Access Denied.", 403

@app.route('/manifest', methods=['GET'])
def get_manifest():
    client_ip = request.remote_addr
    
    if not is_request_authorized(request):
        print(f"[Server][Warning] Unauthorized manifest request from IP: {client_ip}")
        return jsonify({"error": "Unauthorized."}), 403
        
    current_manifest = file_manager.generate_manifest()
    return jsonify(current_manifest), 200

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    client_ip = request.remote_addr

    if not is_request_authorized(request):
        print(f"[Server][Warning] Unauthorized file download request from IP: {client_ip}")
        return "Unauthorized access.", 403

    cleaned_filename = filename.replace("..", "").strip("/")
    
    safe_path = os.path.abspath(os.path.join(file_manager.mods_dir, cleaned_filename))
    base_path = os.path.abspath(file_manager.mods_dir)

    if not safe_path.startswith(base_path):
        print(f"[Server][Warning] Invalid file path requested! Path: {filename}, IP: {client_ip}")
        return "Invalid file path.", 400

    if not os.path.exists(safe_path) or os.path.isdir(safe_path):
        return "File not found.", 404

    return send_file(safe_path)

class ServerApp:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 5000
        
        raw_threads = os.getenv("SERVER_THREADS", "32")
        if raw_threads.isdigit():
            self.SERVER_THREADS = int(raw_threads)
        else:
            print(f"[Server][Warning] Detected invalid SERVER_THREADS format in .env ('{raw_threads}'), automatically downgraded to default 32 threads.")
            self.SERVER_THREADS = 32

    def start(self):
        print("===============================================")
        print(f"| SmallCloud Secured Server is running        |")
        print(f"| Listening locally on: http://{self.host}:{self.port} |")
        print("===============================================")
        serve(app, host=self.host, port=self.port, threads=self.SERVER_THREADS)