# Gestión de almacén — Proyecto de cursada

Sistema de escritorio para administrar un almacén o kiosco: catálogo de productos, control de stock y vencimientos, registro de ventas con distintos medios de pago y cierre de caja diario.

Está hecho en **Python** con una interfaz gráfica en **CustomTkinter**. Los datos se guardan automáticamente en un archivo JSON, así que no se pierden al cerrar el programa.

## Funcionalidades

- **Ventas**: se arma un carrito buscando productos por código (compatible con lector de código de barras) o por nombre. Si varios productos coinciden con el nombre, se muestra una lista para elegir. Al cobrar se elige el medio de pago y el stock se descuenta solo.
- **Stock**: alta de productos nuevos, ajuste de stock (sumar o restar unidades) y una tabla con todo el catálogo que marca:
  - `⚠` stock igual o por debajo del mínimo
  - `✖` producto vencido o que vence hoy (hay que retirarlo)
  - `!` producto que vence en 1 a 3 días
- **Cierre de caja**: para una fecha dada muestra la cantidad de ventas, el total vendido, el total por cada medio de pago y la ganancia (precio de venta menos costo).
- **Alertas**: lista de los productos que hay que reponer porque tienen stock bajo.

Todas las operaciones validan los datos antes de guardar: una venta o un alta con errores no modifica el stock ni el registro de ventas, y la interfaz muestra un mensaje explicando qué falló.

## Requisitos

- Python 3.8 o superior
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

```bash
pip install customtkinter
```

## Cómo ejecutarlo

Con los dos archivos `.py` en la misma carpeta:

```bash
python interfaz.py
```

La primera vez que se guarda algo se crea `datos_kiosco.json` en la misma carpeta, con el catálogo y el historial de ventas.

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `kiosco.py` | Lógica del sistema (backend): catálogo, stock, ventas, cierre de caja y guardado/carga de datos en JSON. No depende de la interfaz. |
| `interfaz.py` | Interfaz gráfica con CustomTkinter. Tiene cuatro pantallas (Ventas, Stock, Caja y Alertas) y usa las funciones de `kiosco.py`. |
| `2do parcial algoritmos.md` | Enunciado del problema con el análisis de entradas, proceso y salidas. |

### Funciones principales de `kiosco.py`

| Función | Qué hace | Devuelve |
|---|---|---|
| `agregar_producto(codigo, nombre, precio, costo, stock, stock_minimo, vencimiento)` | Da de alta un producto | `"creado"`, `"ya_existe"` o `"datos_invalidos"` |
| `buscar_producto(codigo)` | Busca por código exacto | El producto o `None` |
| `buscar_por_nombre(texto)` | Busca productos cuyo nombre contenga el texto (sin distinguir mayúsculas) | Lista de `(codigo, producto)` |
| `actualizar_stock(codigo, cantidad)` | Suma (o resta, si es negativa) unidades al stock | El nuevo stock o `None` si el código no existe o quedaría negativo |
| `registrar_venta(items, medio_pago)` | Registra una venta con una lista de `(codigo, cantidad)` | La venta registrada, o `"datos_invalidos"`, `"codigo_inexistente"` o `"stock_insuficiente"` |
| `productos_con_stock_bajo()` | Productos con stock menor o igual al mínimo | Lista de `(codigo, producto)` |
| `cierre_de_caja(fecha)` | Resumen de las ventas de una fecha (`AAAA-MM-DD`) | Cantidad de ventas, total vendido, total por medio de pago y ganancia |

### Formato de los datos

Cada producto se guarda en un diccionario cuya clave es el código:

```json
{
  "7790001": {
    "nombre": "Alfajor",
    "precio": 1200,
    "costo": 800,
    "stock": 24,
    "stock_minimo": 5,
    "vencimiento": "2026-12-15"
  }
}
```

Cada venta guarda la fecha, los productos vendidos (con el precio y el costo de ese momento), el total y el medio de pago.

## Autor

Marichal Agustin
