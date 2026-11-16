Gestión de un almacén: enunciado, entradas, proceso y salida.

La gestión de un almacén requiere poder llevar control de los productos existentes, para lo cual se pretende diseñar un sistema acorde a las siguientes especificaciones:
En el almacén se requiere una catalogación de todos los productos existentes, para lo cual se almacenará un código de producto,  nombre del producto, unidades en stock, precio de venta, precio de costo, un stock mínimo y fecha de vencimiento del producto.
Además el sistema debe avisar qué productos se encuentran por debajo del stock mínimo o vencidos, para poder reponerlos o retirarlos de la venta.
El almacén desea registrar todo tipo de venta realizada en el día, teniendo en cuenta que el cliente puede abonar con diferentes métodos de pago. Como pago en efectivo, transferencia, tarjeta(débito o crédito) o también pagos con QR(Quick Response).
Al finalizar el día el almacén necesita un cierre de caja con la cantidad de ventas realizadas, el total vendido separado en cada método de pago y la ganancia obtenida.

Entradas:
El sistema recibe tres tipos de datos. El catálogo del producto, datos de cada venta y la fecha que se consulta en el cierre del día.
-Datos del producto(catálogo): Código del producto, nombre, unidades en stock, precio de venta, precio de costo, stock mínimo y fecha de vencimiento.
-Datos de venta: productos vendidos(código y cantidad de c/uno), métodos de pago(efectivo, transferencia, tarjeta débito o crédito y pago con QR), fecha de venta que toma el sistema.

Proceso:
El sistema valida los datos antes de guardar cualquier cambio, de modo que una operación con errores no modifica el stock ni el registro de ventas.
1)-Al cargar un producto:
-Se verifica que los datos ingresados sean válidos, precio de venta, stock y stock mínimo no deben ser negativos e igual a 0
-Verificar que el código no esté repetido
-Guardar el producto en el catálogo
2)-Al registrar una venta:
-Verificar que el código exista en el catálogo y que las cantidades sean mayor a 0
-Verificar que haya stock suficiente de cada producto
-Calcular el total de la venta
-Descontar del stock las unidades vendidas
-Guardar la venta con su fecha, método de pago, productos vendidos 
3)-Control de productos:
-Comparar el stock de cada producto con su stock mínimo para detectar los que haya que reponer
-Comparar la fecha de vencimiento con la fecha actual, para detectar productos vencidos o próximos a vencer
4)-Cierre del día:
-Seleccionar las ventas de la fecha consultada
-Contar las ventas y sumar el total vendido
-Sumar el total vendido por cada método de pago
-Calcular la ganancia

Salidas:
El sistema responde a cada operación con una confirmación o con un mensaje que explica por qué no se pudo realizar, emite los avisos y el reporte del día
-Confirmación de que el producto fue cargado o mensaje de error para los datos inválidos o productos repetidos
-Registro de la venta(total y método de pago)
-Stock actualizado después de cada venta
-Mensaje de error si la venta no se puede realizar(código inexistente, stock insuficiente o pago insuficiente)
-Listado de productos con stock bajo y de productos vencidos o a vencer
-Reporte del cierre diario: cantidad de ventas, total vendido, total por método de pago y ganancia obtenida.
