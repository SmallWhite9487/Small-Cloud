import json
import locale
import os
import sys
from pathlib import Path

try:
    import ctypes
except ImportError:
    ctypes = None


class I18n:
    def __init__(self, language=None, base_dir=None):
        self.base_dir = Path(base_dir or Path(__file__).resolve().parent)
        self.available_languages = {
            "zh_cn": "简体中文",
            "zh_tw": "繁體中文",
            "en": "English",
        }
        self.default_language = "en"
        self.current_language = self._normalize_language(language or self.detect_system_language())
        self.translations = self._load_all_translations()

    def _normalize_language(self, language):
        if not language:
            return self.default_language

        code = str(language).strip().lower().replace("-", "_")
        if code.startswith("zh"):
            if code in {"zh_tw", "zh_hk", "zh_mo", "zh_hant", "zh_hant_hk", "zh_hant_mo"}:
                return "zh_tw"
            return "zh_cn"

        if code in self.available_languages:
            return code

        return self.default_language

    def _parse_locale_to_language(self, candidate):
        if candidate is None:
            return None

        if isinstance(candidate, int):
            if candidate in {1033}:
                return "en"
            if candidate in {2052, 3076, 1028, 1029}:
                return "zh_cn" if candidate in {2052, 1029} else "zh_tw"
            return None

        code = str(candidate).strip().lower().replace("-", "_")
        code = code.replace(".", "_").replace("@", "_")
        base = code.split("_")[0]

        if base.startswith("zh"):
            if any(token in code for token in ("tw", "hk", "mo", "hant")):
                return "zh_tw"
            return "zh_cn"

        if base.startswith("en"):
            return "en"

        return None

    def detect_system_language(self):
        candidates = []

        default_locale = locale.getdefaultlocale()[0]
        if default_locale:
            candidates.append(default_locale)

        if os.name == "nt" and ctypes is not None:
            try:
                win_lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
                if win_lang_id:
                    candidates.append(win_lang_id)
            except Exception:
                pass

        for env_name in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
            value = os.environ.get(env_name)
            if value:
                candidates.append(value)

        for candidate in candidates:
            normalized = self._parse_locale_to_language(candidate)
            if normalized:
                return normalized

        return self.default_language

    def _load_all_translations(self):
        loaded = {}
        file_candidates = {
            "zh_cn": ["l_simplified_chinese.json"],
            "zh_tw": ["l_traditional_chinese.json"],
            "en": ["l_english.json"],
        }

        lang_dirs = []
        for base in [self.base_dir.parent, self.base_dir.parent.parent, Path(getattr(sys, "_MEIPASS", "")) if hasattr(sys, "_MEIPASS") else None]:
            if base:
                lang_dirs.append(base / "lang")
                lang_dirs.append(base)

        lang_dirs.extend([
            Path(__file__).resolve().parent.parent / "lang",
            Path(__file__).resolve().parent.parent,
            Path(sys.executable).resolve().parent / "lang" if getattr(sys, "frozen", False) else None,
            Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else None,
        ])

        lang_dir = None
        for candidate in lang_dirs:
            if candidate and candidate.exists():
                lang_dir = candidate
                break

        if lang_dir is None:
            lang_dir = self.base_dir.parent / "lang"

        for code in self.available_languages:
            resolved = {}
            for filename in file_candidates.get(code, []):
                file_path = lang_dir / filename
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as handle:
                        resolved = json.load(handle)
                    break
            loaded[code] = resolved
        return loaded

    def set_language(self, language):
        self.current_language = self._normalize_language(language)
        return self.current_language

    def get_next_language(self):
        order = ["zh_cn", "zh_tw", "en"]
        if self.current_language not in order:
            return order[0]
        current_index = order.index(self.current_language)
        return order[(current_index + 1) % len(order)]

    def get_switch_button_text(self):
        next_lang = self.get_next_language()
        return self.get_language_name(next_lang)

    def get_language_name(self, language=None):
        code = self._normalize_language(language or self.current_language)
        return self.available_languages.get(code, code)

    def t(self, key, default=None, **kwargs):
        text = None
        if key in self.translations.get(self.current_language, {}):
            text = self.translations[self.current_language][key]
        elif key in self.translations.get(self.default_language, {}):
            text = self.translations[self.default_language][key]
        elif default is not None:
            text = default
        else:
            text = key

        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text
