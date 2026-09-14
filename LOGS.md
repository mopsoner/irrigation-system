# Irrigation System - Journal de suivi

Ce fichier sert de journal de bord du projet afin de conserver un historique clair des étapes réalisées, du matériel utilisé, des choix techniques et des prochaines actions.

## 2026-09-14

### Ajout du Wi-Fi

- mode station (STA) active au demarrage
- scan des points d'acces avec affichage du SSID, canal, signal et securite
- connexion facultative via `esp32/wifi_config.py`
- delai de connexion configurable et fonctionnement des capteurs maintenu en cas d'erreur Wi-Fi
- le mot de passe n'est jamais affiche dans la console
- ajout de `deploy.sh` pour copier tous les modules sur la carte et eviter les
  erreurs d'import provoquees par une copie isolee de `main.py`

### État actuel

- Environnement de développement : Ubuntu + VS Code
- Carte : ESP32 Freenove / ESP32-WROVER
- Firmware : MicroPython
- Déploiement vers l'ESP32 : `mpremote`
- Port série utilisé : `/dev/ttyUSB0`

### Capteurs et composants actifs

- DHT11 sur GPIO 27
  - mesure de la température
  - mesure de l'humidité
- LED verte sur GPIO 15
- LED jaune sur GPIO 2
- LED rouge sur GPIO 4
- LCD1602 I2C
  - SDA : GPIO 13
  - SCL : GPIO 14
  - bus : `SoftI2C`
  - adresses supportées : `0x27` et `0x3F`

### Logique actuelle

Seuils configurés :

- Température normale : `< 30°C`
- Humidité normale : `> 75%`

Comportement des LED :

- Vert : température et humidité normales
- Jaune : une seule des deux conditions est normale
- Rouge : température et humidité hors seuils

Le LCD affiche :

- température
- humidité
- statut température
- statut humidité

### Architecture actuelle

```text
esp32/
├── boot.py
├── main.py
├── sensors/
│   ├── __init__.py
│   └── dht_sensor.py
├── indicators/
│   ├── __init__.py
│   ├── leds.py
│   └── lcd1602.py
└── actuators/
```

### Points validés

- ESP32 reconnu correctement sous Ubuntu
- conflit `brltty` / CH340 résolu
- MicroPython installé et opérationnel
- communication série avec `mpremote` validée
- lecture DHT11 validée
- gestion des LED validée
- LCD1602 fonctionnel
- projet versionné sur GitHub

### Points laissés de côté pour le moment

- relais
- pompe à eau
- capteur d'humidité du sol
- MQTT
- historisation des mesures
- supervision distante

### Prochaines étapes possibles

1. Centraliser les GPIO et seuils dans un fichier `config.py`
2. Ajouter un logger logiciel pour suivre les mesures et erreurs
3. Ajouter un capteur d'humidité du sol
4. Ajouter la communication Wi-Fi
5. Ajouter MQTT
6. Ajouter la commande d'une pompe ou électrovanne
7. Ajouter la persistance des mesures côté serveur

---

## Convention pour les prochaines entrées

Ajouter une nouvelle section avec la date :

```markdown
## YYYY-MM-DD

### Changements

- ...

### Tests

- ...

### Problèmes rencontrés

- ...

### Prochaines actions

- ...
```
