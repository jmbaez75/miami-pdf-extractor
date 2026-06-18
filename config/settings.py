import sys, os
from pathlib import Path

# --- CONFIGURACIÓN DE RUTAS ---
# Usamos Path() en ambos casos para que el operador / funcione siempre
if getattr(sys, 'frozen', False):
    # En el ejecutable (PyInstaller)
    BASE_DIR = Path(sys._MEIPASS)
    STATIC_ROOT = BASE_DIR / 'static'
else:
    # En desarrollo
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_ROOT = BASE_DIR / 'staticfiles'

print(f"--- CARGANDO SETTINGS.PY | BASE_DIR: {BASE_DIR} ---")

# --- CONFIGURACIÓN DE ESTÁTICOS ---
STATIC_URL = '/static/'

if not getattr(sys, 'frozen', False):
    STATICFILES_DIRS = [BASE_DIR / 'static']
else:
    STATICFILES_DIRS = []

# Quick-start development settings
SECRET_KEY = 'django-insecure-e65ntv89-qr8r$u19$m@6oxkq*m8$7#vxf(+mz(zqy8vwqef_a'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'extraction',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
USER_DATA_DIR = Path(os.path.expanduser("~/.fburo"))
if not USER_DATA_DIR.exists():
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': USER_DATA_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True