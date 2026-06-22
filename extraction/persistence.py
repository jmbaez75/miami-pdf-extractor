
import os
from pathlib import Path
from django.conf import settings
import subprocess
import json
class PersistenceManager:
    # la appimage precisara una carpeta que el usuario debe crear en la misma carpeta llamada "config"
    APPIMAGE_ROUTE = os.environ.get("APPIMAGE")
    APPIMAGE_CONFIG_FOLDER= Path(APPIMAGE_ROUTE).parent / "config" if APPIMAGE_ROUTE else None
    APPIMAGE_CONFIG_FILE = APPIMAGE_CONFIG_FOLDER / "app_config.json" if APPIMAGE_CONFIG_FOLDER else None
    CONFIG_FILE = Path(settings.BASE_DIR) / "config" / "app_config.json"

    @classmethod
    def load_paths(cls):
        
        # si NO detectamos si existe APPIMAGE_CONFIG_FOLDER
        if not cls.APPIMAGE_CONFIG_FOLDER or not os.path.exists(cls.APPIMAGE_CONFIG_FOLDER):
            subprocess.run(['notify-send', 'FBuro', 'important:For persistence, create a "config" folder next to the appimage.'])

            # si no existe ni carpeta ni archivo al lado de la appimage , cargamos las variables de CONFIG FILE
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
        
        elif os.path.exists(cls.APPIMAGE_CONFIG_FILE):
            try:
                with open(cls.APPIMAGE_CONFIG_FILE, "r", encoding='utf-8') as f:
                    data = json.load(f)
                default = cls._get_default_structure()
                default.update(data)
                return default
            except (json.JSONDecodeError, IOError):
                return cls._get_default_structure()
        else:
            # la carpeta existe pero el archivo no esta dentro -> cargamos CONFIG_FILE
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
            "pdf_folder": None,
            "pdf_input": None,
            "map_file_folder": None,
            "map_file": None,
            "mass_pdf_folder": None,
            "excel_folder": None,
            "sensitivity": None,
        }
    
    
    
    
    @classmethod
    def save_paths(cls, **paths):
        # Determinamos si esta la carpeta config al lado de la Appimage
        if not cls.APPIMAGE_CONFIG_FOLDER or not os.path.exists(cls.APPIMAGE_CONFIG_FOLDER):
            subprocess.run(['notify-send', 'FBuro', 'important:For persistence, create a "config" folder next to the appimage.'])
            # grabamos en el interno de la app
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = cls.load_paths()
            data.update(paths)
            with open(cls.CONFIG_FILE, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        # si existe gravamos las en en APPIMAGE_CONFIG_FILE:
        else:
            data = cls.load_paths()
            data.update(paths)
            with open(cls.APPIMAGE_CONFIG_FILE, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)
    @classmethod
    def ensure_configuration(cls):
        # Esta función ahora es solo un "Lector y Validador"
        data = cls.load_paths()
        check_paths = ["mass_pdf_folder", "map_file_folder", "excel_folder"]
        for key in check_paths:
            path_val = data.get(key)

            # Solo verificamos. Si no existe, lanzamos error.
            # Nada de input(), nada de bucles, nada de mkdir().
            if not path_val or not os.path.isdir(path_val):
                raise FileNotFoundError(f"Error de configuración: La ruta para '{key}' no existe o es inválida: {path_val}")
        
        return data
