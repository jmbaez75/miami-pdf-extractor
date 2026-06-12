import pandas as pd
import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from extraction.persistence import PersistenceManager

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
        self.output_excel_dir = config.get('output_excel_path')
        
        # Handle PDF path logic
        self.file_path = pdf_path or config.get('last_map_route_pdf')
        
        if not self.file_path or not os.path.exists(self.file_path):
            raise FileNotFoundError("A valid PDF file is required to start the extraction process.")
        
        # Persist the PDF path
        PersistenceManager.save_paths(last_map_route_pdf=self.file_path)
        
        self.data = []

    def extract_layout(self):
        """Extracts text elements and their bounding box coordinates."""
        print(f"Analyzing layout of: {self.file_path}...")
        
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
        if not self.data:
            print("No data extracted. Nothing to save.")
            return

        full_path = os.path.join(self.output_map_dir, filename)
        df = pd.DataFrame(self.data)
        
        try:
            df.to_csv(full_path, index=False, encoding='utf-8')
            print(f"Template generated successfully at: {full_path}")
        except IOError as e:
            print(f"Failed to save file: {e}")