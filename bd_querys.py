import sys
import os
import requests
from dotenv import load_dotenv

def post_data_in_database(lista_productos):
    for itemProducto in lista_productos:
        idProducto = "ERROR"
        if not itemProducto.id is None:
            idProducto = itemProducto.id
        elemento = {
            "id_zalando": idProducto,
            "name": itemProducto.modelo,
            "brand": itemProducto.marca,
            "color": itemProducto.color,
            "imagen": itemProducto.imagen,
            "link": itemProducto.link,
        }

        #POST O GET DEL ZAPATO DEPENDIENDO SI EXISTE O NO
        dato_zapato = post_or_get_zapato(elemento, itemProducto.id)
        
        for itemPrecio in itemProducto.preciosTalla:
            #REGISTRO DEL PRECIO ACTUAL
            if not itemPrecio is None:
                post_price(dato_zapato, itemPrecio)
            else:
                print("!ERROR EN PRECIO: ")
                print(itemPrecio)
                print()


def post_price(dato_zapato, itemPrecio):
    # URL del endpoint donde realizarás la solicitud POST
    url = os.getenv('URL_API') + "prices"

    #Format price
    cadena_sin_simbolo = str(itemPrecio.precio).replace("€", "").replace("\xa0", "")
    price = float(cadena_sin_simbolo.replace(".", "").replace(",", "."))

    #Creacion del json
    newPrice = {
        "idProducto": dato_zapato["_id"],
        "talla": itemPrecio.talla,
        "price": price,
        "disponible": itemPrecio.disponibilidad,
    }

    # Realizar la solicitud POST para comprobar la existencia del elemento
    response = requests.post(url, json=newPrice)

    # Verificar la respuesta
    if response.status_code != 200:
        print("!ERROR en el registro del precio. Codigo de error:" + str(response.status_code))
        print(dato_zapato)
        print(itemPrecio)
        print()
        

def post_or_get_zapato(elemento, idZalando):
    # URL del endpoint donde realizarás la solicitud POST
    url = os.getenv('URL_API') + "productos/byIdZalando/" + str(idZalando)

    # Realizar la solicitud POST para comprobar la existencia del elemento
    response = requests.get(url)

    # Verificar la respuesta
    if response.status_code == 200:
        dato_zapato = response.json()
        #Verificar si existen datos existente
        
        if dato_zapato:
            #Existe el producto ya
            return dato_zapato
        else:
            #No existe
            #Creacion del elemento en BD
            elemento_created = post_zapato(elemento)
            return elemento_created
    

def post_zapato(elemento):
    # URL del endpoint donde realizarás la solicitud POST
    url = os.getenv('URL_API') + "productos"

    # Realizar la solicitud POST
    response = requests.post(url, json=elemento)

    # Verificar la respuesta
    if response.status_code == 200:
        #print("Producto creado exitosamente.")
        return response.json()
    else:
        return None
    

def get_zapatos_sin_precio_hoy():
    # URL del endpoint donde realizarás la solicitud POST
    url = os.getenv('URL_API') + "productos/checkProductHavePrices"

    # Realizar la solicitud GET
    response = requests.get(url)

    # Verificar la respuesta
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def get_productos_by_marca_y_talla(talla, marca):
    # URL del endpoint donde realizarás la solicitud POST
    url = os.getenv('URL_API') + "productos/byBrand"

    # Realizar la solicitud GET
    payload = {'talla': talla, 'brand': marca}
    response = requests.get(url, params=payload)

    # Verificar la respuesta
    if response.status_code == 200:
        return response.json()
    else:
        return None