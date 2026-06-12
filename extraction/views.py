import json
from django.http import JsonResponse
from django.shortcuts import render
from .persistence import PersistenceManager # Importa tu clase

def show_interface(request):
    # Carga los datos actuales para mostrarlos en el HTML
    context = PersistenceManager.load_paths()
    return render(request, 'extraction/interface.html', context)

def update_config(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Guardamos la clave y valor recibidos
            PersistenceManager.save_paths(**{data['key']: data['value']})
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)