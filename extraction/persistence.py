import json
import os
from pathlib import Path
from django.conf import settings

class PersistenceManager:
    CONFIG_FILE = Path(settings.BASE_DIR) / "config" / "app_config.json"

    @classmethod
    def load_paths(cls):
        if not cls.CONFIG_FILE.exists():
            return cls._get_default_structure()
        
        try:
            with open(cls.CONFIG_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                default = cls._get_default_structure()
                default.update(data)
                return default
        except (json.JSONDecodeError, IOError):
            return cls._get_default_structure()

    @classmethod
    def _get_default_structure(cls):
        return {
            "last_map_route_pdf": None,
            "input_mass_folder": None,
            "output_map_path": None,
            "output_excel_path": None
        }

    @classmethod
    def save_paths(cls, **paths):
        cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = cls.load_paths()
        data.update(paths)
        
        with open(cls.CONFIG_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def ensure_configuration(cls):
        data = cls.load_paths()
        check_paths = ["input_mass_folder", "output_map_path", "output_excel_path"]
        
        updated = False
        for key in check_paths:
            path_val = data.get(key)
            
            if not path_val or not os.path.isdir(path_val):
                print(f"\nConfiguration required for: {key.replace('_', ' ')}")
                valid = False
                while not valid:
                    user_input = input("Enter a valid directory path: ").strip()
                    if os.path.isdir(user_input):
                        data[key] = user_input
                        valid = True
                        updated = True
                    else:
                        print("Invalid directory. Please try again.")
        
        if updated:
            cls.save_paths(**data)
        
        return data