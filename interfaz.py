import tkinter as tk
import os
from tkinter import filedialog
from tkinter import messagebox

from conversor import convertir_a_gif
from propiedades import (
    obtener_propiedades,
    obtener_resoluciones,
    calcular_resolucion
)


# -------------------------
# COLORES
# -------------------------

COLOR_FONDO = "#fff7fb"
COLOR_ROSA = "#f43f7f"
COLOR_ROSA_CLARO = "#f7bfd2"
COLOR_TEXTO = "#292929"
COLOR_BLANCO = "#ffffff"


# -------------------------
# DATOS
# -------------------------

archivos_seleccionados = []
carpeta_destino = None

velocidades = {
    "100%": 1,
    "150%": 1.5,
    "200%": 2
}

velocidades_seleccionadas = {}
resoluciones_seleccionadas = {}


# -------------------------
# VENTANA
# -------------------------

ventana = tk.Tk()
ventana.title("Conversor de GIF")
ventana.geometry("700x850")
ventana.configure(bg=COLOR_FONDO)

fps_seleccionado = tk.IntVar(value=30)
colores_seleccionados = tk.IntVar(value=256)


# -------------------------
# FUNCIONES
# -------------------------

def seleccionar_archivo():

    archivos = filedialog.askopenfilenames(
        filetypes=[("Archivos MOV", "*.mov")]
    )

    for archivo in archivos:

        rutas_existentes = [
            dato["ruta"] for dato in archivos_seleccionados
        ]

        # Evita agregar dos veces el mismo archivo
        if archivo in rutas_existentes:
            continue

        ancho, alto, fps, duracion = obtener_propiedades(archivo)

        datos = {
            "ruta": archivo,
            "ancho": ancho,
            "alto": alto,
            "fps": fps,
            "duracion": duracion
        }

        archivos_seleccionados.append(datos)

        crear_fila_archivo(archivo)

    actualizar_resoluciones()


def crear_fila_archivo(archivo):

    fila = tk.Frame(
        contenedor_archivos,
        bg=COLOR_BLANCO
    )

    fila.pack(
        fill="x",
        padx=10,
        pady=3
    )

    nombre = tk.Label(
        fila,
        text=os.path.basename(archivo),
        bg=COLOR_BLANCO,
        fg=COLOR_TEXTO,
        font=("Segoe UI", 10)
    )

    nombre.pack(
        side="left",
        padx=10,
        pady=6
    )

    boton_eliminar = tk.Button(
        fila,
        text="×",
        command=lambda: eliminar_archivo(archivo, fila),
        bg=COLOR_BLANCO,
        fg=COLOR_ROSA,
        activebackground=COLOR_ROSA_CLARO,
        activeforeground=COLOR_ROSA,
        relief="flat",
        bd=0,
        font=("Segoe UI", 14, "bold"),
        cursor="hand2"
    )

    boton_eliminar.pack(
        side="right",
        padx=10
    )


def eliminar_archivo(archivo, fila):

    for dato in archivos_seleccionados:

        if dato["ruta"] == archivo:
            archivos_seleccionados.remove(dato)
            break

    fila.destroy()

    actualizar_resoluciones()


def actualizar_resoluciones():

    opciones = obtener_resoluciones(
        archivos_seleccionados
    )

    # Guardamos las selecciones que siguen siendo válidas
    selecciones_anteriores = {
        nombre
        for nombre, variable in resoluciones_seleccionadas.items()
        if variable.get()
    }

    # Eliminamos los Checkbuttons anteriores
    for widget in contenedor_resoluciones.winfo_children():
        widget.destroy()

    resoluciones_seleccionadas.clear()

    # Creamos nuevamente los Checkbuttons
    for i, opcion in enumerate(opciones):

        variable = tk.BooleanVar(
            value=opcion in selecciones_anteriores
        )

        checkbox = tk.Checkbutton(
            contenedor_resoluciones,
            text=opcion,
            variable=variable,
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            activebackground=COLOR_BLANCO,
            activeforeground=COLOR_ROSA,
            selectcolor=COLOR_ROSA_CLARO,
            font=("Segoe UI", 10),
            cursor="hand2"
        )

        fila = i // 4
        columna = i % 4

        checkbox.grid(
            row=fila,
            column=columna,
            padx=15,
            pady=2,
            sticky="w"
        )

        resoluciones_seleccionadas[opcion] = variable


