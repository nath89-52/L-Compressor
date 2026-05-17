# ============================================================================
# L COMPRESSOR - Application de compression d'images et vidéos
# ============================================================================
# Dépendances requises:
#   - customtkinter (interface graphique moderne)
#   - tkinterdnd2 (glisser-déposer des fichiers) 
#   - python-vlc (lecture vidéo dans l'interface)
#   - Pillow (PIL) pour le traitement d'images
#   - ffmpeg.exe pour le traitement vidéo
#   - Les modules optionnels sont utilisés si disponibles, sinon des messages d'installation sont affichés.
#   - 
# ============================================================================

import os
import subprocess
import threading
import sys
import re
import platform
import shutil
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import json

if getattr(sys, 'frozen', False):
    base_config = os.path.dirname(sys.executable)
else:
    base_config = os.path.dirname(__file__)

CONFIG_PATH = os.path.join(base_config, "config.json")

def charger_volume():
    """Charge le volume depuis le fichier config."""
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            return data.get("volume", 20)  # 20% par défaut
    except Exception:
        return 20

def sauvegarder_volume(volume):
    """Sauvegarde le volume dans le fichier config."""
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump({"volume": volume}, f)
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

if platform.system() == "Windows":
    FFMPEG_PATH = BASE_DIR / "ffmpeg" / "windows" / "ffmpeg.exe"
    FFPROBE_PATH = BASE_DIR / "ffmpeg" / "windows" / "ffprobe.exe"
else:
    FFMPEG_PATH = shutil.which("ffmpeg")
    FFPROBE_PATH = shutil.which("ffprobe")

# ----------------------------------------------------------------------------
# IMPORTS OPTIONNELS
# ----------------------------------------------------------------------------

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKINTERDND2_DISPONIBLE = True
except ImportError:
    TKINTERDND2_DISPONIBLE = False
    print("tkinterdnd2 non installé. Installation recommandée: pip install tkinterdnd2")

import platform

if platform.system() == "Windows":
    import os
    if getattr(sys, 'frozen', False):
        vlc_path = os.path.join(sys._MEIPASS, 'vlc')
        os.environ['PYTHON_VLC_MODULE_PATH'] = vlc_path
        os.environ['PYTHON_VLC_LIB_PATH'] = os.path.join(vlc_path, 'libvlc.dll')

try:
    import vlc
    VLC_DISPONIBLE = True
except ImportError:
    VLC_DISPONIBLE = False

# ============================================================================
# CONFIGURATION ET CONSTANTES
# ============================================================================

COULEUR_BG = "#1A1A1B"
COULEUR_CADRE = "#2B2B2B"
COULEUR_TEXTE = "#FFFFFF"
COULEUR_TEXTE_GRIS = "#AAAAAA"

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

EXTENSIONS_IMAGE = ('.jpg', '.jpeg', '.png', '.webp')
EXTENSIONS_VIDEO = ('.mp4', '.mkv', '.mov', '.avi')

# ============================================================================
# GESTION DES TÂCHES EN ARRIÈRE-PLAN
# ============================================================================

def executer_en_arriere_plan(fonction):
    """Exécute une fonction dans un thread séparé pour ne pas geler l'UI."""
    thread = threading.Thread(target=fonction)
    thread.daemon = True
    thread.start()

# ============================================================================
# VARIABLES GLOBALES
# ============================================================================

fichier_selectionne = None
type_fichier = None

# ============================================================================
# TRAITEMENT DES FICHIERS
# ============================================================================

def traiter_fichier(fichier):
    """
    Traite le fichier sélectionné:
    - Détecte le type (image ou vidéo)
    - Affiche la prévisualisation
    - Montre les informations du fichier
    - Affiche les options de compression
    """
    global fichier_selectionne, type_fichier
    
    if not fichier or not os.path.exists(fichier):
        return
    
    fichier_selectionne = fichier
    ext = os.path.splitext(fichier)[1].lower()

    if ext in EXTENSIONS_IMAGE:
        type_fichier = "image"
        afficher_preview_image(fichier)
        afficher_infos_image(fichier)
        afficher_options_image()
    elif ext in EXTENSIONS_VIDEO:
        type_fichier = "video"
        afficher_preview_video(fichier)
        afficher_infos_video(fichier)
        afficher_options_video()
    else:
        messagebox.showwarning("Format non supporté", "Veuillez sélectionner une image ou une vidéo.")
        return

    # On vérifie si le bouton est déjà affiché avant de le pack() à nouveau
    btn_compresser.configure(state="normal")
    if not btn_compresser.winfo_ismapped():
        btn_compresser.pack(fill="x", pady=(8, 0))
    label_drop.pack_forget()

