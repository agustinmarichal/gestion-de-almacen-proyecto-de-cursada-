"""Interfaz del kiosco (CustomTkinter).

Usa las funciones del backend de kiosco.py sin modificarlas.
Los dos archivos tienen que estar en la misma carpeta.

Instalación (una sola vez):  pip install customtkinter
Ejecución:                   python interfaz_kiosco.py
"""
from datetime import date

import customtkinter as ctk

from kiosco import (
    kiosco,
    agregar_producto,
    buscar_producto,
    buscar_por_nombre,
    actualizar_stock,
    registrar_venta,
    productos_con_stock_bajo,
    cierre_de_caja,
)

# ----------------------------------------------------------------------
# TEMA (centralizado: para reutilizar la identidad en otro proyecto,
# alcanza con copiar este bloque y los helpers de abajo)
# ----------------------------------------------------------------------
TEMA = {
    "fondo": "#1e1f26",
    "panel": "#2a2c36",
    "borde": "#3a3d4a",
    "acento": "#3b82f6",
    "acento_hover": "#2563eb",
    "ok": "#22c55e",
    "error": "#ef4444",
    "aviso": "#f59e0b",
    "texto": "#e5e7eb",
    "texto_suave": "#9ca3af",
}
FUENTE = "Segoe UI"
FUENTE_TABLA = "Consolas"

MEDIOS_DE_PAGO = ["efectivo", "transferencia", "tarjeta"]

ERRORES_VENTA = {
    "datos_invalidos": "La venta tiene datos inválidos.",
    "codigo_inexistente": "Hay un código que no existe en el catálogo.",
    "stock_insuficiente": "No alcanza el stock para algún producto.",
}

ctk.set_appearance_mode("dark")


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------
def plata(importe):
    """1234.5 -> $1.234,50 (formato argentino)."""
    texto = f"{importe:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"${texto}"


def a_numero(texto, tipo=float):
    """Convierte texto a número aceptando coma decimal. Lanza ValueError si no se puede."""
    return tipo(texto.strip().replace(",", "."))


def texto_vencimiento(vencimiento):
    """'2026-12-15' -> ('15/12/2026', aviso), donde aviso puede ser '', '2d' (vence en
    1 a 3 días), 'HOY' o 'VENCIDO'. Sin fecha devuelve ('-', ''). Si la fecha no se
    puede interpretar, la muestra tal cual y sin aviso."""
    if not vencimiento:
        return "-", ""
    try:
        fecha = date.fromisoformat(vencimiento)
    except ValueError:
        return str(vencimiento), ""
    dias = (fecha - date.today()).days
    if dias < 0:
        aviso = "VENCIDO"
    elif dias == 0:
        aviso = "HOY"
    elif dias <= 3:
        aviso = f"{dias}d"
    else:
        aviso = ""
    return fecha.strftime("%d/%m/%Y"), aviso


def escribir(caja, texto):
    """Reemplaza el contenido de un CTkTextbox de solo lectura."""
    caja.configure(state="normal")
    caja.delete("1.0", "end")
    caja.insert("1.0", texto)
    caja.configure(state="disabled")


def boton(master, texto, comando, secundario=False):
    if secundario:
        return ctk.CTkButton(
            master, text=texto, command=comando,
            fg_color=TEMA["panel"], hover_color=TEMA["borde"], text_color=TEMA["texto"],
        )
    return ctk.CTkButton(
        master, text=texto, command=comando,
        fg_color=TEMA["acento"], hover_color=TEMA["acento_hover"],
    )


def caja_de_texto(master):
    return ctk.CTkTextbox(
        master, font=(FUENTE_TABLA, 14), state="disabled",
        fg_color=TEMA["panel"], text_color=TEMA["texto"],
    )


def subtitulo(master, texto):
    return ctk.CTkLabel(
        master, text=texto, font=(FUENTE, 14, "bold"), text_color=TEMA["texto_suave"]
    )


