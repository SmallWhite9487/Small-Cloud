import subprocess
import platform
import hashlib
import uuid
import os

class HWIDManager:
    def __init__(self):
        pass

    def get_system_uuid(self):
        system = platform.system()
        try:
            if system == "Windows":
                cmd = 'reg query "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid'
                result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
                parts = result.decode('utf-8', errors='ignore').strip().split()
                if len(parts) >= 3:
                    return parts[-1]
                return "WIN-FALLBACK-UUID"
                
            elif system == "Linux":
                if os.path.exists("/sys/class/dmi/id/product_uuid"):
                    with open("/sys/class/dmi/id/product_uuid", "r") as f:
                        return f.read().strip()
                return "LINUX-FALLBACK-UUID"
                
            elif system == "Darwin":
                command = "ioreg -rd1 -c IOPlatformExpertDevice | awk -F'\"' '/IOPlatformUUID/{print $4}'"
                result = subprocess.check_output(command, shell=True)
                return result.decode().strip()
        except Exception:
            return "GLOBAL-FALLBACK-UUID"

    def get_hwid(self):
        sys_uuid = self.get_system_uuid()
        mac_node = uuid.getnode()
        
        # 组合特征桩
        base_id = f"{sys_uuid}-{mac_node}"

        return hashlib.sha256(base_id.encode('utf-8')).hexdigest()