def selectionner_fichier():
    """Ouvre une boîte de dialogue pour sélectionner un fichier."""
    fichier = filedialog.askopenfilename(filetypes=[
        ("Tous les médias", "*.jpg *.jpeg *.png *.webp *.mp4 *.mkv *.mov *.avi"),
        ("Images", "*.jpg *.jpeg *.png *.webp"),
        ("Vidéos", "*.mp4 *.mkv *.mov *.avi"),
    ])
    if fichier:
        traiter_fichier(fichier)

def on_drop(event):
    """Gère le glisser-déposer de fichiers depuis l'explorateur."""
    fichier = event.data
    fichier = fichier.strip('{}')
    traiter_fichier(fichier)

# ============================================================================
# PRÉVISUALISATION
# ============================================================================

def afficher_preview_image(fichier):
    """Affiche l'image sélectionnée dans la zone de prévisualisation."""
    vider_preview()
    try:
        img = Image.open(fichier)
        img.thumbnail((460, 260))
        photo = ImageTk.PhotoImage(img)
        lbl = ctk.CTkLabel(frame_preview, image=photo, text="")
        lbl.image = photo
        lbl.pack(expand=True)
    except Exception as e:
        ctk.CTkLabel(frame_preview, text=f"Impossible d'afficher l'image\n{e}",
                     text_color="gray").pack(expand=True)

def afficher_preview_video(fichier):
    """Affiche la vidéo avec VLC intégré."""
    vider_preview()

    if VLC_DISPONIBLE:
        try:
            instance = vlc.Instance()
            player = instance.media_player_new()

            video_frame = ctk.CTkFrame(frame_preview, fg_color="black")
            video_frame.pack(expand=True, fill="both")

            fenetre.update_idletasks()
            handle = video_frame.winfo_id()

            if sys.platform == "win32":
                player.set_hwnd(handle)
            else:
                player.set_xwindow(handle)

            media = instance.media_new(fichier)
            player.set_media(media)

            controls = ctk.CTkFrame(frame_preview)
            controls.pack(fill="x", pady=4)

            ctk.CTkButton(controls, text="▶ Play", command=player.play).pack(side="left", padx=5)
            ctk.CTkButton(controls, text="⏸ Pause", command=player.pause).pack(side="left", padx=5)
            ctk.CTkButton(controls, text="⏹ Stop", command=player.stop).pack(side="left", padx=5)

            volume_frame = ctk.CTkFrame(frame_preview)
            volume_frame.pack(fill="x", padx=10, pady=(0, 5))

            ctk.CTkLabel(volume_frame, text="🔊 Volume").pack(side="left", padx=5)

            slider_volume = ctk.CTkSlider(volume_frame, from_=0, to=100)
            slider_volume.pack(side="left", fill="x", expand=True, padx=5)

            label_volume = ctk.CTkLabel(volume_frame, text="")
            label_volume.pack(side="right", padx=5)

            volume_defaut = charger_volume()
            player.audio_set_volume(volume_defaut)
            slider_volume.set(volume_defaut)
            label_volume.configure(text=f"{volume_defaut}%")

            def changer_volume(val):
                volume = int(val)
                player.audio_set_volume(volume)
                label_volume.configure(text=f"{volume}%")
                sauvegarder_volume(volume)

            slider_volume.configure(command=changer_volume)

            def toggle_mute():
                player.audio_toggle_mute()

            ctk.CTkButton(volume_frame, text="🔇", width=40, command=toggle_mute).pack(side="right", padx=5)

        except Exception as e:
            ctk.CTkLabel(frame_preview, text=f"Erreur VLC\n{e}", text_color="gray").pack(expand=True)

    else:
        afficher_miniature_video(fichier)

