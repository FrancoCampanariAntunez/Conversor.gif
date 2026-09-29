import imageio_ffmpeg
import subprocess
import re


ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()


def obtener_propiedades(archivo):

    resultado = subprocess.run(
        [ffmpeg, "-i", archivo],
        capture_output=True,
        text=True
    )

    informacion = resultado.stderr


    # -------------------------
    # BUSCAR RESOLUCIÓN
    # -------------------------

    resolucion = re.search(
        r"Video:.*?(\d{2,5})x(\d{2,5})",
        informacion
    )

    if resolucion:

        ancho = int(resolucion.group(1))
        alto = int(resolucion.group(2))

    else:

        ancho = None
        alto = None


    # -------------------------
    # BUSCAR FPS
    # -------------------------

    fps = re.search(
        r"(\d+(?:\.\d+)?) fps",
        informacion
    )

    if fps:

        fps = float(fps.group(1))

    else:

        fps = None


    # -------------------------
    # BUSCAR DURACIÓN
    # -------------------------

    duracion = re.search(
        r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)",
        informacion
    )

    if duracion:

        horas = int(duracion.group(1))
        minutos = int(duracion.group(2))
        segundos = float(duracion.group(3))

        duracion_total = (
            horas * 3600
            + minutos * 60
            + segundos
        )

    else:

        duracion_total = None


    return ancho, alto, fps, duracion_total


def obtener_resoluciones(archivos):

    resoluciones = [
        "100%",
        "75%",
        "50%"
    ]


    # Solo mostramos las resoluciones cuadradas
    # si hay archivos seleccionados y TODOS son cuadrados.

    todos_son_cuadrados = (
        bool(archivos)
        and all(
            dato["ancho"] == dato["alto"]
            for dato in archivos
        )
    )


    if todos_son_cuadrados:

        resoluciones.extend([
            "112x112",
            "300x300",
            "500x500",
            "750x750"
        ])


    return resoluciones


def calcular_resolucion(
    ancho,
    alto,
    resolucion,
    personalizada=None
):

    # Resolución personalizada
    if personalizada:

        return personalizada


    # 100% = tamaño original
    if resolucion == "100%":

        return ancho, alto


    # 75% = 75% del tamaño original
    if resolucion == "75%":

        return (
            round(ancho * 0.75),
            round(alto * 0.75)
        )


    # 50% = 50% del tamaño original
    if resolucion == "50%":

        return (
            round(ancho * 0.50),
            round(alto * 0.50)
        )


    # Resoluciones cuadradas
    if resolucion == "112x112":

        return 112, 112


    if resolucion == "300x300":

        return 300, 300


    if resolucion == "500x500":

        return 500, 500


    if resolucion == "750x750":

        return 750, 750


    # Por seguridad, si llega una opción desconocida,
    # mantenemos la resolución original.

    return ancho, alto