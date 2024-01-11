from bd_querys import *
from exportarDatos import ExportarDatosZapatos
from threading import Thread
import threading
import sys
import os
from datetime import *
import requests
import json
import pywhatkit
from zalando_data_scraper import *
import math
URL_API = "http://localhost:3100/"
#URL_API = "https://api-zalando.netlify.app/.netlify/functions/app/"
NUM_HILOS = 16

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

def openZalando(pagina_inicio, pagina_final, url_zalando, outputFolder, hilo):

    lista_productos = []

    #for indice_pagina in range(int(pagina_final)):
    for indice_pagina in range(pagina_inicio, int(pagina_final)):
        lista_productos = []

        url_with_page = url_zalando + "?p="+str(indice_pagina)

        scraper = ZalandoDataScraper()
        scraper.initDriver(url_with_page)

        listUrls = [];

        #Obtener URLs
        listUrls = scraper.scrapearZalando(url_with_page)

        #Gestion SIN HILOS
        contProductos = 1
        for itemUrls in listUrls:
            print("------Hilo=> "+str(hilo)+"------")
            print("------Procesando producto=> "+str(contProductos)+"/"+str(len(listUrls))+"------")
            producto_zalando = scraper.scrapearProductoZalando(itemUrls)
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
        #now = datetime.now()
        #dt_string = now.strftime("%d%m%Y-%H%M%S")
        #name_result_string = "zalando_resultado_pagina_" + str(indice_pagina)
        #exportar = ExportarDatosZapatos(outputFolder+name_result_string+"_"+dt_string+'.xls','', lista_productos)
        #exportar.exportarExcel()

        scraper.endDriver()

def mainThreadZalando(outputFolder):

    string_marcas_seleccionadas = ".".join(VECTOR_MARCAS_SELECCIONADAS)

    url_zalando = "https://www.zalando.es/calzado-hombre/" + string_marcas_seleccionadas + "/"

    scraper = ZalandoDataScraper()
    scraper.initDriver(url_zalando)
    pagina_final = scraper.scrappearPaginasZalando(url_zalando)

    total_paginas_hilo = math.floor(int(pagina_final) / NUM_HILOS)
    resto_paginas = int(pagina_final) - (total_paginas_hilo * NUM_HILOS)

    threads = []
    for hiloEjecucion in range(NUM_HILOS):
        if hiloEjecucion == NUM_HILOS - 1:
            #Ultima Pagina
            pagina_inicio = (hiloEjecucion * total_paginas_hilo)
            pagina_fin = (hiloEjecucion * total_paginas_hilo) + total_paginas_hilo + resto_paginas + 1
        else:
            pagina_inicio = (hiloEjecucion * total_paginas_hilo)
            pagina_fin = (hiloEjecucion * total_paginas_hilo) + total_paginas_hilo
        thread = threading.Thread(target=openZalando, args=(pagina_inicio, pagina_fin, url_zalando, outputFolder, hiloEjecucion))
        threads.append(thread)
        thread.start()

    # Esperar a que todos los hilos terminen
    for thread in threads:
        thread.join()

    print("Todos los hilos han terminado.")

def procesar_lista_zapatos_sin_precio(list_zapatos, hiloEjecucion):
    lista_productos = []

    scraper = ZalandoDataScraper()
    scraper.initDriver("https://www.zalando.es/")

    scraper.aceptar_cookies()

    contProductos = 1

    for itemZapato in list_zapatos:
        print("------Hilo=> "+str(hiloEjecucion)+"------")
        print("------Procesando producto=> "+str(contProductos)+"/"+str(len(list_zapatos))+"------")
        producto_zalando = scraper.scrapearProductoZalando(itemZapato['link'])
        contProductos = contProductos + 1

        if producto_zalando is None:
            print("!ERROR EN PRODUCTO: ")
            print(itemZapato)
            print()
        else:
            lista_productos.append(producto_zalando)

    #Publicar en BD
    post_data_in_database(lista_productos)

    scraper.endDriver()

