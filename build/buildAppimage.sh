#!/bin/bash
# Script unificado para construir la AppImage de la aplicación Miami
set -e # Detener el script si ocurre algún error

# --- 1. CONFIGURACIÓN ---
PROJECT_SRC="/home/administrador/Proyectos_Python/FBuro"
BUILD_DIR="/tmp/construccion_fburo"
APP_DIR="$BUILD_DIR/final_app"
APPIMAGE_TOOL="appimagetool"
APPIMAGE_NAME="Miami_1.0.AppImage"

echo "--- Iniciando proceso de construcción ---"

# --- 2. PREPARACIÓN DEL ENTORNO ---
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cp -r "$PROJECT_SRC"/* "$BUILD_DIR/"
cd "$BUILD_DIR"

# Verificación de archivos base
if [ ! -f "run_django.py" ]; then
    echo "ERROR: run_django.py no encontrado."
    exit 1
fi

# --- 3. COMPILACIÓN CON PYINSTALLER ---
echo "--- Compilando con PyInstaller ---"
uv run python -m PyInstaller \
  --noconfirm --onedir --windowed --name "miami" \
  --add-data "staticfiles:staticfiles" \
  --add-data "config:config" \
  --add-data "extraction:extraction" \
  --add-data "templates:templates" \
  --collect-all whitenoise \
  --collect-all waitress \
  --collect-all django \
  run_django.py

# --- 4. ESTRUCTURACIÓN DE APPIMAGE ---
echo "--- Estructurando archivos para AppImage ---"
mkdir -p "$APP_DIR"
cp -r dist/miami/* "$APP_DIR/"

# Configuración del icono
if [ -f "favicon.ico" ]; then
    cp favicon.ico "$APP_DIR/.DirIcon"
    cp favicon.ico "$APP_DIR/miami.png"
fi

# Crear AppRun
cat <<EOF > "$APP_DIR/AppRun"
#!/bin/sh
# Directorio base de la AppImage
cd "\$(dirname "\$0")"
# Ejecutar el binario generado por PyInstaller
exec ./miami
EOF
chmod +x "$APP_DIR/AppRun"

# Crear archivo .desktop
cat <<EOF > "$APP_DIR/miami.desktop"
[Desktop Entry]
Name=Miami 1.1
Exec=AppRun
Icon=miami
Type=Application
Categories=Utility;
EOF

# --- 5. GENERACIÓN DE LA APPIMAGE ---
if [ ! -f "$APPIMAGE_TOOL" ]; then
    echo "--- Descargando appimagetool ---"
    wget -O "$APPIMAGE_TOOL" https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$APPIMAGE_TOOL"
fi

echo "--- Generando archivo final ---"
ARCH=x86_64 ./"$APPIMAGE_TOOL" "$APP_DIR" "$APPIMAGE_NAME"

echo "--- ÉXITO ---"
echo "La aplicación ha sido empaquetada en: $BUILD_DIR/$APPIMAGE_NAME"