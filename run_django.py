import os
import sys
from waitress import serve
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

def run():
    # 1. Configurar el entorno de Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    application = get_wsgi_application()

    # 2. Configurar la ruta de estáticos para el ejecutable
    if getattr(sys, 'frozen', False):
        # Cuando se empaqueta con PyInstaller
        static_dir = os.path.join(sys._MEIPASS, 'static')
    else:
        # En desarrollo local
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    # 3. Aplicar WhiteNoise
    application = WhiteNoise(application, root=static_dir)

    # 4. Servir la aplicación
    print(f"Servidor iniciado. Sirviendo estáticos desde: {static_dir}")
    serve(application, host='127.0.0.1', port=8000)

if __name__ == "__main__":
    run()