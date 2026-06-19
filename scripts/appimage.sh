#!/bin/bash

# --- CONFIGURACIÓN Y VERBOSE ---
set -ex  # -e: para parar si hay error, -x: para mostrar cada comando (verbose)

DIR_BASE="./"
APP_DIR="$DIR_BASE/final_app"
TOOL="appimagetool"
NOMBRE_APP="Miami_1.0.AppImage"

echo "--- 1. Preparando entorno AppImage ---"
cd "$DIR_BASE"

# 2. Verificar existencia de la carpeta
[ -d "$APP_DIR" ] || { echo "ERROR: La carpeta $APP_DIR no existe. Ejecuta compile.sh primero."; exit 1; }

# 3. Crear AppRun
echo '#!/bin/sh' > "$APP_DIR/AppRun"
echo 'cd "$(dirname "$0")"' >> "$APP_DIR/AppRun"
echo './miami' >> "$APP_DIR/AppRun"
chmod +x "$APP_DIR/AppRun"

# 4. Asegurar icono con extensión correcta
cp "$DIR_BASE/favicon.ico" "$APP_DIR/.DirIcon.png" || cp "$APP_DIR/miami.png" "$APP_DIR/.DirIcon.png"

# 5. Descargar appimagetool si no existe
if [ ! -f "$TOOL" ]; then
    echo "--- Descargando appimagetool ---"
    wget -O "$TOOL" https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$TOOL"
fi

# 4. Asegurar el icono como .DirIcon (sin extensión, pero el sistema lo reconoce)
cp "$DIR_BASE/favicon.ico" "$APP_DIR/.DirIcon" || cp "$APP_DIR/miami.png" "$APP_DIR/.DirIcon"

# 6. Crear el .desktop apuntando al nombre "base" del icono
cat <<EOF > "$APP_DIR/miami.desktop"
[Desktop Entry]
Name=Miami 1.0
Exec=AppRun
Icon=.DirIcon
Type=Application
Categories=Utility;
EOF

echo "--- 7. Generando archivo AppImage final ---"
# Forzamos arquitectura ARCH=x86_64 y nombre personalizado
ARCH=x86_64 ./"$TOOL" "$APP_DIR" "$NOMBRE_APP"

echo "--- ÉXITO: AppImage generada en $DIR_BASE/$NOMBRE_APP ---"
ls -lh "$DIR_BASE/$NOMBRE_APP"