def validar_resolucion_personalizada():

    try:

        ancho = int(entrada_ancho.get())
        alto = int(entrada_alto.get())

        if ancho <= 0 or alto <= 0:
            raise ValueError

        return ancho, alto

    except ValueError:

        return None


def obtener_nombre_resolucion(resolucion):

    if resolucion == "100%":
        return "original"

    return resolucion.replace("%", "")


def obtener_salida(archivo, velocidad_nombre, resolucion_nombre):

    nombre = os.path.splitext(
        os.path.basename(archivo)
    )[0]

    resolucion_nombre = obtener_nombre_resolucion(
        resolucion_nombre
    )

    base = (
        f"{nombre}_"
        f"{velocidad_nombre.replace('%', '')}_"
        f"{resolucion_nombre}"
    )

    salida = os.path.join(
        carpeta_destino,
        base + ".gif"
    )

    contador = 2

    while os.path.exists(salida):

        salida = os.path.join(
            carpeta_destino,
            f"{base}_{contador}.gif"
        )

        contador += 1

    return salida


def convertir_archivos():

    # -------------------------
    # VALIDAR ARCHIVOS
    # -------------------------

    if not archivos_seleccionados:

        messagebox.showwarning(
            "Sin archivos",
            "Seleccioná al menos un archivo MOV."
        )

        return


    # -------------------------
    # VALIDAR CARPETA
    # -------------------------

    if carpeta_destino is None:

        messagebox.showwarning(
            "Sin carpeta",
            "Seleccioná una carpeta de destino."
        )

        return


    # -------------------------
    # OBTENER VELOCIDADES
    # -------------------------

    velocidades_elegidas = [
        nombre
        for nombre, variable
        in velocidades_seleccionadas.items()
        if variable.get()
    ]

    if not velocidades_elegidas:

        messagebox.showwarning(
            "Sin velocidad",
            "Seleccioná al menos una velocidad."
        )

        return


    # -------------------------
    # OBTENER RESOLUCIONES
    # -------------------------

    resoluciones_elegidas = [
        nombre
        for nombre, variable
        in resoluciones_seleccionadas.items()
        if variable.get()
    ]


    # -------------------------
    # RESOLUCIÓN PERSONALIZADA
    # -------------------------

    personalizada = personalizada_seleccionada.get()

    resolucion_personalizada = None

    if personalizada:

        resolucion_personalizada = (
            validar_resolucion_personalizada()
        )

        if resolucion_personalizada is None:

            messagebox.showwarning(
                "Resolución inválida",
                "La resolución personalizada debe tener "
                "un ancho y un alto mayores que 0."
            )

            return

    if not resoluciones_elegidas and not personalizada:

        messagebox.showwarning(
            "Sin resolución",
            "Seleccioná al menos una resolución."
        )

        return

    cantidad_total = (
        len(archivos_seleccionados)
        * (len(resoluciones_elegidas) + (1 if personalizada else 0))
        * len(velocidades_elegidas)
    )

    cantidad_actual = 0

    boton_convertir.config(
        state="disabled"
    )

    etiqueta_progreso.config(
        text=f"Preparando {cantidad_total} archivo(s)..."
    )

    barra_progreso.place(
        relwidth=0
    )

    ventana.update_idletasks()


    # -------------------------
    # CONVERSIÓN
    # -------------------------

    cantidad = 0

    for dato in archivos_seleccionados:

        # Resoluciones predefinidas
        for resolucion_nombre in resoluciones_elegidas:

            ancho, alto = calcular_resolucion(
                dato["ancho"],
                dato["alto"],
                resolucion_nombre
            )

            for velocidad_nombre in velocidades_elegidas:

                velocidad_valor = velocidades[
                    velocidad_nombre
                ]

                salida = obtener_salida(
                    dato["ruta"],
                    velocidad_nombre,
                    resolucion_nombre
                )

                etiqueta_progreso.config(
                    text=f"Exportando {cantidad_actual + 1} de {cantidad_total}..."
                )

                ventana.update_idletasks()

                convertir_a_gif(
                    dato["ruta"],
                    salida,
                    ancho,
                    alto,
                    velocidad_valor,
                    fps_seleccionado.get(),
                    colores_seleccionados.get()
                )

                cantidad_actual += 1

                barra_progreso.place(
                    relwidth=cantidad_actual / cantidad_total
                )

                etiqueta_progreso.config(
                    text=f"Exportando {cantidad_actual} de {cantidad_total}..."
                )

                ventana.update_idletasks()

                cantidad += 1


        # Resolución personalizada
        if personalizada:

            ancho, alto = resolucion_personalizada

            nombre_personalizado = (
                f"{ancho}x{alto}"
            )

            for velocidad_nombre in velocidades_elegidas:

                velocidad_valor = velocidades[
                    velocidad_nombre
                ]

                salida = obtener_salida(
                    dato["ruta"],
                    velocidad_nombre,
                    nombre_personalizado
                )

                etiqueta_progreso.config(
                    text=f"Exportando {cantidad_actual + 1} de {cantidad_total}..."
                )

                ventana.update_idletasks()

                convertir_a_gif(
                    dato["ruta"],
                    salida,
                    ancho,
                    alto,
                    velocidad_valor,
                    fps_seleccionado.get(),
                    colores_seleccionados.get()
                )

                cantidad_actual += 1

                barra_progreso.place(
                    relwidth=cantidad_actual / cantidad_total
                )

                etiqueta_progreso.config(
                    text=f"Exportando {cantidad_actual} de {cantidad_total}..."
                )

                ventana.update_idletasks()

                cantidad += 1


    messagebox.showinfo(
        "Conversión terminada",
        f"Se generaron {cantidad} GIF(s) correctamente."
    )
    etiqueta_progreso.config(
        text=f"✓ Conversión completada — {cantidad} GIF(s)"
    )

    barra_progreso.place(
        relwidth=1
    )

    boton_convertir.config(
        state="normal"
    )

    ventana.update_idletasks()

