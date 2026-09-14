#!/usr/bin/env sh

# Copie l'application complete afin que main.py et tous ses modules restent
# synchronises sur la carte. Lancer depuis la racine du depot.
set -eu

PORT="${1:-/dev/ttyUSB0}"

if ! command -v mpremote >/dev/null 2>&1; then
    echo "Erreur: mpremote est introuvable. Installer avec: python -m pip install mpremote" >&2
    exit 1
fi

if [ ! -f esp32/main.py ]; then
    echo "Erreur: lancer deploy.sh depuis la racine du depot." >&2
    exit 1
fi

echo "Deploiement de l'application complete sur ${PORT}..."
mpremote connect "${PORT}" fs cp -r esp32/actuators :
mpremote connect "${PORT}" fs cp -r esp32/connectivity :
mpremote connect "${PORT}" fs cp -r esp32/cameras :
mpremote connect "${PORT}" fs cp -r esp32/indicators :
mpremote connect "${PORT}" fs cp -r esp32/sensors :
mpremote connect "${PORT}" fs cp esp32/boot.py :boot.py
mpremote connect "${PORT}" fs cp esp32/wifi_config.py :wifi_config.py
# main.py est copie en dernier: il ne peut donc pas demarrer avant ses imports.
mpremote connect "${PORT}" fs cp esp32/main.py :main.py

echo "Deploiement termine. Redemarrage de l'ESP32..."
mpremote connect "${PORT}" reset
