#!/bin/bash
set -e  # para que si algo falla, se detenga en seco

echo "--- Copiando proyecto a /tmp ---"
rm -rf /tmp/construccion_fburo
cp -r /home/administrador/Proyectos_Python/FBuro /tmp/construccion_fburo

cd /tmp/construccion_fburo

echo "--- Compilando con PyInstaller ---"
bash compile.sh

echo "--- Generando AppImage ---"
bash appimage.sh

echo "--- TERMINADO ---"
echo "AppImage en: /tmp/construccion_fburo/Miami_1.0.AppImage"