from datetime import date
import json, os, sys

if getattr(sys, "frozen", False):          # corriendo como .exe
    CARPETA = os.path.dirname(sys.executable)
else:                                      # corriendo como .py
    CARPETA = os.path.dirname(os.path.abspath(__file__))

ARCHIVO = os.path.join(CARPETA, "datos_kiosco.json")
#------------------------------------------------------
kiosco = {}
ventas = []
#------------------------------------------------------
#Agregar un producto al kiosco
def agregar_producto(codigo, nombre, precio, costo, stock, stock_minimo, vencimiento=None):
#Verificar que los datos ingresados sean válidos, no pueden ser 0 o negativos
    if precio <=0 or stock <0 or stock_minimo <0:
        return "datos_invalidos"
    if codigo in kiosco:
        return "ya_existe"
#En el diccionario kiosco con clave "codigo" se guardan todos los datos de cada producto
    kiosco[codigo] = {"nombre": nombre, "precio": precio, "costo": costo, "stock": stock, "stock_minimo": stock_minimo, "vencimiento": vencimiento}
    guardar_datos()
    return "creado"
#------------------------------------------------------
#Buscar producto
def buscar_producto(codigo):
    return kiosco.get(codigo) # .get() es una funcion de diccionarios, te devuelve el catalogo del producto buscado(si existe) o None(si no existe)
#------------------------------------------------------
#Acualizacion de stock
def actualizar_stock(codigo, cantidad):
    if buscar_producto(codigo) is None:
        return None  #Se verifica que el codigo exista
    nuevo=kiosco[codigo]["stock"] + cantidad #Se calcula el nuevo stock sumando la cantidad ingresada al stock actual
    if nuevo <0: #El stock ingresado no puede ser 0 o negativo
        return None
    else:
        kiosco[codigo]["stock"] = nuevo #Se actualiza el stock
        guardar_datos()
        return nuevo
#------------------------------------------------------
#Registrar venta
def registrar_venta(items, medio_pago):
    #Validaciones de producto
    if not items:
        return "datos_invalidos"
    for codigo, cantidad in items:
        if cantidad <=0:
            return "datos_invalidos"
        if buscar_producto(codigo) is None:
            return "codigo_inexistente"
        if cantidad > kiosco[codigo]["stock"]:
            return "stock_insuficiente"
    #datos validados
    total=0
    item_venta=[] #lista que guarda los items de la venta, cada item es un diccionario con codigo, cantidad, precio y costo
    for codigo, cantidad in items:
        producto=buscar_producto(codigo)
        actualizar_stock(codigo, -cantidad) #Se usa la variable cantidad en negativo, ya que la funcion actualizar_stock es una suma
        item_venta.append({"codigo": codigo,
            "cantidad": cantidad,
            "precio": producto["precio"],
            "costo": producto["costo"]
            }) #diccionario que guarda los datos de cada item de la venta
        total += producto["precio"] * cantidad #Se calcula el total de la venta sumando el precio de cada item multiplicado por la cantidad vendida
    venta = {
        "fecha": str(date.today()),
        "items": item_venta,
        "total": total,
        "medio_pago": medio_pago
        } #diccionario que guarda los datos de la venta, fecha, items, total y medio de pago
    ventas.append(venta)
    guardar_datos()
    return venta
#------------------------------------------------------
#Productos con stock bajo
def productos_con_stock_bajo():
    stockmin=[]
    for codigo, producto in kiosco.items(): #for que recorre el diccionario kiosco, donde codigo es la clave y producto es el valor (que es otro diccionario con los datos del producto)
        if producto["stock"] <= producto["stock_minimo"]: #Se compara el stock actual con el stock minimo, si es menor o igual se agrega a la lista stockmin
            stockmin.append((codigo, producto))
    return stockmin       
#------------------------------------------------------
#Buscar Producto por nombre
def buscar_por_nombre(texto):
    resultado=[]
    for codigo, producto in kiosco.items(): 
        if texto.lower() in producto["nombre"].lower(): #se compara el texto ingresado con el nombre del producto, ambos en minuscula para que no sea sensible a mayusculas o minusculas
            resultado.append((codigo, producto))
    return resultado
#------------------------------------------------------
#Cierre de caja
def cierre_de_caja(fecha):
    cantidad = 0 #Variable cantidad que guarda y va sumando la cantidad de ventas realizadas en la fecha ingresada
    total = 0 #Variable total que guarda y va sumando el total de ventas realizadas en la fecha ingresada
    ganancia = 0 #Variable ganancia que guarda y va sumando la ganancia obtenida en la fecha ingresada
    por_medio={} #diccionario que guarda el total vendido por cada medio de pago
    for venta in ventas: 
        if venta["fecha"]== fecha: #Si la fecha de la venta es igual a la fecha ingresada, se suman los datos de la venta a las variables cantidad, total y ganancia, y se guarda el total vendido por cada medio de pago en el diccionario por_medio
            cantidad += 1
            total += venta["total"]
            for item in venta["items"]: #Se recorre la lista de items de la venta
                ganancia += (item["precio"] - item["costo"]) * item["cantidad"] #Variable ganancia que guarda y va sumando el calculo de precio + item multiplicado por la cantidad vendida
            if venta["medio_pago"] in por_medio: #Si el medio de pago de la venta ya existe en el diccionario por_medio, se suma el total de la venta al valor existente, si no existe se crea una nueva entrada en el diccionario con el total de la venta
                por_medio[venta["medio_pago"]] += venta["total"]
            else:
                por_medio[venta["medio_pago"]] = venta["total"]
    guardar_datos()
    return {
            "cantidad_ventas": cantidad,
            "total_vendido": total,
            "por_medio_pago": por_medio,
            "ganancia": ganancia
            } #diccionario que guarda los datos del cierre de caja

#Guardar Datos
def guardar_datos():
    datos_kiosco = {"kiosco": kiosco, "ventas": ventas} 
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(datos_kiosco, archivo, ensure_ascii=False, indent=2)
#------------------------------------------------------
#Cargar Datos
def cargar_datos():
    if not os.path.exists(ARCHIVO): 
        return
    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    kiosco.clear()
    kiosco.update(datos["kiosco"])
    ventas.clear()
    ventas.extend(datos["ventas"])
#------------------------------------------------------
cargar_datos()
#------------------------------------------------------