def afficher_miniature_video(fichier):
    """Extrait une miniature de la vidéo avec ffmpeg."""
    try:
        miniature_path = os.path.join(base_path, "_miniature_temp.jpg")
        commande = [
            str(FFMPEG_PATH), '-y', '-i', fichier,
            '-vframes', '1', '-q:v', '2', miniature_path
        ]
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        subprocess.run(commande, check=True, creationflags=flags,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        img = Image.open(miniature_path)
        img.thumbnail((460, 240))
        photo = ImageTk.PhotoImage(img)
        lbl = ctk.CTkLabel(frame_preview, image=photo, text="")
        lbl.image = photo
        lbl.pack(expand=True)
        ctk.CTkLabel(frame_preview,
                     text="⚠ Installez vlc pour la lecture vidéo (pip install python-vlc)",
                     text_color="gray", font=("Arial", 10)).pack()
    except Exception:
        ctk.CTkLabel(frame_preview, text="📹 Vidéo sélectionnée\n(prévisualisation indisponible)",
                     text_color="gray", font=("Arial", 13)).pack(expand=True)

def vider_preview():
    """Supprime tous les éléments de la zone de prévisualisation."""
    for widget in frame_preview.winfo_children():
        widget.destroy()

# ============================================================================
# INFORMATIONS SUR LES FICHIERS
# ============================================================================

def afficher_infos_image(fichier):
    """Affiche les informations du fichier image (taille, dimensions, format)."""
    try:
        taille = os.path.getsize(fichier) / 1024
        unite = "Ko"
        if taille > 1024:
            taille /= 1024
            unite = "Mo"
        img = Image.open(fichier)
        w, h = img.size
        ext = os.path.splitext(fichier)[1].upper().replace(".", "")
        label_infos.configure(text=f"Taille : {taille:.1f} {unite}   •   {w}x{h}px   •   {ext}")
    except Exception:
        label_infos.configure(text="Infos indisponibles")

def afficher_infos_video(fichier):
    """
    Affiche les informations du fichier vidéo.
    En mode normal: taille, résolution, durée, format.
    En mode avancé: ajoute le bitrate et les FPS extraits via ffmpeg.
    """
    try:
        taille = os.path.getsize(fichier) / (1024 * 1024)
        ext = os.path.splitext(fichier)[1].upper().replace(".", "")

        result = subprocess.run(
            [str(FFMPEG_PATH), '-i', fichier],
            stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
            creationflags=(subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        )
        output = result.stderr.decode('utf-8', errors='ignore')

        duree = "?"
        for ligne in output.split('\n'):
            if 'Duration:' in ligne:
                duree = ligne.strip().split('Duration:')[1].split(',')[0].strip()
                break

        dims = "?"
        match = re.search(r'(\d{2,5}x\d{2,5})', output)
        if match:
            dims = match.group(1)

        bitrate = "?"
        for ligne in output.split('\n'):
            if 'bitrate:' in ligne:
                match_br = re.search(r'bitrate:\s*(\d+(?:\.\d+)?)\s*kb/s', ligne, re.IGNORECASE)
                if match_br:
                    bitrate = match_br.group(1)
                    break
        if bitrate == "?":
            for ligne in output.split('\n'):
                if 'Stream' in ligne and 'Video:' in ligne:
                    match_br = re.search(r'(\d+(?:\.\d+)?)\s*kb/s', ligne)
                    if match_br:
                        bitrate = match_br.group(1)
                        break

        fps = "?"
        for ligne in output.split('\n'):
            if 'Stream' in ligne and 'Video:' in ligne:
                match_fps = re.search(r'(\d+(?:\.\d+)?)\s*fps', ligne, re.IGNORECASE)
                if match_fps:
                    fps = match_fps.group(1)
                    break

        infos_base = f"Taille : {taille:.1f} Mo   •   {dims}px   •   Durée : {duree}   •   {ext}"

        if mode_avance.get():
            infos_base += f"   •   Bitrate : {bitrate} kb/s   •   FPS : {fps}"

        label_infos.configure(text=infos_base)
    except Exception as e:
        label_infos.configure(text=f"Infos indisponibles\n({str(e)})")

# ============================================================================
# OPTIONS DE COMPRESSION
# ============================================================================

def afficher_options_image():
    """Affiche les options de compression pour les images."""
    vider_options()
    if mode_avance.get():
        _options_image_avance()
    else:
        _options_image_simple()

def afficher_options_video():
    """Affiche les options de compression pour les vidéos."""
    vider_options()
    if mode_avance.get():
        _options_video_avance()
    else:
        _options_video_simple()

def vider_options():
    """Efface les options précédentes avant d'en afficher de nouvelles."""
    for widget in frame_options.winfo_children():
        try:
            widget.pack_forget()
        except Exception:
            pass

def _options_image_simple():
    """Options simples pour images: un seul slider de qualité."""
    global slider_qualite
    ctk.CTkLabel(frame_options, text="Qualité (10-95)", font=("Arial", 12), text_color=COULEUR_TEXTE).pack(pady=(8, 0))
    slider_qualite = ctk.CTkSlider(frame_options, from_=10, to=95)
    slider_qualite.set(70)
    slider_qualite.pack(fill="x", padx=40, pady=4)
    lbl = ctk.CTkLabel(frame_options, text="Qualité : 70", text_color=COULEUR_TEXTE)
    lbl.pack()
    slider_qualite.configure(command=lambda v: lbl.configure(text=f"Qualité : {int(v)}"))
    make_label_editable(lbl, slider_qualite)

def _options_video_simple():
    """Options simples pour vidéos: un seul slider de qualité (converti en CRF)."""
    global slider_qualite
    ctk.CTkLabel(frame_options, text="Qualité (10-95)", font=("Arial", 12), text_color=COULEUR_TEXTE).pack(pady=(8, 0))
    slider_qualite = ctk.CTkSlider(frame_options, from_=10, to=95)
    slider_qualite.set(70)
    slider_qualite.pack(fill="x", padx=40, pady=4)
    lbl = ctk.CTkLabel(frame_options, text="Qualité : 70", text_color=COULEUR_TEXTE)
    lbl.pack()
    slider_qualite.configure(command=lambda v: lbl.configure(text=f"Qualité : {int(v)}"))
    make_label_editable(lbl, slider_qualite)

def _options_image_avance():
    """Options avancées pour images: qualité minimum, résolution, taille cible."""
    global slider_qualite, resolution_var, slider_taille

    ctk.CTkLabel(frame_options, text="Qualité minimum (10-95)", font=("Arial", 12), text_color=COULEUR_TEXTE).pack(pady=(8, 0))
    slider_qualite = ctk.CTkSlider(frame_options, from_=10, to=95)
    slider_qualite.set(30)
    slider_qualite.pack(fill="x", padx=40, pady=4)
    lbl_q = ctk.CTkLabel(frame_options, text="Qualité minimum : 30", text_color=COULEUR_TEXTE)
    lbl_q.pack()
    slider_qualite.configure(command=lambda v: lbl_q.configure(text=f"Qualité minimum : {int(v)}"))
    make_label_editable(lbl_q, slider_qualite)

    row1 = ctk.CTkFrame(frame_options, fg_color=COULEUR_BG)
    row1.pack(fill="x", padx=40, pady=(8, 0))
    ctk.CTkLabel(row1, text="Résolution", font=("Arial", 12), text_color=COULEUR_TEXTE).pack(side="left")
    resolution_var = ctk.CTkOptionMenu(row1,
        values=["Original", "1920x1080", "1280x720", "854x480", "640x360"], width=160,
        fg_color=COULEUR_CADRE, text_color=COULEUR_TEXTE)
    resolution_var.set("Original")
    resolution_var.pack(side="right")

    ctk.CTkLabel(frame_options, text="Taille cible (Mo)", font=("Arial", 12), text_color=COULEUR_TEXTE).pack(pady=(8, 0))
    slider_taille = ctk.CTkSlider(frame_options, from_=0.1, to=10)
    slider_taille.set(2.0)
    slider_taille.pack(fill="x", padx=40, pady=4)
    lbl_t = ctk.CTkLabel(frame_options, text="Taille cible : 2.0 Mo", text_color=COULEUR_TEXTE)
    lbl_t.pack()
    # Le label affiche directement la valeur du slider (pas de division)
    slider_taille.configure(command=lambda v: lbl_t.configure(text=f"Taille cible : {v:.1f} Mo"))
    make_label_editable(lbl_t, slider_taille)

def _options_video_avance():
    """Options avancées pour vidéos: résolution, FPS, bitrate personnalisé avec checkbox."""
    afficher_options_video_avance_avec_bitrate()

# ============================================================================
# COMPRESSION
# ============================================================================

def compresser():
    """Démarre la compression du fichier sélectionné."""
    if not fichier_selectionne:
        return

    sortie = filedialog.asksaveasfilename(
        defaultextension=(".jpg" if type_fichier == "image" else ".mp4"),
        filetypes=(
            [("JPEG", "*.jpg"), ("WebP", "*.webp")] if type_fichier == "image"
            else [("MP4 Video", "*.mp4")]
        )
    )
    if not sortie:
        return

    btn_compresser.configure(state="disabled", text="⏳  Compression en cours...")

    if type_fichier == "image":
        if mode_avance.get():
            executer_en_arriere_plan(lambda: _compresser_image_avance(sortie))
        else:
            executer_en_arriere_plan(lambda: _compresser_image_simple(sortie))
    elif type_fichier == "video":
        if mode_avance.get():
            executer_en_arriere_plan(lambda: _compresser_video_avance(sortie))
        else:
            executer_en_arriere_plan(lambda: _compresser_video_simple(sortie))

def _compresser_image_simple(sortie):
    """Compression d'image avec qualité simple (PIL, format JPEG/WebP)."""
    try:
        img = Image.open(fichier_selectionne)
        if img.mode in ("RGBA", "P") and sortie.lower().endswith(".jpg"):
            img = img.convert("RGB")
        img.save(sortie, quality=int(slider_qualite.get()), optimize=True)
        finaliser(fichier_selectionne, sortie)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))
    finally:
        fenetre.after(0, lambda: btn_compresser.configure(state="normal", text="✅  Compresser"))

