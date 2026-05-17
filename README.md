# L-Compressor

100% local image and video compression application.

<div align="center">
  <img src="assets/image/Banner.png" width="100%"/>
</div>

## Description

L-Compressor is a project developed in Python as part of my first year of Bac Pro CIEL.
It offers an intuitive interface with a simple mode for quick use, and an advanced mode for more precise control over compression settings.

## Features
- File selection (images and videos)
- Drag & drop support
- Image and video preview
- Built-in video playback
- Simple and advanced mode
- Image compression (quality, resolution, target size)
- Video compression with FFmpeg (CRF, bitrate, FPS, resolution)
- File information display (size, dimensions, duration, etc.)
- Double-click to edit slider values

## Preview

<div align="center">
  <table>
    <tr>
      <td align="center">
        <b>File selection</b><br/>
        <img src="assets/image/image/select.png" width="250"/>
      </td>
      <td align="center">
        <b>Image compression</b><br/>
        <img src="assets/image/image.png" width="250"/>
      </td>
      <td align="center">
        <b>Image compression (advanced)</b><br/>
        <img src="assets/image/image-advanced.png" width="250"/>
      </td>
    </tr>
    <tr>
      <td align="center">
        <b>Video compression</b><br/>
        <img src="assets/image/video.png" width="250"/>
      </td>
      <td align="center">
        <b>Video compression (advanced)</b><br/>
        <img src="assets/image/video-advanced.png" width="250"/>
      </td>
      <td></td>
    </tr>
  </table>
</div>

## Technologies used

- Python
- CustomTkinter (GUI)
- FFmpeg (video processing)
- Pillow (image processing)
- tkinterdnd2 (drag & drop)
- VLC (video playback)

### Download the executable

[![Download from GitHub Releases](https://img.shields.io/badge/Download-GitHub%20Releases-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/nath89-52/L_Compressor/releases/tag/v1.0)

## Installation

### 1. Clone the project
```bash
git clone https://github.com/nath89-52/L_Compressor.git
cd L_Compressor
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

## Windows
#### Included dependencies
The repository already includes:
- FFmpeg binaries
- VLC runtime files
No additional installation is required.

#### Run the application
```bash
python src/main.py
```
### Build Windows executable
#### First build (generates .spec file)
```bash
pyinstaller --onefile --windowed --name "L-Compressor" ^
--add-binary "ffmpeg.exe;." ^
--add-binary "vlc/libvlc.dll;vlc" ^
--add-binary "vlc/libvlccore.dll;vlc" ^
--add-data "vlc/plugins;vlc/plugins" ^
--icon=assets/logo.ico src/main.py
```

#### Subsequent builds
```bash
pyinstaller "L-Compressor.spec"
```

## Linux

### 1. System dependencies

#### Arch Linux
```bash
sudo pacman -Syu python python-pip tk ffmpeg vlc git
```
#### Ubuntu / Debian
```bash
sudo apt install python3 python3-pip python3-tk ffmpeg vlc git
```

### 2. Virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Run the application
```bash
python src/main.py
```

### Build Linux executable

#### Install PyInstaller if needed:
```bash
pip install pyinstaller
```
#### Then build:
```bash
pyinstaller --onefile --windowed --name "L-Compressor" src/main.py
```
The binary will be located in:
```bash
dist/L-Compressor
```
Run it with:
```bash
./dist/L-Compressor
```

⚠ Notes (Linux)
FFmpeg must be installed via system package manager
VLC is required for video preview support
Some virtual machines may have issues with hardware-accelerated video decoding
The application automatically uses system FFmpeg (shutil.which("ffmpeg"))

## Usage
- Run via terminal (`python main.py`) or launch the `.exe`
- Select or drag & drop a file
- Choose compression settings
- Click Compress
- Choose the output location

## Available modes
### Simple mode
Quick quality adjustment

### Advanced mode
#### Images:
- Minimum quality
- Resolution
- Target size

#### Videos:
- Resolution
- FPS
- Custom bitrate

## Roadmap

- [x] Drag & Drop
- [x] Video preview
- [ ] Compression history
- [ ] Custom themes
- [ ] Size estimation before compression

## About the project

This is my first project published on GitHub.

It was developed as part of my first year of Bac Pro CIEL and allowed me to learn Python application development, the use of multimedia libraries, and the creation of graphical user interfaces.

For any suggestion, advice or feedback:

You can:
- open an issue on GitHub
- propose improvements
- report bugs

## License

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
