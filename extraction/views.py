import json
import os 

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
        # rellenemos de acuerdo a las valriables de json 
        'pdf_folder': config.get('pdf_folder'),             #A
        'pdf_input': config.get('pdf_input'),               #B
        'output_map_path': config.get('output_map_path'),   #C
        'map_pdf_folder': config.get('map_pdf_folder'),     #D
        'map_file': config.get('map_file'),                 #E
        'mass_pdf_folder': config.get('mass_pdf_folder'),   #E
        'excel_folder': config.get('excel_folder'),         #F
        'sensitivity': config.get('sensitivity'),
 
    })


def update_config(request):
    if request.method == 'POST':
        print("DEBUG: Entró en update_config")
        try:
            data = json.loads(request.body)
            # Guardamos la clave y valor recibidos
            PersistenceManager.save_paths(**{data['key']: data['value']})
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)




def execute_path(request):
   
    if request.method == 'POST':    
       # mostramos las variables recibidas enviadsa en consosla
       data = json.loads(request.body)
       print("Datos recibidos:", data)
       if data.get('action') == 'screening':
           print("Ejecutando la ruta de screening")
           
       elif data.get('action') == 'mapping':
            try:
                extractor = MapExtractor(data['pdf_input'])
                extractor.file_path = data.get('pdf_input')
                extractor.output_map_dir = data.get('map_out')
                print("Ejecutando la ruta de mapping")
                extractor.extract_layout().save_template("mapa_resultado.csv")
            except Exception as e:
                print(f"Error al procesar la ruta de mapeo: {e}")
                print(f"{data}")   
       return JsonResponse({'status': 'success', 'message': 'Ruta procesada correctamente'})
    return JsonResponse({'status': 'error', 'message': 'Solo se permiten peticiones POST'}, status=400) 
#### Edición de de CSV de MAPEO #####
def get_template_data(request):
    # Esto busca el CSV que generó el MapExtractor en Tab 1
    # Asegúrate de usar la misma ruta que guardaste en tu PersistenceManager
    config = PersistenceManager.load_paths()
    path = os.path.join(config.get('output_map_path'), "mapa_resultado.csv")
    
    if not os.path.exists(path):
        return JsonResponse({'error': 'No existe plantilla, ejecuta Tab 1 primero'}, status=404)
        
    df = pd.read_csv(path)
    return JsonResponse(df.fillna('').to_dict(orient='records'), safe=False)

def save_template_config(request):
    data = json.loads(request.body)
    config = PersistenceManager.load_paths()
    path = os.path.join(config.get('output_map_path'), "mapa_resultado.csv")
    
    df = pd.read_csv(path)
    
    # Actualizamos el DataFrame con los cambios recibidos
    for update in data['updates']:
        idx = int(update['index'])
        df.at[idx, 'header_label'] = update['header_label']
    
    df.to_csv(path, index=False)
    return JsonResponse({'status': 'ok'})