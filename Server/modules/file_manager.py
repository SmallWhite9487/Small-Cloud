import os
import hashlib
import json


class FileManager:
    def __init__(self, mods_dir=None):
        base_dir = os.environ.get("SMALLCLOUD_BASE_DIR", os.getcwd())
        default_mods_dir = os.path.join(base_dir, "uploads")
        self.mods_dir = os.path.abspath(mods_dir or os.environ.get("SMALLCLOUD_UPLOADS_DIR", default_mods_dir))
        os.makedirs(self.mods_dir, exist_ok=True)

    def calculate_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"[Server] Error calculating hash for {file_path}: {e}")
            return None

    def generate_manifest(self):
        manifest = {}
        
        if not os.path.exists(self.mods_dir):
            os.makedirs(self.mods_dir)
            print(f"[Server] Created missing mods directory at: {self.mods_dir}")
            return manifest

        print(f"[Server] Scanning mods directory: {self.mods_dir}...")
        
        for root, dirs, files in os.walk(self.mods_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.mods_dir).replace("\\", "/")
                
                file_hash = self.calculate_sha256(full_path)
                file_size = os.path.getsize(full_path)
                
                if file_hash:
                    manifest[rel_path] = {
                        "hash": file_hash,
                        "size": file_size
                    }
        
        print(f"[Server] Scan complete. Found {len(manifest)} file(s).")
        return manifest