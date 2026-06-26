import os
import sys
import socket
import subprocess
import threading
import time
import shutil
from waitress import serve
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

def is_port_in_use(port):
    """Checks if the port is currently being used by any process."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def wait_for_server(port, timeout=15):
    """Actively waits for the server to respond on the specified port."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.5)
    return False

def run():
    port = 8000
    
    # 1. Clean up previous processes if the port is occupied
    if is_port_in_use(port):
        # We attempt to close the previous instance cleanly using fuser
        os.system(f"fuser -k {port}/tcp")
        time.sleep(1) # Small pause to ensure the socket is released

    # 2. Django Configuration
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    application = get_wsgi_application()
    
    # Static files location (support for AppImage or standard execution)
    if getattr(sys, 'frozen', False):
        static_dir = os.path.join(sys._MEIPASS, 'staticfiles')
    else:
        static_dir = os.path.join(os.path.dirname(__file__), 'staticfiles')
    
    application = WhiteNoise(application, root=static_dir, prefix='static/')
    
    # 3. Start the server in a secondary thread (daemon=True to exit if script dies)
    server_thread = threading.Thread(target=lambda: serve(application, host='127.0.0.1', port=port), daemon=True)
    server_thread.start()

    # 4. Wait for the server to be alive and launch the browser
    if wait_for_server(port):
        if shutil.which("xdg-open"):
            # Popen allows the browser to run independently
            subprocess.Popen(['xdg-open', f'http://127.0.0.1:{port}/fburo'])
    else:
        print("Error: The server did not respond on port 8000 within the time limit.")
        sys.exit(1)

    # 5. Keep the main thread alive while the server runs in the background
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    run()