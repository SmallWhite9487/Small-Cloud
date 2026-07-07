import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import sys
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from .i18n import I18n
from .server_sync import ServerSync
from .file_manager import ClientFileManager

GAME_PRESETS = {
    "game_def_7d2d": r"steamapps/common/7 Days To Die/Mods",
}

class SmallCloudGUI:
    def __init__(self, root):
        self.root = root
        self.i18n = I18n()
        self.root.title(self.i18n.t("app_title"))
        self.root.geometry("830x430")
        self.root.resizable(False, False)

        self.server_url = tk.StringVar(value="")
        self.mod_dir = tk.StringVar(value=os.path.abspath("mods"))
        self.max_workers_var = tk.IntVar(value=8) 
        
        self.speed_var = tk.StringVar(value=self.i18n.t("speed_label_placeholder"))
        self.size_var = tk.StringVar(value=self.i18n.t("size_label_placeholder"))
        self.language_button_text = tk.StringVar(value=self.i18n.get_language_name(self.i18n.get_next_language()))

        self.total_download_bytes = 0
        self.downloaded_bytes_this_second = 0
        self.total_need_bytes = 0
        self.lock = threading.Lock()

        self.user_choice_event = threading.Event()
        self.user_choice_result = False
        self.dialog_message = ""
        self.dialog_title = ""

        self.syncer = None
        self.file_mgr = None
        self.create_widgets()
        
        self.check_dialog_queue()

    def tr(self, key, **kwargs):
        return self.i18n.t(key, **kwargs)

    def create_widgets(self):
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        total_width = 830
        left_width = int(total_width * 3 / 5)
        right_width = int(total_width * 2 / 5)
        
        left_container = tk.Frame(self.root, width=left_width, height=430)
        left_container.grid(row=0, column=0, sticky="nsew")
        left_container.grid_propagate(False)

        right_container = tk.Frame(self.root, width=right_width, height=430)
        right_container.grid(row=0, column=1, sticky="nsew")
        right_container.grid_propagate(False)

        # =========================================================
        
        left_frame = tk.Frame(left_container, padx=15, pady=10)
        left_frame.pack(fill="both", expand=True)

        self.title_label = tk.Label(left_frame, text=self.tr("app_title_full"), font=("Microsoft YaHei", 14, "bold"))
        self.title_label.pack(pady=(5, 5), anchor="w")

        self.status_frame = tk.LabelFrame(left_frame, text=f" {self.tr('system_status')} ", padx=10, pady=5)
        self.status_frame.pack(fill="both", expand=True)

        self.status_text = tk.Text(self.status_frame, height=11, state="disabled", font=("Consolas", 9))
        self.status_text.pack(fill="both", expand=True)

        dashboard_infobar = tk.Frame(left_frame)
        dashboard_infobar.pack(fill="x", pady=(8, 2))
        
        speed_lbl = tk.Label(dashboard_infobar, textvariable=self.speed_var, font=("Microsoft YaHei", 9, "bold"), fg="#0078d4")
        speed_lbl.pack(side="left")
        
        size_lbl = tk.Label(dashboard_infobar, textvariable=self.size_var, font=("Microsoft YaHei", 9))
        size_lbl.pack(side="right")

        self.progress = ttk.Progressbar(left_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 10))

        bottom_btn_frame = tk.Frame(left_frame)
        bottom_btn_frame.pack(fill="x", pady=(0, 5))

        self.sync_button = tk.Button(
            bottom_btn_frame, text=self.tr("start_sync"), font=("Microsoft YaHei", 10, "bold"), 
            bg="#0078d4", fg="white", relief="flat", command=self.confirm_start_sync
        )
        self.sync_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.lang_button = tk.Button(
            bottom_btn_frame, textvariable=self.language_button_text, font=("Microsoft YaHei", 9),
            bg="#f3f3f3", fg="#333333", relief="flat", command=self.switch_language, padx=10
        )
        self.lang_button.pack(side="right")

        # =========================================================

        self.right_frame = tk.LabelFrame(right_container, text=f" {self.tr('dashboard_settings')} ", padx=15, pady=15)
        self.right_frame.pack(fill="both", expand=True, padx=(5, 15), pady=15)

        self.lbl_server = tk.Label(self.right_frame, text=self.tr("server_domain"), font=("Microsoft YaHei", 9, "bold"))
        self.lbl_server.pack(anchor="w", pady=(0, 2))
        server_entry = tk.Entry(self.right_frame, textvariable=self.server_url, font=("Segoe UI", 10))
        server_entry.pack(fill="x", pady=(0, 8))

        self.lbl_preset = tk.Label(self.right_frame, text=self.tr("game_preset"), font=("Microsoft YaHei", 9, "bold"))
        self.lbl_preset.pack(anchor="w", pady=(0, 2))
        
        preset_display_values = [self.tr(k) for k in GAME_PRESETS.keys()]
        self.preset_combo = ttk.Combobox(self.right_frame, values=preset_display_values, state="readonly", font=("Microsoft YaHei", 9))
        self.preset_combo.pack(fill="x", pady=(0, 8))
        self.preset_combo.bind("<<ComboboxSelected>>", self.apply_game_preset)

        self.lbl_dir = tk.Label(self.right_frame, text=self.tr("mod_dir"), font=("Microsoft YaHei", 9, "bold"))
        self.lbl_dir.pack(anchor="w", pady=(0, 2))
        path_select_frame = tk.Frame(self.right_frame)
        path_select_frame.pack(fill="x")
        
        dir_entry = tk.Entry(path_select_frame, textvariable=self.mod_dir, font=("Segoe UI", 9))
        dir_entry.pack(fill="x", pady=(0, 5))
        
        self.btn_action_frame = tk.Frame(self.right_frame)
        self.btn_action_frame.pack(fill="x", pady=(5, 0))
        
        self.browse_btn = tk.Button(self.btn_action_frame, text=f" {self.tr('browse')}... ", font=("Microsoft YaHei", 8), command=self.browse_local_directory)
        self.browse_btn.pack(fill="x", pady=(0, 5))
        
        self.lbl_workers = tk.Label(self.right_frame, text=self.tr("max_workers"), font=("Microsoft YaHei", 9, "bold"))
        self.lbl_workers.pack(anchor="w", pady=(0, 2))
        
        self.workers_slider = tk.Scale(
            self.right_frame, 
            from_=1, to=32, orient=tk.HORIZONTAL,
            variable=self.max_workers_var, resolution=1,
            tickinterval=0, showvalue=True,
            troughcolor="#e1e1e1", activebackground="#0078d4",
            relief="flat", bd=0
        )
        self.workers_slider.pack(fill="x", pady=(0, 4))
        
        self.lbl_note = tk.Label(self.right_frame, text=self.tr("concurrency_note"), font=("Microsoft YaHei", 8), fg="#666666")
        self.lbl_note.pack(anchor="w", pady=(0, 8))

    def switch_language(self):
        next_lang = self.i18n.get_next_language()
        self.i18n.set_language(next_lang)
        
        self.root.title(self.tr("app_title"))
        self.title_label.config(text=self.tr("app_title_full"))
        self.status_frame.config(text=f" {self.tr('system_status')} ")
        self.right_frame.config(text=f" {self.tr('dashboard_settings')} ")
        self.lbl_server.config(text=self.tr("server_domain"))
        self.lbl_preset.config(text=self.tr("game_preset"))
        self.lbl_workers.config(text=self.tr("max_workers"))
        self.lbl_note.config(text=self.tr("concurrency_note"))
        self.lbl_dir.config(text=self.tr("mod_dir"))
        self.browse_btn.config(text=f" {self.tr('browse')}... ")
        self.sync_button.config(text=self.tr("start_sync") if self.sync_button["state"] == "normal" else self.tr("syncing"))
        self.speed_var.set(self.tr("speed_label_placeholder"))
        self.size_var.set(self.tr("size_label_placeholder"))
        
        preset_display_values = [self.tr(k) for k in GAME_PRESETS.keys()]
        self.preset_combo.config(values=preset_display_values)
        self.preset_combo.set('')
        
        self.language_button_text.set(self.i18n.get_language_name(self.i18n.get_next_language()))
        self.log(self.tr('language_switched', language=self.i18n.get_language_name(next_lang)))

    def log(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def format_size(self, bytes_value):
        for unit in ['Bytes', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} TB"

    def browse_local_directory(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.mod_dir.set(os.path.abspath(selected_directory))
            self.confirm_current_directory()

    def confirm_current_directory(self):
        current_path = self.mod_dir.get().strip()
        if not current_path:
            messagebox.showerror(self.tr("app_title"), self.tr("error_dir_empty"))
            return
        is_yes = messagebox.askyesno(
            self.tr("confirm_dir_title"), 
            self.tr("confirm_dir_message", path=current_path)
        )
        if is_yes:
            self.log(f"[Client] {self.tr('dir_confirmed', path=current_path)}")
        else:
            self.log(f"[Client] {self.tr('dir_cancelled')}")

    def get_steam_install_path(self):
        if sys.platform != "win32": return None
        import winreg
        for subkey in [r"SOFTWARE\Valve\Steam", r"SOFTWARE\Wow6432Node\Valve\Steam"]:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_READ)
                path, _ = winreg.QueryValueEx(key, "SteamPath")
                winreg.CloseKey(key)
                return os.path.abspath(path)
            except Exception: continue
        return None

    def get_all_steam_library_folders(self):
        libraries = []
        steam_base = self.get_steam_install_path()
        if not steam_base: return libraries
        libraries.append(steam_base)
        vdf_path = os.path.join(steam_base, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            try:
                with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f: content = f.read()
                found_paths = re.findall(r'"path"\s+"([^"]+)"', content)
                for p in found_paths:
                    clean_path = p.replace("\\\\", "\\")
                    if os.path.exists(clean_path) and clean_path not in libraries:
                        libraries.append(os.path.abspath(clean_path))
            except Exception: pass
        return libraries

    def apply_game_preset(self, event):
        selected_translated = self.preset_combo.get()
        selected_game_key = None
        for k in GAME_PRESETS.keys():
            if self.tr(k) == selected_translated:
                selected_game_key = k
                break
                
        if not selected_game_key: return
        rel_preset_path = GAME_PRESETS[selected_game_key]

        if not messagebox.askyesno(self.tr("preset_confirm_title"), self.tr("preset_confirm_message", game=selected_translated)):
            self.preset_combo.set('')
            return

        if "AppData" in rel_preset_path:
            user_home = os.environ.get("USERPROFILE", "C:\\Users\\Default")
            final_path = os.path.abspath(os.path.join(user_home, rel_preset_path))
            self.mod_dir.set(final_path)
            self.log(f"[Preset] {self.tr('preset_match_success', path=final_path)}")
            return

        self.log(f"[Preset] {self.tr('preset_scanning', game=selected_translated)}")
        libraries = self.get_all_steam_library_folders()
        matched_path = None
        for lib in libraries:
            full_check = os.path.join(lib, rel_preset_path)
            if os.path.exists(full_check):
                matched_path = os.path.abspath(full_check)
                break

        if matched_path:
            self.mod_dir.set(matched_path)
            self.log(f"[Preset] {self.tr('preset_match_success', path=matched_path)}")
        else:
            self.log(f"[Warning] {self.tr('preset_not_found')}")
            messagebox.showwarning(self.tr("preset_not_found_title"), self.tr("preset_not_found_message"))

    def confirm_start_sync(self):
        current_url = self.server_url.get().strip()
        current_dir = self.mod_dir.get().strip()
        
        if not current_url or not current_dir:
            messagebox.showerror(self.tr("app_title"), self.tr("error_dir_empty"))
            return

        workers = self.max_workers_var.get()
        is_yes = messagebox.askyesno(
            self.tr("sync_begin_title"),
            self.tr("sync_begin_message", url=current_url, dir=current_dir, workers=workers)
        )
        if is_yes:
            self.start_sync_thread()
        else:
            self.log(f"[Client] {self.tr('sync_cancelled')}")

    def start_sync_thread(self):
        self.sync_button.config(state="disabled", text=self.tr("syncing"), bg="#cccccc")
        self.progress["value"] = 0
        self.speed_var.set(self.tr("speed_label_placeholder"))
        self.size_var.set(self.tr("size_label_placeholder"))
        
        self.total_download_bytes = 0
        self.downloaded_bytes_this_second = 0
        self.total_need_bytes = 0

        self.syncer = ServerSync(base_url=self.server_url.get().strip())
        self.file_mgr = ClientFileManager(local_dir=self.mod_dir.get().strip(), i18n=self.i18n)

        worker = threading.Thread(target=self.sync_worker_logic, daemon=True)
        worker.start()

    def request_user_confirmation_from_thread(self, title, message):
        self.dialog_title = title
        self.dialog_message = message
        self.user_choice_event.clear()
        self.user_choice_event.wait()
        return self.user_choice_result

    def check_dialog_queue(self):
        if self.dialog_message:
            res = messagebox.askyesno(self.dialog_title, self.dialog_message)
            self.user_choice_result = res
            self.dialog_message = ""
            self.dialog_title = ""
            self.user_choice_event.set()
        self.root.after(100, self.check_dialog_queue)

    def chunk_received_callback(self, chunk_len):
        with self.lock:
            self.total_download_bytes += chunk_len
            self.downloaded_bytes_this_second += chunk_len

    def update_speed_loop(self, stop_event):
        while not stop_event.is_set():
            time.sleep(1.0)
            with self.lock:
                current_speed_bytes = self.downloaded_bytes_this_second
                self.downloaded_bytes_this_second = 0
            
            speed_mb = current_speed_bytes / (1024 * 1024)
            self.speed_var.set(self.tr("speed_label_format", speed=f"{speed_mb:.2f} MB/s"))
            
            done_str = self.format_size(self.total_download_bytes)
            total_str = self.format_size(self.total_need_bytes)
            self.size_var.set(self.tr("size_label_progress", done=done_str, total=total_str))
            
            if self.total_need_bytes > 0:
                self.progress["value"] = (self.total_download_bytes / self.total_need_bytes) * 100

    def sync_worker_logic(self):
        stop_speed_thread = threading.Event()
        speed_thread = threading.Thread(target=self.update_speed_loop, args=(stop_speed_thread,), daemon=True)
        
        try:
            self.log("[Client] Connection testing...")
            if not self.syncer.check_connection():
                self.log("[Error] Server connection failed.")
                self.reset_button()
                return

            self.log("[Client] HWID Authenticating...")
            hwid = self.syncer.send_hwid()
            if not hwid:
                self.log("[Error] Authentication failed.")
                self.reset_button()
                return

            manifest = self.syncer.get_manifest(hwid)
            if manifest is None:
                self.log("[Error] Manifest pull failed.")
                self.reset_button()
                return

            self.log(f"[Client] {self.tr('file_manager_checking_consistency')}")
            
            local_files = []
            if os.path.exists(self.file_mgr.local_dir):
                for root_dir, _, filenames in os.walk(self.file_mgr.local_dir):
                    for f in filenames:
                        fp = os.path.join(root_dir, f)
                        rel = os.path.relpath(fp, self.file_mgr.local_dir).replace("\\", "/")
                        if rel not in manifest:
                            local_files.append(rel)

            if local_files:
                file_list_str = "\n".join(local_files[:5]) + ("\n..." if len(local_files) > 5 else "")
                msg = self.tr("cleanup_confirm_message", count=len(local_files)) + f"\n\n{file_list_str}"
                
                confirm_delete = self.request_user_confirmation_from_thread(self.tr("cleanup_confirm_title"), msg)
                if not confirm_delete:
                    self.log(f"[Client] {self.tr('cleanup_cancelled')}")
                    self.reset_button()
                    return

            download_queue = self.file_mgr.compare_with_server(manifest, log_callback=self.log)

            if not download_queue:
                self.log(f"\n[🎉] {self.tr('sync_no_updates')}")
                self.speed_var.set(self.tr("speed_label_placeholder"))
                self.size_var.set(self.tr("size_label_aligned"))
                self.progress["value"] = 100
                self.reset_button(text=self.tr("latest_status"))
                return

            for f_path in download_queue:
                self.total_need_bytes += manifest[f_path]["size"]

            user_workers = self.max_workers_var.get()
            download_msg = self.tr("download_confirm_message", count=len(download_queue), size=self.format_size(self.total_need_bytes), workers=user_workers)
            confirm_download = self.request_user_confirmation_from_thread(self.tr("download_confirm_title"), download_msg)
            
            if not confirm_download:
                self.log(f"[Client] {self.tr('download_cancelled')}")
                self.reset_button()
                return

            self.log(f"\n[Client] {self.tr('download_started', workers=user_workers)}")
            speed_thread.start()

            success_count = 0
            with ThreadPoolExecutor(max_workers=user_workers) as executor:
                futures = {
                    executor.submit(
                        self.syncer.download_file, hwid, file, self.file_mgr.local_dir, self.chunk_received_callback
                    ): file for file in download_queue
                }
                for future in as_completed(futures):
                    file_name = futures[future]
                    if future.result():
                        success_count += 1
                        self.log(self.tr("download_success", file=file_name))
                    else:
                        self.log(self.tr("download_error", file=file_name))

            self.progress["value"] = 100
            self.size_var.set(self.tr("size_label_progress", done=self.format_size(self.total_need_bytes), total=self.format_size(self.total_need_bytes)))
            self.log(f"\n[Client] {self.tr('sync_finished', success=success_count, total=len(download_queue))}")
            messagebox.showinfo(self.tr("app_title"), self.tr("sync_success_info"))
            
        except Exception as e:
            self.log(f"\n{self.tr('fatal_error', error=e)}")
        finally:
            stop_speed_thread.set()
            self.speed_var.set(self.tr("speed_label_placeholder"))
            self.reset_button()

    def reset_button(self, text=None):
        if text is None:
            text = self.tr("start_sync")
        self.sync_button.config(state="normal", text=text, bg="#0078d4")