# ----------------------------------------------------------------------
# PANTALLA BASE
# ----------------------------------------------------------------------
class Pantalla(ctk.CTkFrame):
    def __init__(self, master, titulo):
        super().__init__(master, fg_color=TEMA["fondo"], corner_radius=0)
        ctk.CTkLabel(
            self, text=titulo, font=(FUENTE, 24, "bold"), text_color=TEMA["texto"]
        ).pack(anchor="w", padx=24, pady=(20, 8))
        self.estado = ctk.CTkLabel(self, text="", font=(FUENTE, 13))
        self.estado.pack(side="bottom", anchor="w", padx=24, pady=10)

    def mensaje(self, texto, tipo="ok"):
        self.estado.configure(text=texto, text_color=TEMA[tipo])

    def actualizar(self):
        """Se llama cada vez que se entra a la pantalla."""


# ----------------------------------------------------------------------
# VENTAS
# ----------------------------------------------------------------------
class PantallaVentas(Pantalla):
    def __init__(self, master):
        super().__init__(master, "Ventas")
        self.carrito = {}  # codigo -> cantidad

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", padx=24, pady=(0, 12))

        self.codigo = ctk.CTkEntry(fila, placeholder_text="Código o nombre (o escaneá)", width=260)
        self.codigo.pack(side="left", padx=(0, 8))
        self.cantidad = ctk.CTkEntry(fila, width=70)
        self.cantidad.insert(0, "1")
        self.cantidad.pack(side="left", padx=(0, 8))
        boton(fila, "Agregar", self.agregar).pack(side="left")

        # El lector de código de barras escribe el código y manda Enter
        self.codigo.bind("<Return>", lambda e: self.agregar())
        self.cantidad.bind("<Return>", lambda e: self.agregar())
        self.codigo.bind("<Escape>", lambda e: self.ocultar_sugerencias())

        # Panel de coincidencias por nombre: queda oculto hasta que haga falta elegir
        self.sugerencias = ctk.CTkFrame(self, fg_color=TEMA["panel"])

        self.detalle = caja_de_texto(self)
        self.detalle.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        self.total = ctk.CTkLabel(
            self, text="Total: $0,00", font=(FUENTE, 22, "bold"), text_color=TEMA["texto"]
        )
        self.total.pack(anchor="e", padx=24)

        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(fill="x", padx=24, pady=(8, 0))
        self.medio = ctk.CTkOptionMenu(
            pie, values=MEDIOS_DE_PAGO,
            fg_color=TEMA["panel"], button_color=TEMA["acento"],
            button_hover_color=TEMA["acento_hover"],
        )
        self.medio.pack(side="left")
        boton(pie, "Cobrar", self.cobrar).pack(side="right")
        boton(pie, "Vaciar carrito", self.vaciar, secundario=True).pack(side="right", padx=8)

    def actualizar(self):
        self.ocultar_sugerencias()
        self.redibujar()
        self.codigo.focus()

    def agregar(self):
        """Busca primero por código exacto (lo que manda el lector) y, si no
        existe, por nombre."""
        texto = self.codigo.get().strip()
        if not texto:
            self.mensaje("Escribí un código o un nombre.", "aviso")
            return

        if buscar_producto(texto) is not None:
            self.agregar_codigo(texto)
            return

        coincidencias = buscar_por_nombre(texto)  # [(codigo, producto), ...]
        if not coincidencias:
            self.ocultar_sugerencias()
            self.mensaje("No existe un producto con ese código ni con ese nombre.", "error")
        elif len(coincidencias) == 1:
            self.agregar_codigo(coincidencias[0][0])
        else:
            self.mostrar_sugerencias(coincidencias)

    MAX_SUGERENCIAS = 6

    def mostrar_sugerencias(self, coincidencias):
        self.ocultar_sugerencias()
        ctk.CTkLabel(
            self.sugerencias, text="Varios productos coinciden, elegí uno (Esc para cancelar):",
            font=(FUENTE, 13), text_color=TEMA["texto_suave"],
        ).pack(anchor="w", padx=12, pady=(8, 2))
        for codigo, p in coincidencias[: self.MAX_SUGERENCIAS]:
            ctk.CTkButton(
                self.sugerencias, anchor="w", height=30,
                text=f"{p['nombre']}   ·   {plata(p['precio'])}   ·   stock {p['stock']}",
                fg_color="transparent", hover_color=TEMA["borde"], text_color=TEMA["texto"],
                command=lambda c=codigo: self.agregar_codigo(c),
            ).pack(fill="x", padx=8, pady=1)
        restantes = len(coincidencias) - self.MAX_SUGERENCIAS
        if restantes > 0:
            ctk.CTkLabel(
                self.sugerencias, text=f"… y {restantes} más. Escribí más letras para afinar.",
                font=(FUENTE, 12), text_color=TEMA["texto_suave"],
            ).pack(anchor="w", padx=12, pady=(0, 6))
        self.sugerencias.pack(fill="x", padx=24, pady=(0, 12), before=self.detalle)
        self.mensaje(f"{len(coincidencias)} productos coinciden.", "aviso")

    def ocultar_sugerencias(self):
        self.sugerencias.pack_forget()
        for hijo in self.sugerencias.winfo_children():
            hijo.destroy()

    def agregar_codigo(self, codigo):
        """Agrega al carrito el producto con este código (ya sabemos que existe)."""
        try:
            cantidad = a_numero(self.cantidad.get(), int)
        except ValueError:
            self.mensaje("La cantidad tiene que ser un número entero.", "error")
            return
        if cantidad <= 0:
            self.mensaje("La cantidad tiene que ser mayor a 0.", "error")
            return

        producto = buscar_producto(codigo)
        if producto is None:
            self.mensaje("No existe un producto con ese código.", "error")
            return

        # Si el producto ya está en el carrito, se suman las cantidades
        total_pedido = self.carrito.get(codigo, 0) + cantidad
        if total_pedido > producto["stock"]:
            self.mensaje(
                f"Stock insuficiente de {producto['nombre']}: quedan {producto['stock']}.",
                "error",
            )
            return

        self.carrito[codigo] = total_pedido
        self.ocultar_sugerencias()
        self.codigo.delete(0, "end")
        self.cantidad.delete(0, "end")
        self.cantidad.insert(0, "1")
        self.codigo.focus()
        self.mensaje(f"Agregado: {producto['nombre']}", "ok")
        self.redibujar()

    def redibujar(self):
        lineas = []
        total = 0
        for codigo, cantidad in self.carrito.items():
            producto = buscar_producto(codigo)
            importe = producto["precio"] * cantidad
            total += importe
            lineas.append(
                f"{producto['nombre'][:28]:<28} x{cantidad:<4} {plata(importe):>14}"
            )
        escribir(self.detalle, "\n".join(lineas))
        self.total.configure(text=f"Total: {plata(total)}")

    def vaciar(self):
        self.carrito.clear()
        self.redibujar()

    def cobrar(self):
        if not self.carrito:
            self.mensaje("El carrito está vacío.", "aviso")
            return

        items = list(self.carrito.items())  # [(codigo, cantidad), ...]
        resultado = registrar_venta(items, self.medio.get())

        if isinstance(resultado, str):  # el backend devolvió un código de error
            self.mensaje(ERRORES_VENTA.get(resultado, resultado), "error")
            return

        self.vaciar()
        self.mensaje(
            f"Venta registrada: {plata(resultado['total'])} ({resultado['medio_pago']})",
            "ok",
        )
        self.codigo.focus()  # listo para escanear el próximo producto


