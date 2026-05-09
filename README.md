# L-Compressor

Application de compression d’images et de vidéos 100% locale.

## Description

L-Compressor est un projet développé en Python dans le cadre de l’année de Première Bac Pro CIEL.
Elle propose une interface intuitive avec un mode simple pour une utilisation rapide, et un mode avancé pour un contrôle plus précis des paramètres de compression.

## Fonctionnalités principales
- Sélection de fichiers (images et vidéos)
- Glisser-déposer (drag & drop)
- Prévisualisation des images et des video
- Lecture vidéo intégrée
- Mode simple et mode avancé
- Compression d’images (qualité, résolution, taille cible)
- Compression vidéo avec FFmpeg (CRF, bitrate, FPS, résolution)
- Affichage des informations (taille, dimensions, durée, etc.)
- Double-click pour modifier les valeurs des curseurs

## Technologies utilisées

- Python
- CustomTkinter (interface graphique)
- FFmpeg (traitement vidéo)
- Pillow (traitement d’image)
- tkinterdnd2 (drag & drop)
- VLC (lecture vidéo)

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/nath89-52/L_Compressor.git
cd L_Compressor
 ```

### 2. Installer les dépendances

```bash
pip install customtkinter pillow tkinterdnd2
```

#### Prévisualisation vidéo (optionnelle)

Pour activer la prévisualisation vidéo, il faut :

- Les fichiers `libvlc.dll`, `libvlccore.dll` et le dossier `plugins/` dans le répertoire du projet *(déjà inclus dans le repo)*
- Le module Python `python-vlc` :

```bash
pip install python-vlc
```

> ℹ️ L'installation de VLC Media Player n'est **pas nécessaire**, les fichiers inclus suffisent.

### 3. Installer FFmpeg

Ce projet nécessite FFmpeg pour fonctionner.

- Télécharger FFmpeg : https://ffmpeg.org/download.html
- Extraire l’archive
- Placer `ffmpeg.exe` dans le même dossier que le script  
ou ajouter FFmpeg au PATH système (recommandé)

### 4. Lancer l’application

```bash
python main.py
```

## Build de l'exécutable

### Première compilation (génère le .spec)
```bash
pyinstaller --onefile --windowed --name "L Compressor" --add-binary "ffmpeg.exe;." --add-binary "vlc/libvlc.dll;vlc” --add-binary "vlc/libvlccore.dll;vlc” --add-data "vlc/plugins;vlc/plugins” --icon=logo.ico main.py
```

### Recompilations avec le .spec
```bash
pyinstaller "L Compressor.spec"
```

> !! Ne pas relancer la première commande après avoir modifié le `.spec`, elle l'écrasera.

### Télécharger l’exécutable

[![Download from GitHub Releases](https://img.shields.io/badge/Download-GitHub%20Releases-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/nath89-52/L_Compressor/releases/tag/v1.0)

### Utilisation
- Lancer via le terminal (python main.py) ou lancer le .exe
- Sélectionner un fichier ou le glisser dans la fenêtre
- Choisir les options de compression
- Cliquer sur Compresser
- Choisir l’emplacement de sauvegarde

## Modes disponibles
### Mode simple
Réglage rapide de la qualité

### Mode avancé
#### Images :
- Qualité minimum
- Résolution
- Taille cible

#### Vidéos :
- Résolution
- FPS
- Bitrate personnalisé

## Roadmap

- [x] Drag-Drop
- [x] Preview video
- [ ] Historique des compressions
- [ ] Thèmes personnalisés
- [ ] Estimation de taille avant compression

## À propos du projet

Ce projet est mon premier projet publié sur GitHub.

Il a été réalisé dans le cadre de l’année de Première Bac Pro CIEL et me permet d’apprendre le développement d’applications Python, l’utilisation de bibliothèques multimédias ainsi que la création d’interfaces graphiques.

Les retours, conseils et suggestions sont les bienvenus.

## Contact

Pour toute suggestion, conseil ou retour sur le projet :

Vous pouvez :
- ouvrir une issue sur GitHub
- proposer des améliorations
- signaler des bugs

## Licence

MIT License

Copyright (c) 2026 nath89-52

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.