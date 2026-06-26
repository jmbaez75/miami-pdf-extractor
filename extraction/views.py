import json
import os 
import pandas as pd
import threading

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.http import JsonResponse
from django.shortcuts import render
from .persistence import PersistenceManager 
from django.views.decorators.csrf import ensure_csrf_cookie

from extraction.processor import MapExtractor
from extraction.processor import MapMassReader

BATCH_PROGRESS = {'status': 'idle', 'current': 0, 'total': 0, 'result': None, 'message': ''}
BATCH_LOCK = threading.Lock()


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
        'map_file_folder': config.get('map_file_folder'),   #D
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
    print(f"datos recibidos")
    if request.method == 'POST':    
       # mostramos las variables recibidas enviadsa en consosla
       data = json.loads(request.body)
       print("Datos recibidos:", data)
       
       if data.get('action') == 'screening':
            try:
                reader = MapMassReader()
                # cargamos la variables en el reader
                reader.sensitivity = float(data.get('sensitivity')) if data.get('sensitivity') else data.get('sensitivity')
                reader.excel_folder = data.get('excel_folder')
                reader.mass_pdf_folder = data.get('mass_pdf_folder')
                reader.map_path = data.get('map_file_folder')+ data.get('map_file')
                reader.check_rutes() 
                
                # this line executes the batch job
                # but is commented because it is executed in a separate thread                                
                # excel_path = reader.run_batch()
                # it is replaced by threading.Thread(target=_run_batch_job, args=(reader,), daemon=True).start()

                # Actualizamos el estado del lote. si esta en progresoquit
                with BATCH_LOCK:
                    BATCH_PROGRESS.update({'status': 'running', 'current': 0, 'total': 0, 'result': None, 'message': ''})
                
                # the next line do the next things. Explaineds:
                # 1. Run the batch job in a separate thread (_run_batch_job)
                # 2. Run the progress_cb function in the main thread
                
                threading.Thread(target=_run_batch_job, args=(reader,), daemon=True).start()
                
            except Exception as e:
                error_message = str(e)+" "+str(type(e))+" "+str(e.__traceback__)
                return JsonResponse({'status': 'error', 'message': error_message}, status=500)    
            
            
            return JsonResponse({'status': 'started', 'message': 'Lote iniciado, procesando PDFs...'})  
            
       elif data.get('action') == 'mapping':
            try:
                extractor = MapExtractor(data['pdf_input'])
                extractor.file_path = data.get('pdf_input')
                extractor.output_map_dir = data.get('map_out')
                extractor.extract_layout().save_template("mapa_resultado.csv")
                return JsonResponse({'status': 'success', 'message': 'Mapeo guardado'})
            
            except Exception as e:
                mensaje=f"Error al procesar la ruta de mapeo: {e} en ruta {data.get('pdf_input')}"
                return JsonResponse({'status': 'error', 'message': mensaje}, status=500)
               
       
    return JsonResponse({'status': 'error', 'message': 'Solo se permiten peticiones POST'}, status=400) 
#### Edición de de CSV de MAPEO #####
def get_template_data(request):
    # Esto busca el CSV que generó el MapExtractor en Tab 1
    # Asegúrate de usar la misma ruta que guardaste en tu PersistenceManager
    config = PersistenceManager.load_paths()
    path = os.path.join(config.get('map_file_folder'),config.get('map_file'))
    if not os.path.exists(path):
        message_selected_fields = 'CSV not found. Please, check that the route and file name to .csv map in "PDF batch processing" tab exists in your system' 
        return JsonResponse({'status': 'error', 'message': message_selected_fields})
        
    df = pd.read_csv(path)
    return JsonResponse(df.fillna('').to_dict(orient='records'), safe=False)

def save_template_config(request):
    try:
        data = json.loads(request.body)
        config = PersistenceManager.load_paths()
        
        path = os.path.join(config.get('map_file_folder'), config.get('map_file'))
        
        if not os.path.exists(path):
            return JsonResponse({'status': 'error', 'message': 'Archivo CSV no encontrado'}, status=404)
        
        # --- AQUÍ LA SOLUCIÓN ---
        # Forzamos la columna 'header_label' como string para evitar el error de float64
        df = pd.read_csv(path, dtype={'header_label': str})
        
        # Actualizamos el DataFrame
        for update in data['updates']:
            idx = int(update['index'])
            if 0 <= idx < len(df):
                # Limpiamos el valor antes de guardarlo (opcional, elimina espacios accidentales)
                val = str(update['header_label']).strip()
                df.at[idx, 'header_label'] = val
        
        # Guardamos preservando el orden y los tipos
        df.to_csv(path, index=False, encoding='utf-8')
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        # Esto te ayudará a ver el error real en la consola de Django si algo falla
        print(f"Error crítico guardando configuración: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
#### Gestión del CSV de Filtros (Tab 4) ####

def get_filters_path():
    # Obtiene la carpeta 'config' donde está app_config.json
    print(PersistenceManager.CONFIG_FILE.parent)
    return PersistenceManager.CONFIG_FILE.parent / "filtros.csv"
    
def get_filters(request):
    path = PersistenceManager.CONFIG_FILE.parent / "filtros.csv"
    
    # 1. Si no existe, creamos el archivo con estructura básica
    if not path.exists():
        df = pd.DataFrame(columns=['texto_original', 'texto_reemplazo'])
        df.to_csv(path, index=False)
        return JsonResponse([], safe=False)
    
    try:
        # 2. Leemos el archivo
        df = pd.read_csv(path)
        
        # 3. Si está vacío (solo cabeceras), devolvemos lista vacía
        if df.empty:
            return JsonResponse([], safe=False)
            
        return JsonResponse(df.fillna('').to_dict(orient='records'), safe=False)
    except Exception as e:
        print(f"Error crítico en get_filters: {e}")
        return JsonResponse([], safe=False) # Retornar lista vacía para no romper el JS
def save_filters(request):
    try:
        data = json.loads(request.body)
        path = get_filters_path()
        
        # Guardar los nuevos filtros
        df = pd.DataFrame({
            'texto_original': data.get('original', []),
            'texto_reemplazo': data.get('reemplazo', [])
        })
        
        df.to_csv(path, index=False, encoding='utf-8')
        return JsonResponse({'status': 'ok', 'message': 'Filtros guardados correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
##### Functions for batch processing ####
# includes:
# 1. threading
# 2. progress bar
# 3. error handling

def _run_batch_job(reader):
    
    def progress_cb(current, total):
        with BATCH_LOCK:
            BATCH_PROGRESS['current'] = current
            BATCH_PROGRESS['total'] = total

    try:
        # this line is the one that does the work
        # 1. Run the batch job
        # 2. Run the progress_cb function
        # 3. Return the result
        # 4. Update the progress bar

        excel_path = reader.run_batch(progress_callback=progress_cb)
        with BATCH_LOCK:
            BATCH_PROGRESS['status'] = 'done'
            BATCH_PROGRESS['result'] = excel_path
    except Exception as e:
        with BATCH_LOCK:
            BATCH_PROGRESS['status'] = 'error'
            BATCH_PROGRESS['message'] = str(e)


def get_batch_progress(request):
    with BATCH_LOCK:
        return JsonResponse(dict(BATCH_PROGRESS))