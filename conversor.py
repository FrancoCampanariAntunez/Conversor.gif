import imageio_ffmpeg
import subprocess


ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()


def convertir_a_gif(archivo, salida, ancho, alto, velocidad, fps, colores=256):

    subprocess.run([
        ffmpeg,
        "-i", archivo,
        "-filter_complex",
        f"[0:v]"
        f"setpts={1 / velocidad}*PTS,"
        f"fps={fps},"
        f"scale={ancho}:{alto},"
        f"split[a][b];"
        f"[a]palettegen=max_colors={colores}[p];"
        "[b][p]paletteuse=dither=none",
        "-gifflags", "-offsetting-transdiff",
        "-loop", "0",
        salida
    ], check=True, creationflags=subprocess.CREATE_NO_WINDOW)