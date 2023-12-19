from exportarDatos import ExportarDatosZapatos
from threading import Thread
import sys
import os
from datetime import *
import requests
import json
from zalando_data_scraper import *
#URL_API = "http://localhost:3100/"
URL_API = "https://api-zalando.netlify.app/.netlify/functions/app/"

def split_list(a, n):
    k, m = divmod(len(a), n)
    return list((a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)))

def scrapearListProductHilo(lista, hilo, resultados, scraper):
    listProductos = []

    cont=1
    for itemUrl in lista:
        producto_zalando = scraper.scrapearProductoZalando(itemUrl)
        
        if(producto_zalando != None):
            print('Hilo nº '+str(hilo)+' ' +str(cont) + '/' + str(len(lista)) + ' - OK - ' + itemUrl)
            listProductos.append(producto_zalando)
        else:
            print('Hilo nº '+str(hilo)+' ' +str(cont) + '/' + str(len(lista)) + ' - ERROR - ' + itemUrl)
        cont +=1
    
    resultados[hilo] = listProductos

def openZalando(idioma, ficheroKw, outputFolder):

    string_marcas_seleccionadas = ".".join(VECTOR_MARCAS_SELECCIONADAS)

    url_zalando = "https://www.zalando.es/calzado-hombre/" + string_marcas_seleccionadas + "/"
    #url_zalando = "https://www.zalando.es/calzado-hombre/nike.adidas/"

    scraper = ZalandoDataScraper(idioma, outputFolder)
    scraper.initDriver(url_zalando)
    pagina_final = scraper.scrappearPaginasZalando(url_zalando)
    #pagina_final = 1

    lista_productos = []

    #for indice_pagina in range(int(pagina_final)):
    for indice_pagina in range(1, int(pagina_final)):
        lista_productos = []

        url_with_page = url_zalando + "?p="+str(indice_pagina)

        scraper = ZalandoDataScraper(idioma, outputFolder)
        scraper.initDriver(url_with_page)

        listUrls = [];

        #Obtener URLs
        listUrls = scraper.scrapearZalando(url_with_page)
        # Modo test split list => listUrls = split_list(listUrls,20)[0]
        # Modo test unitario => listUrls.append("https://www.zalando.es/adidas-originals-adi-ease-zapatillas-ad112o02f-c11.html")

        #Gestion SIN HILOS
        contProductos = 1
        for itemUrls in listUrls:
            print("------Pagina=> "+str(indice_pagina)+"/"+str(pagina_final)+"------")
            print("------Procesando producto=> "+str(contProductos)+"/"+str(len(listUrls))+"------")
            producto_zalando = scraper.scrapearProductoZalando(itemUrls)
            print(producto_zalando)
            contProductos = contProductos + 1

            if producto_zalando is None:
                print("!ERROR EN PRODUCTO: ")
                print(itemUrls)
                print()
            else:
                lista_productos.append(producto_zalando)

        #Publicar en BD
        post_data_in_database(lista_productos)

        #Export Excel
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y-%H%M%S")
        name_result_string = "zalando_resultado_pagina_" + str(indice_pagina)
        exportar = ExportarDatosZapatos(outputFolder+name_result_string+"_"+dt_string+'.xls','', lista_productos)
        exportar.exportarExcel()

        scraper.endDriver()



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
    url = URL_API + "prices"

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
    url = URL_API + "productos/byIdZalando/" + str(idZalando)

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
    url = URL_API + "productos"

    # Realizar la solicitud POST
    response = requests.post(url, json=elemento)

    # Verificar la respuesta
    if response.status_code == 200:
        #print("Producto creado exitosamente.")
        return response.json()
    else:
        return None

if __name__ == "__main__":
    idioma = "ES"
    kwLugares = r"C:\Users\josel\OneDrive\Escritorio\ProyectoZalando\texto.txt"
    fichero = r"C:\Users\josel\OneDrive\Escritorio\ProyectoZalando\export\\"
    
    openZalando(idioma,kwLugares, fichero)
    '''while True:
        idioma = input('----------\n[1] Introduce the language, (ES o EN): ')
        if(idioma != 'ES' and idioma != 'EN'):
            print("----------\n** Error ** That is not a valid language. Enter a valid language\n")
            continue
        else:
            break
    
    while True:
        fichero = input('----------\n[2] Introduce the path to save the images: ')
        if(os.path.isdir(fichero) == False):
            print("----------\n** Error ** That is not a valid folder. Enter a valid folder\n")
            continue
        else:
            caracter = fichero[len(fichero)-1]
            if(caracter != '/' or caracter != '\\'):
                fichero = fichero.replace('/','\\')+'\\'
            break
    
    while True:
        kwLugares = input('----------\n[3] Introduce the path of the keywords txt file: ')
        if(os.path.isfile(kwLugares) == False):
            print("----------\n** Error ** That is not a valid txt file. Enter a valid file\n")
            continue
        else:
            break'''