def seleccionar_carpeta():

    global carpeta_destino

    carpeta = filedialog.askdirectory()

    if carpeta:

        carpeta_destino = carpeta

        etiqueta_carpeta.config(
            text=carpeta,
            fg=COLOR_TEXTO
        )


# -------------------------
# ESTILO
# -------------------------


# -------------------------
# TÍTULO
# -------------------------

titulo = tk.Label(
    ventana,
    text="▣  Conversor de GIF",
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO,
    font=("Segoe UI", 24, "bold")
)

titulo.pack(
    pady=(25, 25)
)


# -------------------------
# ARCHIVOS
# -------------------------

etiqueta_archivos = tk.Label(
    ventana,
    text="📁  Archivos seleccionados",
    bg=COLOR_FONDO,
    fg=COLOR_ROSA,
    font=("Segoe UI", 12, "bold")
)

etiqueta_archivos.pack(
    anchor="w",
    padx=45
)


contenedor_archivos = tk.Frame(
    ventana,
    bg=COLOR_BLANCO,
    highlightbackground=COLOR_ROSA_CLARO,
    highlightthickness=1
)

contenedor_archivos.pack(
    fill="x",
    padx=45,
    pady=(8, 12)
)


boton_archivo = tk.Button(
    ventana,
    text="📁  Seleccionar archivos",
    command=seleccionar_archivo,
    bg=COLOR_BLANCO,
    fg=COLOR_ROSA,
    activebackground=COLOR_ROSA_CLARO,
    activeforeground=COLOR_ROSA,
    relief="solid",
    bd=1,
    font=("Segoe UI", 10, "bold"),
    padx=15,
    pady=7,
    cursor="hand2"
)

boton_archivo.pack(
    pady=(0, 25)
)


# -------------------------
# RESOLUCIÓN
# -------------------------

etiqueta_resolucion = tk.Label(
    ventana,
    text="↗  Resolución",
    bg=COLOR_FONDO,
    fg=COLOR_ROSA,
    font=("Segoe UI", 12, "bold")
)

etiqueta_resolucion.pack(
    anchor="w",
    padx=45
)


contenedor_resoluciones = tk.Frame(
    ventana,
    bg=COLOR_BLANCO,
    highlightbackground=COLOR_ROSA_CLARO,
    highlightthickness=1
)

contenedor_resoluciones.pack(
    fill="x",
    padx=45,
    pady=(8, 10)
)


# -------------------------
# PERSONALIZADA
# -------------------------

personalizada_seleccionada = tk.BooleanVar(
    value=False
)


checkbox_personalizada = tk.Checkbutton(
    ventana,
    text="Usar resolución personalizada",
    variable=personalizada_seleccionada,
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO,
    activebackground=COLOR_FONDO,
    activeforeground=COLOR_ROSA,
    selectcolor=COLOR_ROSA_CLARO,
    font=("Segoe UI", 10, "bold"),
    cursor="hand2"
)

checkbox_personalizada.pack(
    anchor="w",
    padx=45,
    pady=(5, 5)
)


