from django.core.management.base import BaseCommand
from extraction.processor import MapExtractor
import os

class Command(BaseCommand):
    help = 'Analyzes a PDF and generates a coordinates template CSV'

    def add_arguments(self, parser):
        # Permitimos pasar la ruta del archivo PDF como argumento
        parser.add_argument('pdf_path', type=str, help='Path to the source PDF file')    # recoge las variables 

    def handle(self, *args, **options):
        pdf_path = options['pdf_path']
        output_csv = "template_coords.csv"

        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f"File not found: {pdf_path}"))
            return

        # Instanciamos nuestra clase MapExtractor y ejecutamos el proceso
        try:
            extractor = MapExtractor(pdf_path)                                             # llama a l clase MapExtractor
            extractor.extract_layout().save_template(output_csv)
            self.stdout.write(self.style.SUCCESS(f"Successfully generated {output_csv}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))