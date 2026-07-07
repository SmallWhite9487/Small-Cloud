import os
import sys

def get_app_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.dirname(os.path.abspath(__file__))


def ensure_server_workspace(base_dir):
    os.makedirs(base_dir, exist_ok=True)

    env_path = os.path.join(base_dir, ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as handle:
            handle.write(
                "# SmallCloud Server configuration\n"
                "SERVER_SECRET_TOKEN=change_me_to_a_long_random_string\n"
                "SERVER_THREADS=32\n"
            )
        print(f"[Server] Created preset .env at: {env_path}")

    whitelist_path = os.path.join(base_dir, "whitelist.txt")
    if not os.path.exists(whitelist_path):
        with open(whitelist_path, "w", encoding="utf-8") as handle:
            handle.write("# SmallCloud Whitelist\n# Add one authorized HWID per line.\n")
        print(f"[Server] Created preset whitelist at: {whitelist_path}")

    uploads_dir = os.path.join(base_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    print(f"[Server] Ensured uploads directory exists at: {uploads_dir}")

    return base_dir, env_path, whitelist_path, uploads_dir


APP_BASE_DIR = get_app_base_dir()
os.chdir(APP_BASE_DIR)
os.environ["SMALLCLOUD_BASE_DIR"] = APP_BASE_DIR
os.environ["SMALLCLOUD_UPLOADS_DIR"] = os.path.join(APP_BASE_DIR, "uploads")
ensure_server_workspace(APP_BASE_DIR)
modules_path = os.path.join(APP_BASE_DIR, "modules")
if modules_path not in sys.path:
    sys.path.append(modules_path)

from modules.server import ServerApp

class Main:
    def __init__(self):
        self.server_app = ServerApp()

    def run(self):
        self.server_app.start()

if __name__ == "__main__":
    print("[Server] Please edit .env and whitelist.txt before allowing clients to connect.")
    main_app = Main()
    main_app.run()