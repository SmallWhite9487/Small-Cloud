import requests
import os
from .read_hwid import HWIDManager

class ServerSync:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip('/')
        self.active_token = ""

    def check_connection(self):
        try:
            url = f"{self.base_url}/"
            print(f"[Client] Try to connect to: {url}")
            requests.get(url, timeout=5)
            print(f"[Client] Connection successful!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[Client] Connection failed: {e}")
            return False

    def send_hwid(self):
        hwid_manager = HWIDManager()
        hwid = hwid_manager.get_hwid()
        if not hwid:
            return None
        try:
            url = f"{self.base_url}/"
            resp = requests.post(url, json=hwid, timeout=5)
            if resp.status_code == 200:
                try:
                    resp_data = resp.json()
                    self.active_token = resp_data.get("token", "")
                    print(f"[Client] Security Token successfully cached.")
                except Exception:
                    print(f"[Warning] Failed to parse auth response JSON.")
                return hwid
            return None
        except requests.exceptions.RequestException:
            return None

    def get_manifest(self, hwid):
        try:
            url = f"{self.base_url}/manifest"
            headers = {
                "X-HWID": hwid,
                "X-Secret-Token": self.active_token,
                "User-Agent": "SmallCloudClient/1.0.0 (Python-Requests)"
            }
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"[Client] Manifest request failed with status: {resp.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[Client] Manifest request error: {e}")
            return None

    def download_file(self, hwid, rel_path, local_dir="mods", progress_callback=None):
        try:
            url = f"{self.base_url}/download/{rel_path}"
            headers = {
                "X-HWID": hwid,
                "X-Secret-Token": self.active_token,
                "User-Agent": "SmallCloudClient/1.0.0 (Python-Requests)"
            }
            local_path = os.path.join(local_dir, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with requests.get(url, headers=headers, stream=True, timeout=10) as r:
                if r.status_code == 200:
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                if progress_callback:
                                    progress_callback(len(chunk))
                    return True
                return False
        except Exception:
            return False