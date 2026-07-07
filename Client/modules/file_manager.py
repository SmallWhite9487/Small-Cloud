import os
import hashlib


class ClientFileManager:
    def __init__(self, local_dir="mods", i18n=None):
        self.local_dir = os.path.abspath(local_dir)
        self.i18n = i18n

    def _tr(self, key, **kwargs):
        if not self.i18n:
            return key
        text = self.i18n.t(key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    def calculate_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None

    def compare_with_server(self, server_manifest, log_callback=None):
        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)

        def print_log(msg):
            if log_callback:
                log_callback(msg)
            print(msg)

        tasks_to_download = []
        print_log(f"[Client] {self._tr('file_manager_checking_consistency')}")

        for rel_path, info in server_manifest.items():
            local_path = os.path.join(self.local_dir, rel_path)

            if not os.path.exists(local_path):
                print_log(self._tr("file_manager_missing", path=rel_path))
                tasks_to_download.append(rel_path)
                continue

            local_hash = self.calculate_sha256(local_path)
            if local_hash != info["hash"]:
                print_log(self._tr("file_manager_outdated", path=rel_path))
                tasks_to_download.append(rel_path)

        print_log(f"[Client] {self._tr('file_manager_checking_extras')}")
        deleted_count = 0

        for root, dirs, files in os.walk(self.local_dir, topdown=False):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.local_dir).replace("\\", "/")

                if rel_path not in server_manifest:
                    try:
                        os.remove(full_path)
                        print_log(self._tr("file_manager_cleanup_success", path=rel_path))
                        deleted_count += 1
                    except Exception as e:
                        print_log(self._tr("file_manager_cleanup_failed", path=rel_path, error=e))

            for d in dirs:
                dir_path = os.path.join(root, d)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except Exception:
                    pass

        if deleted_count > 0:
            print_log(f"[Client] {self._tr('file_manager_cleanup_complete', count=deleted_count)}")
        else:
            print_log(self._tr("file_manager_cleanup_verified"))

        print_log(f"[Client] {self._tr('file_manager_compare_complete', count=len(tasks_to_download))}")
        return tasks_to_download