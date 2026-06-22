#!/bin/bash
# Función para reportar errores
error_exit() {
    echo "¡ERROR en la línea $1: $2"
    exit 1
}

echo "--- INICIANDO CONSTRUCCIÓN ---"

# 1. Limpieza rigurosa
rm -rf build dist final_app staticfiles || error_exit $LINENO "No se pudo limpiar build/dist"

# 2. Verificar archivos esenciales
[ -f "run_django.py" ] || error_exit $LINENO "No existe run_django.py"
[ -f "favicon.ico" ] || error_exit $LINENO "No existe favicon.ico"
[ -f "manage.py" ] || error_exit $LINENO "No existe manage.py"

# 3. Recolectar estáticos al directorio 'staticfiles'
echo "Recolectando archivos estáticos en /staticfiles..."
uv run python manage.py collectstatic --noinput || error_exit $LINENO "Falló el collectstatic"

# 4. Compilación PyInstaller
# IMPORTANTE: Hemos cambiado 'static' por 'staticfiles' en --add-data
echo "Ejecutando PyInstaller con el entorno activo de uv..."
uv run --active -- python -m PyInstaller \
  --noconfirm --onedir --windowed --name "miami" \
  --add-data "staticfiles:staticfiles" \
  --add-data "config:config" \
  --add-data "extraction:extraction" \
  --add-data "templates:templates" \
  --add-data "db.sqlite3:." \
  --collect-all whitenoise \
  --collect-all waitress \
  --collect-all django \
  run_django.py || error_exit $LINENO "PyInstaller falló"

# 5. Estructura final
echo "Creando estructura final en /final_app..."
mkdir -p final_app || error_exit $LINENO "No se pudo crear final_app"
cp -r dist/miami/* final_app/ || error_exit $LINENO "No se pudieron copiar los archivos desde dist/"

# 6. Icono y archivo .desktop
cp favicon.ico final_app/miami.png
cat <<EOF > final_app/miami.desktop
[Desktop Entry]
Type=Application
Name=Miami
Exec=miami
Icon=miami.png
Comment=Aplicacion de gestion FBuro
Categories=Utility;
EOF

echo "--- CONSTRUCCIÓN FINALIZADA: Revisa la carpeta final_app/ ---"
