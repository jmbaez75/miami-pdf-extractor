import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.http import JsonResponse
from django.shortcuts import render
from .persistence import PersistenceManager # Importa tu clase
from django.views.decorators.csrf import ensure_csrf_cookie

from extraction.processor import MapExtractor # Importa tu clase

@ensure_csrf_cookie
def show_interface(request):
    # Cargamos las rutas desde tu archivo JSON
    config = PersistenceManager.load_paths()
    
    # Enviamos los datos al template
    return render(request, 'extraction/interface.html', {
        'last_map_route_pdf': config.get('last_map_route_pdf'),
        'input_mass_folder': config.get('input_mass_folder'),
        'output_map_path': config.get('output_map_path'),
        'output_excel_path': config.get('output_excel_path')
    })


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

    return JsonResponse({'status': 'error'}, status=405)


def execute_path(request):
   
    print("Ejecutando la ruta")
    if request.method == 'POST':
       
       # mostramos las variables recibidas enviadsa en consosla
       data = json.loads(request.body)
       print("Datos recibidos:", data)
       if data.get('action') == 'screening':
           print("Ejecutando la ruta de screening")
       elif data.get('action') == 'mapping':
           try:
            extractor = MapExtractor(pdf_path=data['pdf_input'])
            print("Ejecutando la ruta de mapping")
            extractor.extract_layout().save_template("mapa_resultado.csv")
           except Exception as e:
            print(f"Error al procesar la ruta de mapeo: {e}")   
       return JsonResponse({'status': 'success', 'message': 'Ruta procesada correctamente'})
    return JsonResponse({'status': 'error', 'message': 'Solo se permiten peticiones POST'}, status=400) 
