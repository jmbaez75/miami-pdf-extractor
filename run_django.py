import os
import sys
import subprocess
from waitress import serve
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
def run():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    application = get_wsgi_application()
    # Apuntamos a 'staticfiles' (donde los pone collectstatic)
    if getattr(sys, 'frozen', False):
        static_dir = os.path.join(sys._MEIPASS, 'staticfiles')
    else:
        static_dir = os.path.join(os.path.dirname(__file__), 'staticfiles')
    
    # El prefix es OBLIGATORIO para que el navegador encuentre /static/...
    
    application = WhiteNoise(application, root=static_dir, prefix='static/')
    
    print(f"Servidor iniciado. Sirviendo estáticos desde: {static_dir}")

    try:
        subprocess.run(['notify-send', 'FBuro', 'Miami Data Extractor is running. Open http://127.0.0.1:8000/fburo in your browser.'])
    except FileNotFoundError:
        pass
    serve(application, host='127.0.0.1', port=8000)

if __name__ == "__main__":
    run()