def procesarProductosSinPrecioActual(outputFolder):
    list_zapatos = get_zapatos_sin_precio_hoy()

    numero_inicial_elementos = len(list_zapatos)

    list_zapatos_split = split_list(list_zapatos, NUM_HILOS)

    threads = []
    for hiloEjecucion in range(NUM_HILOS):
        thread = threading.Thread(target=procesar_lista_zapatos_sin_precio, args=(list_zapatos_split[hiloEjecucion], hiloEjecucion))
        threads.append(thread)
        thread.start()

    # Esperar a que todos los hilos terminen
    for thread in threads:
        thread.join()

    print("Todos los hilos han terminado.")
    print()

    print("Inicialmente habia: "+str(numero_inicial_elementos) + " sin precio")
    list_zapatos_sin_precio_post_operation = get_zapatos_sin_precio_hoy()
    print("Ahora hay " + str(len(list_zapatos_sin_precio_post_operation)) + " sin precio.")

def procesadoIndividual():
    URL_SELECCIONADA = "https://www.zalando.es/adidas-originals-adi2000-unisex-zapatillas-focus-olivecrystal-whitewonder-beige-ad115o1kt-n11.html"

    scraper = ZalandoDataScraper()
    scraper.initDriver("https://www.zalando.es/")

    scraper.aceptar_cookies()

    producto_zalando = scraper.scrapearProductoZalando(URL_SELECCIONADA)

    if producto_zalando is None:
        print("!ERROR EN PRODUCTO: ")
    else:
        lista_productos = []
        lista_productos.append(producto_zalando)
        print("Datos Zapato:")
        print(producto_zalando)
        print()
        #Publicar en BD
        post_data_in_database(lista_productos)

def envio_mensajes():

    list_marcas = [
        {"marca": "adidas Originals", "talla": "40 2/3"},
        {"marca": "adidas Performance", "talla": "40 2/3"},
        {"marca": "adidas Sportswear", "talla": "40 2/3"},
        {"marca": "Nike Performance", "talla": "41"},
        {"marca": "Nike SB", "talla": "41"},
        {"marca": "Nike Sportswear", "talla": "41"},
        {"marca": "Puma", "talla": "41"},
        {"marca": "New Balance", "talla": "41"},
        {"marca": "Vans", "talla": "41"},
        {"marca": "Converse", "talla": "41"},
    ]

    for itemMarca in list_marcas:
        list_productos = get_productos_by_marca_y_talla(itemMarca['talla'], itemMarca['marca'])

        for indiceProducto in range(5):
            if len(list_productos) >= indiceProducto:
                itemProducto = list_productos[indiceProducto]

                detallesProducto = f"{itemProducto['imagen']}\nNombre: {itemProducto['name']}\nMarca: {itemProducto['brand']}\nColor: {itemProducto['color']}\nPrecio Actual: {round(itemProducto['precio_actual_talla'], 2)} €\nPrecio Medio: {round(itemProducto['precio_medio'], 2)} €\nOferta: {round(itemProducto['porcentaje_cambio'], 2)} %\nLink:{itemProducto['link']}"

                send_message_to_telegram(detallesProducto)

        time.sleep(10)

def send_message_to_telegram(contenido):
    url = "https://api.telegram.org/bot6491103996:AAHxS8xRf_MveCVOzw-948quImdqpZQ9ZD0/sendMessage"

    payload = json.dumps({
    "text": contenido,
    "chat_id": "-4055086397"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

if __name__ == "__main__":
    fichero = r"C:\Users\josel\OneDrive\Escritorio\ProyectoZalando\export\\"

    #Funcion general
    mainThreadZalando(fichero)

    time.sleep(30)

    #Funcion para obtener los precios de los productos no comtemplados
    procesarProductosSinPrecioActual(fichero)

    time.sleep(30)

    #Notificacion de los resultados obtenidos
    envio_mensajes()

    #Proceso individual de un producto - Casos de prueba
    #procesadoIndividual()