def _compresser_image_avance(sortie):
    """Compression d'image avec taille cible et redimensionnement."""
    try:
        img = Image.open(fichier_selectionne)
        if img.mode in ("RGBA", "P") and sortie.lower().endswith(".jpg"):
            img = img.convert("RGB")

        res = resolution_var.get()
        if res != "Original":
            largeur, hauteur = map(int, res.split("x"))
            img = img.resize((largeur, hauteur), Image.LANCZOS)

        taille_cible_octets = slider_taille.get() * 1024 * 1024
        qualite_min = int(slider_qualite.get())
        qualite = 95
        img.save(sortie, quality=qualite, optimize=True)

        while os.path.getsize(sortie) > taille_cible_octets and qualite > qualite_min:
            qualite -= 5
            img.save(sortie, quality=qualite, optimize=True)

        finaliser(fichier_selectionne, sortie)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))
    finally:
        fenetre.after(0, lambda: btn_compresser.configure(state="normal", text="✅  Compresser"))

def _compresser_video_simple(sortie):
    """Compression vidéo avec qualité CRF (Constant Rate Factor)."""
    try:
        # qualite 95 → CRF ~0 (meilleure qualité)
        # qualite 10 → CRF ~46 (qualité basse)
        valeur_crf = int(51 - (slider_qualite.get() / 95) * 51)
        valeur_crf = max(0, min(51, valeur_crf))  # Sécurité: clamp entre 0 et 51
        commande = [
            str(FFMPEG_PATH), '-y', '-i', fichier_selectionne,
            '-vcodec', 'libx264', '-crf', str(valeur_crf),
            '-preset', 'fast', '-acodec', 'aac',
            '-pix_fmt', 'yuv420p', sortie
        ]
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        subprocess.run(commande, check=True, creationflags=flags)
        finaliser(fichier_selectionne, sortie)
    except FileNotFoundError:
        messagebox.showerror("Erreur", "FFmpeg non trouvé.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))
    finally:
        fenetre.after(0, lambda: btn_compresser.configure(state="normal", text="✅  Compresser"))

def _compresser_video_avance(sortie):
    """Compression vidéo avec bitrate personnalisé, résolution et FPS."""
    try:
        res = resolution_var.get()
        fps = fps_var.get()
        
        commande = [str(FFMPEG_PATH), '-y', '-i', fichier_selectionne]

        if res != "Original":
            largeur, hauteur = res.split("x")
            commande += ['-vf', f'scale={largeur}:{hauteur}']

        commande += ['-vcodec', 'libx264', '-preset', 'fast']

        if bitrate_personnalise and bitrate_personnalise.get():
            bitrate = int(slider_bitrate.get())
            commande += ['-b:v', f'{bitrate}k']
        else:
            commande += ['-crf', '23']  # Valeur CRF par défaut (bonne qualité)

        if fps != "Original":
            commande += ['-r', fps]

        commande += ['-acodec', 'aac', '-pix_fmt', 'yuv420p', sortie]

        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        subprocess.run(commande, check=True, creationflags=flags)
        finaliser(fichier_selectionne, sortie)
    except FileNotFoundError:
        messagebox.showerror("Erreur", "FFmpeg non trouvé.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))
    finally:
        fenetre.after(0, lambda: btn_compresser.configure(state="normal", text="✅  Compresser"))

def finaliser(avant, apres):
    """Affiche un message de confirmation avec les tailles avant/après compression."""
    t_avant = os.path.getsize(avant) // 1024
    t_apres = os.path.getsize(apres) // 1024
    messagebox.showinfo("Terminé", f"Succès !\nAvant : {t_avant} Ko\nAprès : {t_apres} Ko")

def on_toggle_mode():
    """
    Callback appelé quand l'utilisateur active/désactive le mode avancé.
    Recharge les options ET rafraîchit les infos vidéo pour afficher/masquer bitrate & FPS.
    """
    if fichier_selectionne:
        if type_fichier == "image":
            afficher_options_image()
        elif type_fichier == "video":
            afficher_options_video()
            afficher_infos_video(fichier_selectionne)

# ============================================================================
# CRÉATION DE L'INTERFACE GRAPHIQUE
# ============================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if TKINTERDND2_DISPONIBLE:
    fenetre = TkinterDnD.Tk()
else:
    fenetre = ctk.CTk()

fenetre.configure(bg=COULEUR_BG)
fenetre.title("L Compressor")

# Icône de l'application
icon_path = os.path.join(base_path, "..", "assets", "logo.png")

if platform.system() == "Windows":
    ico_path = os.path.join(base_path, "..", "assets", "logo.ico")
    if os.path.exists(ico_path):
        fenetre.iconbitmap(ico_path)
else:
    if os.path.exists(icon_path):
        icon_image = Image.open(icon_path)
        photo = ImageTk.PhotoImage(icon_image)
        fenetre.iconphoto(True, photo)

fenetre.geometry("570x750")
fenetre.minsize(460, 650)
fenetre.resizable(True, True)

main_container = ctk.CTkFrame(fenetre, fg_color=COULEUR_BG)
main_container.pack(fill="both", expand=True, padx=20, pady=15)

header = ctk.CTkFrame(main_container, fg_color=COULEUR_BG)
header.pack(fill="x", pady=(0, 10))
ctk.CTkLabel(header, text="Local Compressor", font=("Arial", 22, "bold"), text_color=COULEUR_TEXTE).pack(side="left")
mode_avance = ctk.BooleanVar(value=False)
ctk.CTkSwitch(header, text="Mode avancé", variable=mode_avance,
              command=on_toggle_mode).pack(side="right", pady=5)

btn_selection = ctk.CTkButton(main_container, text="📂  Sélectionner un fichier",
              command=selectionner_fichier, height=38,
              fg_color=COULEUR_CADRE, text_color=COULEUR_TEXTE,
              hover_color="#3A3A3A")
btn_selection.pack(fill="x", pady=(0, 8))

frame_preview = ctk.CTkFrame(main_container, fg_color=COULEUR_CADRE, corner_radius=8)
frame_preview.pack(fill="both", expand=True, pady=(0, 4))

if TKINTERDND2_DISPONIBLE:
    frame_preview.drop_target_register(DND_FILES)
    frame_preview.dnd_bind('<<Drop>>', on_drop)

label_drop = ctk.CTkLabel(frame_preview, text="Glissez un fichier ici ou cliquez pour sélectionner",
                          text_color=COULEUR_TEXTE_GRIS, font=("Arial", 13))
label_drop.pack(expand=True)

label_infos = ctk.CTkLabel(main_container, text="", font=("Arial", 11), text_color=COULEUR_TEXTE_GRIS)
label_infos.pack(pady=(2, 4))

ctk.CTkFrame(main_container, height=1, fg_color=COULEUR_CADRE).pack(fill="x", pady=2)

frame_options = ctk.CTkFrame(main_container, fg_color=COULEUR_BG)
frame_options.pack(fill="x", pady=2)

btn_compresser = ctk.CTkButton(main_container, text="✅  Compresser",
                                command=compresser, height=42,
                                state="disabled",
                                fg_color="#27ae60", hover_color="#1e8449",
                                text_color=COULEUR_TEXTE,
                                font=("Arial", 14, "bold"))

# Variables pour les options
slider_qualite = None
resolution_var = None
slider_taille = None
fps_var = None
slider_bitrate = None
label_bitrate = None
bitrate_personnalise = None
frame_bitrate = None

# ============================================================================
# BITRATE PERSONNALISÉ (CHECKBOX + SLIDER)
# ============================================================================

def afficher_options_video_avance_avec_bitrate():
    """
    Options avancées pour vidéos AVEC le choix du bitrate personnalisé.
    Inclut: sélecteur résolution, sélecteur FPS, checkbox bitrate, slider bitrate.
    """
    global resolution_var, fps_var, slider_bitrate, label_bitrate, frame_bitrate, bitrate_personnalise

    row1 = ctk.CTkFrame(frame_options, fg_color=COULEUR_BG)
    row1.pack(fill="x", padx=40, pady=(12, 0))
    ctk.CTkLabel(row1, text="Résolution", font=("Arial", 12), text_color=COULEUR_TEXTE).pack(side="left")
    resolution_var = ctk.CTkOptionMenu(row1,
        values=["Original", "1920x1080", "1280x720", "854x480", "640x360"], width=160,
        fg_color=COULEUR_CADRE, text_color=COULEUR_TEXTE)
    resolution_var.set("Original")
    resolution_var.pack(side="right")

    row2 = ctk.CTkFrame(frame_options, fg_color=COULEUR_BG)
    row2.pack(fill="x", padx=40, pady=(8, 0))
    ctk.CTkLabel(row2, text="FPS", font=("Arial", 12), text_color=COULEUR_TEXTE).pack(side="left")
    fps_var = ctk.CTkOptionMenu(row2, values=["Original", "60", "30", "24"], width=160,
        fg_color=COULEUR_CADRE, text_color=COULEUR_TEXTE)
    fps_var.set("Original")
    fps_var.pack(side="right")

    row3 = ctk.CTkFrame(frame_options, fg_color=COULEUR_BG)
    row3.pack(fill="x", padx=40, pady=(12, 0))
    bitrate_personnalise = ctk.BooleanVar(value=False)
    ctk.CTkCheckBox(row3, text="Bitrate personnalisé", variable=bitrate_personnalise,
                   text_color=COULEUR_TEXTE, fg_color=COULEUR_CADRE).pack(side="left")
    
    frame_bitrate = ctk.CTkFrame(frame_options, fg_color=COULEUR_BG)
    
    def toggle_bitrate_slider():
        """Affiche ou cache le slider de bitrate selon l'état de la checkbox."""
        if bitrate_personnalise.get():
            frame_bitrate.pack(fill="x", pady=(4, 0))
        else:
            frame_bitrate.pack_forget()
    
    ctk.CTkLabel(frame_bitrate, text="Bitrate vidéo (kbps)", font=("Arial", 12), text_color=COULEUR_TEXTE).pack(pady=(12, 0))
    slider_bitrate = ctk.CTkSlider(frame_bitrate, from_=250, to=8000)
    slider_bitrate.set(2000)
    slider_bitrate.pack(fill="x", padx=40, pady=4)
    label_bitrate = ctk.CTkLabel(frame_bitrate, text="Bitrate : 2000 kbps", text_color=COULEUR_TEXTE)
    label_bitrate.pack()
    slider_bitrate.configure(command=lambda v: label_bitrate.configure(text=f"Bitrate : {int(v)} kbps"))
    make_label_editable(label_bitrate, slider_bitrate)
    
    bitrate_personnalise.trace("w", lambda *args: toggle_bitrate_slider())
    frame_bitrate.pack_forget()

# ============================================================================
# ÉDITION PAR DOUBLE-CLIC
# ============================================================================

def make_label_editable(label_widget, slider_widget):
    """
    Rend un label éditable en double-cliquant dessus.
    Ouvre une boîte de dialogue pour entrer la nouvelle valeur.
    """
    def on_label_click(event=None):
        try:
            from tkinter import simpledialog
            nouvelle_valeur = simpledialog.askfloat(
                "Éditer valeur",
                f"Entrez la nouvelle valeur:\n(Plage: {slider_widget.cget('from_')} - {slider_widget.cget('to')})"
            )
            
            if nouvelle_valeur is not None:
                val_min = float(slider_widget.cget('from_'))
                val_max = float(slider_widget.cget('to'))
                
                if val_min <= nouvelle_valeur <= val_max:
                    slider_widget.set(nouvelle_valeur)
                else:
                    messagebox.showerror("Erreur", f"Veuillez entrer une valeur entre {val_min} et {val_max}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Valeur invalide: {str(e)}")
    
    label_widget.bind("<Double-Button-1>", on_label_click)
    label_widget.configure(cursor="hand2")

# ============================================================================
# LANCEMENT DE L'APPLICATION
# ============================================================================

fenetre.mainloop()