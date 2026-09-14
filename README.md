# Système d'irrigation ESP32

## Déploiement

`main.py` importe plusieurs modules locaux, notamment
`indicators.buzzer` et `connectivity.wifi`. Il ne faut donc pas copier uniquement
`main.py` sur la carte : cela laisserait les dépendances absentes ou dans une
ancienne version.

Depuis la racine du dépôt, déployer toute l'application avec :

```sh
./deploy.sh
```

Le port par défaut est `/dev/ttyUSB0`. Pour utiliser un autre port :

```sh
./deploy.sh /dev/ttyACM0
```

Le script copie les répertoires `actuators`, `connectivity`, `indicators` et
`sensors`, puis les fichiers de configuration et enfin `main.py`. Il redémarre
ensuite la carte. Cette copie complète corrige notamment l'erreur
`ImportError: no module named 'indicators.buzzer'`.

## Configuration Wi-Fi

Dans `esp32/wifi_config.py`, laisser `WIFI_SSID = None` pour uniquement scanner
les réseaux à proximité. Pour établir une connexion, renseigner le SSID et le
mot de passe avant de lancer le déploiement :

```python
WIFI_SSID = "mon-reseau"
WIFI_PASSWORD = "mon-mot-de-passe"
```