contenedor_personalizada = tk.Frame(
    ventana,
    bg=COLOR_FONDO
)

contenedor_personalizada.pack(
    pady=(0, 20)
)


etiqueta_ancho = tk.Label(
    contenedor_personalizada,
    text="Ancho:",
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO,
    font=("Segoe UI", 9)
)

etiqueta_ancho.grid(
    row=0,
    column=0,
    sticky="w"
)


etiqueta_alto = tk.Label(
    contenedor_personalizada,
    text="Alto:",
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO,
    font=("Segoe UI", 9)
)

etiqueta_alto.grid(
    row=0,
    column=1,
    sticky="w",
    padx=(15, 0)
)


entrada_ancho = tk.Entry(
    contenedor_personalizada,
    width=15,
    font=("Segoe UI", 10),
    relief="solid",
    bd=1
)

entrada_ancho.grid(
    row=1,
    column=0,
    pady=(3, 8)
)


entrada_alto = tk.Entry(
    contenedor_personalizada,
    width=15,
    font=("Segoe UI", 10),
    relief="solid",
    bd=1
)

entrada_alto.grid(
    row=1,
    column=1,
    padx=(15, 0),
    pady=(3, 8)
)


# -------------------------
# VELOCIDAD
# -------------------------

etiqueta_velocidad = tk.Label(
    ventana,
    text="◷  Velocidad",
    bg=COLOR_FONDO,
    fg=COLOR_ROSA,
    font=("Segoe UI", 12, "bold")
)

etiqueta_velocidad.pack(
    anchor="w",
    padx=45
)


contenedor_velocidades = tk.Frame(
    ventana,
    bg=COLOR_BLANCO,
    highlightbackground=COLOR_ROSA_CLARO,
    highlightthickness=1
)

contenedor_velocidades.pack(
    fill="x",
    padx=45,
    pady=(8, 25)
)


for i, nombre in enumerate(velocidades):

    variable = tk.BooleanVar(
        value=False
    )

    checkbox = tk.Checkbutton(
        contenedor_velocidades,
        text=nombre,
        variable=variable,
        bg=COLOR_BLANCO,
        fg=COLOR_TEXTO,
        activebackground=COLOR_BLANCO,
        activeforeground=COLOR_ROSA,
        selectcolor=COLOR_ROSA_CLARO,
        font=("Segoe UI", 10),
        cursor="hand2"
    )

    checkbox.grid(
        row=0,
        column=i,
        padx=15,
        pady=2,
        sticky="w"
    )

    velocidades_seleccionadas[nombre] = variable

# -------------------------
# FPS
# -------------------------

etiqueta_fps = tk.Label(
    ventana,
    text="◉  FPS",
    bg=COLOR_FONDO,
    fg=COLOR_ROSA,
    font=("Segoe UI", 12, "bold")
)

etiqueta_fps.pack(
    anchor="w",
    padx=45
)


contenedor_fps = tk.Frame(
    ventana,
    bg=COLOR_BLANCO,
    highlightbackground=COLOR_ROSA_CLARO,
    highlightthickness=1
)

contenedor_fps.pack(
    fill="x",
    padx=45,
    pady=(8, 25)
)


for i, fps in enumerate([25, 30, 60]):

    radio = tk.Radiobutton(
        contenedor_fps,
        text=f"{fps} FPS",
        variable=fps_seleccionado,
        value=fps,
        bg=COLOR_BLANCO,
        fg=COLOR_TEXTO,
        activebackground=COLOR_BLANCO,
        activeforeground=COLOR_ROSA,
        selectcolor=COLOR_ROSA_CLARO,
        font=("Segoe UI", 10),
        cursor="hand2"
    )

    radio.grid(
        row=0,
        column=i,
        padx=15,
        pady=2,
        sticky="w"
    )

# -------------------------
# CALIDAD DE COLOR
# -------------------------

etiqueta_colores = tk.Label(
    ventana,
    text="🎨  Calidad de color",
    bg=COLOR_FONDO,
    fg=COLOR_ROSA,
    font=("Segoe UI", 12, "bold")
)

etiqueta_colores.pack(
    anchor="w",
    padx=45
)


contenedor_colores = tk.Frame(
    ventana,
    bg=COLOR_BLANCO,
    highlightbackground=COLOR_ROSA_CLARO,
    highlightthickness=1
)

contenedor_colores.pack(
    fill="x",
    padx=45,
    pady=(8, 5)
)