# ----------------------------------------------------------------------
# STOCK
# ----------------------------------------------------------------------
class PantallaStock(Pantalla):
    def __init__(self, master):
        super().__init__(master, "Stock")

        # --- Alta de producto ---
        subtitulo(self, "Nuevo producto").pack(anchor="w", padx=24)
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=24, pady=(4, 12))

        columnas = [
            ("codigo", "Código"),
            ("nombre", "Nombre"),
            ("precio", "Precio de venta"),
            ("costo", "Costo"),
            ("stock", "Stock actual"),
            ("stock_minimo", "Stock mínimo"),
            ("vencimiento", "Vence (AAAA-MM-DD)"),
        ]
        self.campos = {}
        for i, (clave, texto) in enumerate(columnas):
            entrada = ctk.CTkEntry(form, placeholder_text=texto, width=150)
            entrada.grid(row=i // 4, column=i % 4, padx=(0, 8), pady=4)
            self.campos[clave] = entrada
        boton(form, "Agregar producto", self.agregar).grid(row=1, column=3, pady=4)

        # --- Ajuste de stock ---
        subtitulo(self, "Ajustar stock (positivo suma, negativo resta)").pack(
            anchor="w", padx=24
        )
        ajuste = ctk.CTkFrame(self, fg_color="transparent")
        ajuste.pack(fill="x", padx=24, pady=(4, 12))
        self.aj_codigo = ctk.CTkEntry(ajuste, placeholder_text="Código", width=150)
        self.aj_codigo.pack(side="left", padx=(0, 8))
        self.aj_cantidad = ctk.CTkEntry(ajuste, placeholder_text="+10 o -3", width=100)
        self.aj_cantidad.pack(side="left", padx=(0, 8))
        boton(ajuste, "Ajustar", self.ajustar).pack(side="left")

        # --- Tabla ---
        self.tabla = caja_de_texto(self)
        self.tabla.configure(font=(FUENTE_TABLA, 13), wrap="none")  # sin saltos de línea: las filas no se parten
        self.tabla.pack(fill="both", expand=True, padx=24, pady=(0, 8))

    def actualizar(self):
        lineas = [
            f"{'CÓDIGO':<14}{'NOMBRE':<16}{'PRECIO':>11}{'STOCK':>6}{'MÍN':>4} {'VENCE':<11}"
        ]
        for codigo, p in kiosco.items():
            vence, aviso = texto_vencimiento(p.get("vencimiento"))
            marcas = []
            if p["stock"] <= p["stock_minimo"]:
                marcas.append("⚠")
            if aviso in ("VENCIDO", "HOY"):
                marcas.append(f"✖ {aviso}")      # hay que retirarlo de la venta
            elif aviso:
                marcas.append(f"! {aviso}")      # vence en pocos días
            lineas.append(
                f"{codigo:<14}{p['nombre'][:15]:<16}{plata(p['precio']):>11}"
                f"{p['stock']:>6}{p['stock_minimo']:>4} {vence:<11}{'  '.join(marcas)}"
            )
        if not kiosco:
            lineas.append("(todavía no hay productos cargados)")
        else:
            lineas += [
                "",
                "⚠ stock bajo    ✖ vencido o vence hoy (retirar)    ! vence en 1 a 3 días",
            ]
        escribir(self.tabla, "\n".join(lineas))

    def agregar(self):
        c = self.campos
        try:
            codigo = c["codigo"].get().strip()
            nombre = c["nombre"].get().strip()
            precio = a_numero(c["precio"].get())
            costo = a_numero(c["costo"].get())
            stock = a_numero(c["stock"].get(), int)
            minimo = a_numero(c["stock_minimo"].get(), int)
        except ValueError:
            self.mensaje(
                "Precio y costo tienen que ser números; los stocks, números enteros.",
                "error",
            )
            return
        if not codigo or not nombre:
            self.mensaje("Faltan el código o el nombre.", "error")
            return
        vencimiento = c["vencimiento"].get().strip() or None

        resultado = agregar_producto(codigo, nombre, precio, costo, stock, minimo, vencimiento)

        if resultado == "creado":
            for entrada in c.values():
                entrada.delete(0, "end")
            self.mensaje(f"Producto creado: {nombre}", "ok")
            self.actualizar()
        elif resultado == "ya_existe":
            self.mensaje("Ya existe un producto con ese código.", "error")
        else:
            self.mensaje("Datos inválidos: revisá precio y stocks.", "error")

    def ajustar(self):
        codigo = self.aj_codigo.get().strip()
        try:
            cantidad = a_numero(self.aj_cantidad.get(), int)
        except ValueError:
            self.mensaje("La cantidad tiene que ser un número entero.", "error")
            return

        nuevo = actualizar_stock(codigo, cantidad)
        if nuevo is None:
            self.mensaje(
                "No se pudo: el código no existe o el stock quedaría negativo.", "error"
            )
            return
        self.aj_codigo.delete(0, "end")
        self.aj_cantidad.delete(0, "end")
        self.mensaje(f"Stock actualizado: ahora hay {nuevo} unidades.", "ok")
        self.actualizar()


# ----------------------------------------------------------------------
# CAJA
# ----------------------------------------------------------------------
class PantallaCaja(Pantalla):
    def __init__(self, master):
        super().__init__(master, "Cierre de caja")

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", padx=24, pady=(0, 12))
        self.fecha = ctk.CTkEntry(fila, width=150)
        self.fecha.pack(side="left", padx=(0, 8))
        boton(fila, "Calcular", self.calcular).pack(side="left")
        self.fecha.bind("<Return>", lambda e: self.calcular())

        self.resumen = caja_de_texto(self)
        self.resumen.pack(fill="both", expand=True, padx=24, pady=(0, 8))

    def actualizar(self):
        self.fecha.delete(0, "end")
        self.fecha.insert(0, str(date.today()))
        self.calcular()

    def calcular(self):
        fecha = self.fecha.get().strip()
        try:
            date.fromisoformat(fecha)
        except ValueError:
            self.mensaje("La fecha tiene que tener el formato AAAA-MM-DD.", "error")
            return

        r = cierre_de_caja(fecha)
        lineas = [
            f"Ventas del día:  {r['cantidad_ventas']}",
            f"Total vendido:   {plata(r['total_vendido'])}",
            f"Ganancia:        {plata(r['ganancia'])}",
            "",
            "Por medio de pago:",
        ]
        for medio, importe in r["por_medio_pago"].items():
            lineas.append(f"  {medio:<16}{plata(importe):>14}")
        if not r["por_medio_pago"]:
            lineas.append("  (sin ventas)")
        escribir(self.resumen, "\n".join(lineas))
        self.mensaje("", "ok")


# ----------------------------------------------------------------------
# ALERTAS
# ----------------------------------------------------------------------
class PantallaAlertas(Pantalla):
    def __init__(self, master):
        super().__init__(master, "Alertas de stock")
        self.lista = caja_de_texto(self)
        self.lista.pack(fill="both", expand=True, padx=24, pady=(0, 8))

    def actualizar(self):
        bajos = productos_con_stock_bajo()
        if not bajos:
            escribir(self.lista, "Todo en orden: ningún producto con stock bajo.")
            return
        lineas = []
        for codigo, p in bajos:
            lineas.append(
                f"{p['nombre'][:28]:<28} stock {p['stock']:<4} mínimo {p['stock_minimo']:<4} "
                f"(código {codigo})"
            )
        escribir(self.lista, "\n".join(lineas))


# ----------------------------------------------------------------------
# VENTANA PRINCIPAL
# ----------------------------------------------------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kiosco")
        self.geometry("1000x640")
        self.minsize(860, 560)
        self.configure(fg_color=TEMA["fondo"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        barra = ctk.CTkFrame(self, width=190, corner_radius=0, fg_color=TEMA["panel"])
        barra.grid(row=0, column=0, sticky="nsew")
        barra.pack_propagate(False)
        ctk.CTkLabel(
            barra, text="Kiosco", font=(FUENTE, 22, "bold"), text_color=TEMA["texto"]
        ).pack(padx=20, pady=(24, 20), anchor="w")

        self.pantallas = {
            "Ventas": PantallaVentas(self),
            "Stock": PantallaStock(self),
            "Caja": PantallaCaja(self),
            "Alertas": PantallaAlertas(self),
        }
        self.botones = {}
        for nombre in self.pantallas:
            b = ctk.CTkButton(
                barra, text=nombre, anchor="w", height=38,
                fg_color="transparent", hover_color=TEMA["borde"],
                text_color=TEMA["texto"],
                command=lambda n=nombre: self.mostrar(n),
            )
            b.pack(fill="x", padx=12, pady=3)
            self.botones[nombre] = b

        self.mostrar("Ventas")

    def mostrar(self, nombre):
        for n, pantalla in self.pantallas.items():
            pantalla.grid_forget()
            self.botones[n].configure(fg_color="transparent")
        pantalla = self.pantallas[nombre]
        pantalla.actualizar()
        pantalla.grid(row=0, column=1, sticky="nsew")
        self.botones[nombre].configure(fg_color=TEMA["acento"])


if __name__ == "__main__":
    App().mainloop()