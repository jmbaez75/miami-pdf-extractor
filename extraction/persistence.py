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
        # Mantenemos la creación de la carpeta del JSON por seguridad, 
        # pero nada más.
        cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = cls.load_paths()
        data.update(paths)
        
        with open(cls.CONFIG_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def ensure_configuration(cls):
        # Esta función ahora es solo un "Lector y Validador"
        data = cls.load_paths()
        check_paths = ["mass_pdf_folder", "output_map_path", "excel_folder"]
        
        for key in check_paths:
            path_val = data.get(key)
            
            # Solo verificamos. Si no existe, lanzamos error.
            # Nada de input(), nada de bucles, nada de mkdir().
            if not path_val or not os.path.isdir(path_val):
                raise FileNotFoundError(f"Error de configuración: La ruta para '{key}' no existe o es inválida: {path_val}")
        
        return data