import os


class WhitelistManager:
    def __init__(self, whitelist_path=None, pending_path=None):
        base_dir = os.environ.get("SMALLCLOUD_BASE_DIR", os.getcwd())
        self.whitelist_path = whitelist_path or os.path.join(base_dir, "whitelist.txt")
        self.pending_path = pending_path or os.path.join(base_dir, "whitelist_pending.txt")
        self.allowed_hwids = set()
        self.load_whitelist()

    def load_whitelist(self):
        if os.path.exists(self.whitelist_path):
            with open(self.whitelist_path, "r", encoding="utf-8") as f:
                self.allowed_hwids = {line.strip() for line in f if line.strip() and not line.startswith("#")}
        else:
            with open(self.whitelist_path, "w", encoding="utf-8") as f:
                f.write("# SmallCloud Whitelist - Paste authorized HWIDs here\n")
            self.allowed_hwids = set()
        print(f"[Server] Successfully loaded {len(self.allowed_hwids)} authorized HWID(s).")

    def is_authorized(self, hwid):
        return hwid in self.allowed_hwids

    def record_pending_hwid(self, hwid, ip):
        existing_pendings = set()
        if os.path.exists(self.pending_path):
            with open(self.pending_path, "r", encoding="utf-8") as f:
                existing_pendings = {line.strip() for line in f}

        record_line = f"{hwid} # IP: {ip}"
        if record_line not in existing_pendings:
            with open(self.pending_path, "a", encoding="utf-8") as f:
                f.write(f"{record_line}\n")
            print(f"[Server][Warning] Blocked unauthorized connection. HWID saved to pending list.")