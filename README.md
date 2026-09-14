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

Le script copie les répertoires `actuators`, `cameras`, `connectivity`,
`indicators` et `sensors`, puis les fichiers de configuration et enfin
`main.py`. Il redémarre ensuite la carte. Cette copie complète corrige notamment l'erreur
`ImportError: no module named 'indicators.buzzer'`.

## Caméra OV2640

L'application initialise l'OV2640 au démarrage avec le module MicroPython
`camera`. Le firmware installé sur l'ESP32 doit donc inclure ce module et être
configuré avec le brochage de la carte caméra. Le pilote accepte aussi bien
l'API fonctionnelle `camera.init()` / `camera.capture()` que l'API orientée
objet `camera.Camera()` avec `capture()` ou `snapshot()`. À chaque **nouvelle** détection
du PIR, une image JPEG est enregistrée dans `/photos` (`photo_0001.jpg`,
`photo_0002.jpg`, etc.) et le LCD affiche `Photo prise !` avec le nom du
fichier. Une sortie PIR qui reste haute ne déclenche pas plusieurs photos.

Si la caméra est absente ou si le firmware ne fournit pas `camera`, les autres
capteurs et l'irrigation continuent de fonctionner et l'erreur est écrite sur
le port série.

Le simple fait que `import camera` fonctionne ne garantit pas qu'il s'agit du
pilote OV2640. Si le message `module camera incompatible` apparaît, vérifier
dans le REPL avec `import camera; print(dir(camera))`, puis installer un firmware
ESP32 avec le pilote caméra natif si aucune des API indiquées ci-dessus n'est
présente.

Chaque capture est vérifiée avant son enregistrement : une image qui ne
commence pas par la signature JPEG `FF D8` est refusée au lieu de créer un
fichier `.jpg` illisible. Le message `capture non JPEG` signifie que le pilote
renvoie probablement des pixels RGB bruts et doit être configuré en JPEG. Les
anciens fichiers déjà incorrects doivent être supprimés du dossier `/photos`.

## Configuration Wi-Fi

Dans `esp32/wifi_config.py`, laisser `WIFI_SSID = None` pour uniquement scanner
les réseaux à proximité. Pour établir une connexion, renseigner le SSID et le
mot de passe avant de lancer le déploiement :

```python
WIFI_SSID = "mon-reseau"
WIFI_PASSWORD = "mon-mot-de-passe"
```