opciones_colores = [
    ("256 (máxima)", 256),
    ("192 (alta)", 192),
    ("128 (media)", 128),
    ("64 (liviana)", 64),
]

for i, (texto, valor) in enumerate(opciones_colores):

    radio = tk.Radiobutton(
        contenedor_colores,
        text=texto,
        variable=colores_seleccionados,
        value=valor,
        bg=COLOR_BLANCO,
        fg=COLOR_TEXTO,
        activebackground=COLOR_BLANCO,
        activeforeground=COLOR_ROSA,
        selectcolor=COLOR_ROSA_CLARO,
        font=("Segoe UI", 10),
        cursor="hand2"
    )

    radio.grid(
        row=0,
        column=i,
        padx=15,
        pady=2,
        sticky="w"
    )

etiqueta_ayuda_colores = tk.Label(
    ventana,
    text="Menos colores = menor peso. Si no se nota diferencia visual, conviene bajar.",
    bg=COLOR_FONDO,
    fg="#777777",
    font=("Segoe UI", 8)
)

etiqueta_ayuda_colores.pack(
    anchor="w",
    padx=45,
    pady=(0, 20)
)

# -------------------------
# CARPETA DE DESTINO
# -------------------------

etiqueta_destino = tk.Label(
    ventana,
    text="📁  Carpeta de destino",
    bg=COLOR_FONDO,
    fg=COLOR_ROSA,
    font=("Segoe UI", 12, "bold")
)

etiqueta_destino.pack(
    anchor="w",
    padx=45
)


contenedor_destino = tk.Frame(
    ventana,
    bg=COLOR_FONDO
)

contenedor_destino.pack(
    fill="x",
    padx=45,
    pady=(8, 20)
)


etiqueta_carpeta = tk.Label(
    contenedor_destino,
    text="Ninguna carpeta seleccionada",
    bg=COLOR_BLANCO,
    fg="#777777",
    anchor="w",
    relief="solid",
    bd=1,
    padx=10,
    pady=8
)

etiqueta_carpeta.pack(
    side="left",
    fill="x",
    expand=True
)


boton_carpeta = tk.Button(
    contenedor_destino,
    text="📁  Seleccionar carpeta",
    command=seleccionar_carpeta,
    bg=COLOR_BLANCO,
    fg=COLOR_ROSA,
    activebackground=COLOR_ROSA_CLARO,
    activeforeground=COLOR_ROSA,
    relief="solid",
    bd=1,
    font=("Segoe UI", 9, "bold"),
    padx=10,
    pady=6,
    cursor="hand2"
)

boton_carpeta.pack(
    side="right",
    padx=(10, 0)
)



# -------------------------
# CONVERTIR
# -------------------------

boton_convertir = tk.Button(
    ventana,
    text="✨  CONVERTIR",
    command=convertir_archivos,
    bg=COLOR_ROSA,
    fg=COLOR_BLANCO,
    activebackground="#e83270",
    activeforeground=COLOR_BLANCO,
    relief="flat",
    bd=0,
    font=("Segoe UI", 13, "bold"),
    padx=35,
    pady=12,
    cursor="hand2"
)

boton_convertir.pack(
    pady=(0, 15)
)
# -------------------------
# PROGRESO
# -------------------------

etiqueta_progreso = tk.Label(
    ventana,
    text="",
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO,
    font=("Segoe UI", 9)
)

etiqueta_progreso.pack(
    pady=(0, 5)
)


contenedor_progreso = tk.Frame(
    ventana,
    bg=COLOR_ROSA_CLARO,
    height=8
)

contenedor_progreso.pack(
    fill="x",
    padx=45,
    pady=(0, 15)
)

contenedor_progreso.pack_propagate(False)


barra_progreso = tk.Frame(
    contenedor_progreso,
    bg=COLOR_ROSA
)

barra_progreso.place(
    x=0,
    y=0,
    relheight=1,
    relwidth=0
)

# -------------------------
# INFORMACIÓN
# -------------------------

separador = tk.Frame(
    ventana,
    bg=COLOR_ROSA_CLARO,
    height=1
)

separador.pack(
    fill="x",
    padx=45
)


etiqueta_info = tk.Label(
    ventana,
    text="ⓘ  Los archivos convertidos se guardarán en la carpeta seleccionada.",
    bg=COLOR_FONDO,
    fg="#777777",
    font=("Segoe UI", 9)
)

etiqueta_info.pack(
    pady=12
)


# -------------------------
# INICIAR
# -------------------------

def iniciar_interfaz():
    ventana.mainloop()