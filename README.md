# corail_scrapper

Scripts pour récupérer et visualiser les conventions collectives publiées sur le site Corail.

## Interface web

Le script `visualisation.py` lance une petite application Flask qui affiche les données de `syndicats.db`.

### Sous Linux

```bash
chmod +x setup_env.sh
./setup_env.sh
```

Le script crée un environnement virtuel, installe les dépendances (Flask, pandas) puis démarre le serveur disponible sur http://127.0.0.1:5000.

### Sous Windows

Exécuter `setup_env.bat` et suivre les indications.
