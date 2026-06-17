import pandas as pd
import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from extraction.persistence import PersistenceManager
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

'''

{
    "pdf_folder": "/home/administrador/pruebas/",
    "pdf_input": "prueba.pdf",
    "map_file_folder": "D",
    "map_file": "E ",
    "mass_pdf_folder": "F",
    "excel_folder": "G  ",
    "sensitivity": "19",
    "output_map_path": "/home/administrador/pruebas/"
}


'''
class MapExtractor:
    """
    Analyzes a base PDF to extract layout coordinates.
    Generates a template CSV for mapping fields.
    """

    def __init__(self, pdf_path=None):
        # Ensure all required output paths are verified/configured
        config = PersistenceManager.ensure_configuration()
        
        # Load output configuration
        self.output_map_dir = config.get('output_map_path')
        self.output_excel_dir = config.get('excel_folder')
        
        # Handle PDF path logic
        self.file_path = pdf_path or config.get('map_file_folder')+config.get('map_file')

        # Persist the PDF path
        PersistenceManager.save_paths(last_map_route_pdf=self.file_path) #Creates Files & Dirs
        
        self.data = []

    def extract_layout(self):        
        for page in extract_pages(self.file_path):
            for element in page:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if text:
                        x0, y0, x1, y1 = element.bbox
                        self.data.append({
                            "page": page.pageid,
                            "x0": round(x0, 2),
                            "y0": round(y0, 2),
                            "x1": round(x1, 2),
                            "y1": round(y1, 2),
                            "header_label": "",
                            "original_text": text
                        })
        return self

    def save_template(self, filename):
        """Saves the layout template to the configured output directory."""
        # 1. Validar datos
        if not self.data:
            raise ValueError("Error: No se extrajo ningún dato. El archivo PDF podría estar vacío o ser una imagen.")
        print(self.output_map_dir)
        print(os.path.exists(self.output_map_dir))
        # 2. Validar directorio una sola vez
        if not os.path.exists(self.output_map_dir):
            raise FileNotFoundError(f"La carpeta de salida no existe: {self.output_map_dir}")

        full_path = os.path.join(self.output_map_dir, filename)
        df = pd.DataFrame(self.data)
        
        # 3. GUARDADO DIRECTO (Sin try/except intermedio)
        # Si esto falla, el error real (PermissionError, OSError, etc.)
        # subirá directamente a views.py sin que tú lo silencies.
        df.to_csv(full_path, index=False, encoding='utf-8')
        
        print(f"Template generado exitosamente en: {full_path}")
            

class MapMassReader:

    _COORD_COLS       = ('x0', 'y0', 'x1', 'y1')
    _WIDE_TOL_HEADERS = frozenset({"NOMINAL", "LIQUIDO"})

    def __init__(self, data=None):
        
        config = {**PersistenceManager.ensure_configuration(), **(data or {})}

        self.map_path        = os.path.join(config.get('map_file_folder', ''), config.get('map_file', ''))
        self.excel_folder    = config.get('excel_folder', '')
        self.mass_pdf_folder = config.get('mass_pdf_folder', '')
        self.sensitivity     = float(config.get('sensitivity', 5))
        self.filtro_path     = "config/filtros.csv"
        self.coordenadas     = self._load_map(self.map_path)
        self._coords_list    = self.coordenadas.to_dict('records')
        self._filtros        = self._load_filtros()

    def _load_map(self, path):
        df = pd.read_csv(path, dtype=str)  # TODO: todo como string, sin conversión automática
        for col in self._COORD_COLS:
            df[col] = df[col].str.strip().str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df[df['header_label'].notna() & df['header_label'].str.strip().ne('')]
        df = df[df['x0'].notna() & df['y0'].notna()]
        # diagnóstico: imprime lo que queda
        print("=== MAPA CARGADO ===")
        print(df[['header_label', 'x0', 'y0']].to_string())
        print(f"tipos: {df[['x0','y0']].dtypes.to_dict()}")
        return df.reset_index(drop=True)

    def _load_filtros(self):
        if not os.path.exists(self.filtro_path):
            return []
        try:
            df = pd.read_csv(self.filtro_path).fillna("")
            return list(df[['texto_original', 'texto_reemplazo']].itertuples(index=False, name=None))
        except Exception:
            return []

    def _aplicar_filtros(self, texto):
        for original, reemplazo in self._filtros:
            texto = texto.replace(str(original), str(reemplazo))
        return texto

    def extract_text_with_coordinates(self, pdf_path):
        return [
            {"text": el.get_text().strip(),
             "x0": float(el.x0), "y0": float(el.y0),
             "x1": float(el.x1), "y1": float(el.y1)}
            for page in extract_pages(pdf_path)
            for el in page
            if isinstance(el, LTTextContainer) and el.get_text().strip()
        ]

    def _match_line(self, linea, datos):
        lx = float(linea['x0'])
        ly = float(linea['y0'])
        texto = linea['text']

        for row in self._coords_list:
            header = row['header_label']
            cx = row['x0']
            cy = row['y0']

            # paranoia total: si por lo que sea llegan como no-float, skip
            try:
                cx = float(cx)
                cy = float(cy)
            except (TypeError, ValueError):
                continue

            tolx, toly = (50.0, 0.1) if header in self._WIDE_TOL_HEADERS \
                         else (self.sensitivity, self.sensitivity)

            if abs(lx - cx) <= tolx and abs(ly - cy) <= toly:
                if header == "FACTURAS_PAGADAS":
                    m = re.search(r'\d{2}/\d{5}', texto)
                    datos['ref_int'] = m.group(0) if m else texto
                    datos['ref_ext'] = texto.split(',')[0].strip() if ',' in texto else texto.strip()
                datos[header] = self._aplicar_filtros(texto)
                break

    def _process_pdf(self, pdf_path, pdf_file):
        print(f"procesando fichero {pdf_file} en {pdf_path}")
        print(f"Se grabaran los resultados en {self.excel_folder}")
        datos = {h: "" for h in self.coordenadas['header_label'].unique()}
        datos.update({'Fichero': pdf_file, 'ref_int': "", 'ref_ext': ""})
        for linea in self.extract_text_with_coordinates(pdf_path):
            self._match_line(linea, datos)
        return datos

    def run_batch(self):
        if not os.path.exists(self.mass_pdf_folder):
            raise FileNotFoundError(f"Carpeta PDF no encontrada: {self.mass_pdf_folder}")

        pdf_files = [f for f in os.listdir(self.mass_pdf_folder) if f.lower().endswith('.pdf')]
        if not pdf_files:
            raise FileNotFoundError(f"No hay PDFs en: {self.mass_pdf_folder}")

        results = [
            self._process_pdf(os.path.join(self.mass_pdf_folder, f), f)
            for f in pdf_files
        ]

        # os.makedirs(self.excel_folder, exist_ok=True) !!!!! peligro para la ciberseguridad
        output_path = os.path.join(
            self.excel_folder,
            f"resultados_batch_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        pd.DataFrame(results).to_excel(output_path, index=False)
        return output_path
    
    def check_rutes(self):

        if not os.path.exists(self.map_path):
            raise FileNotFoundError(f"CSV map not founded: {self.map_path}")
        if not os.path.exists(self.excel_folder):
            raise FileNotFoundError(f"Folder for final Excel file results not founded: {self.excel_folder}")
        if not os.path.exists(self.mass_pdf_folder):
            raise FileNotFoundError(f"Folder with pdf batch not founded: {self.mass_pdf_folder}")

        return