from excel_data import *
import os
from datetime import *
import requests
from dotenv import load_dotenv
import pandas as pd
import time
import numpy as np

URL_CATEGORY_CARREFOUR = "https://www.carrefour.es/cloud-api/categories-api/v1/categories/menu/"
URL_PRODUCTS_BY_CATEGORY_CARREFOUR = "https://www.carrefour.es/cloud-api/plp-food-papi/v1"

HEADERS_REQUEST_CARREFOUR = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': "es-GB,es;q=0.9,en-GB;q=0.8,en;q=0.7,es-419;q=0.6",
    'Cookie': '',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def gestion_carrefour(ruta):
    
    #Add cookie into header json
    HEADERS_REQUEST_CARREFOUR["Cookie"] = os.getenv('COOKIE_CARREFOUR')
    
    # Registra el tiempo de inicio
    tiempo_inicio_carrefour = time.time()

    # Ejecutar las acciones para obtener los productos
    list_categories = get_ids_categorys_carrefour()
    df_carrefour = get_products_by_category_carrefour(list_categories, ruta)

    # Registra el tiempo de finalización
    tiempo_fin_carrefour = time.time()

    # Calcula la duración total
    duracion_total_carrefour = tiempo_fin_carrefour - tiempo_inicio_carrefour

    # Obtener minutos y segundos
    minutos_carrefour = int(duracion_total_carrefour // 60)
    segundos_carrefour = int(duracion_total_carrefour % 60)

    # Mostrar el log con el tiempo de ejecución en minutos y segundos
    print(f"La ejecución de Carrefour ha tomado un tiempo de {minutos_carrefour} minutos y {segundos_carrefour} segundos")
    
    return df_carrefour
    

def get_products_by_category_carrefour(list_categories, ruta):
    
    df_products = pd.DataFrame()
    
    for index, stringCategoria in enumerate(list_categories):
        print(str(index+1)+"/" + str(len(list_categories)) + " - Procesando los productos de la categoria "+str(stringCategoria)+".")
        url = URL_PRODUCTS_BY_CATEGORY_CARREFOUR + str(stringCategoria)

        #Cumplimentar todos los offset hasta el error
        existeOffset = True
        offsetPagina = 0
        while(existeOffset == True):
            try:
                print("[OFFSET] " + str(offsetPagina) + " - Categoria "+str(stringCategoria)+".")
                #Obtener los productos de la categoria
                url_page = url + "?offset=" + str(offsetPagina)
                list_products_data = requests.get(url_page, headers=HEADERS_REQUEST_CARREFOUR)
                list_products = list_products_data.json()
                
                # Obtener las columnas específicas de "categories"
                df_productos = pd.json_normalize(list_products["results"], "items")
                
                # Concatenar "https://www.carrefour.es" a la columna "url"
                df_productos['url'] = 'https://www.carrefour.es' + df_productos['url']
                df_productos['categoria'] = stringCategoria
                df_productos['supermercado'] = "Carrefour"

                # Seleccionar y renombrar columnas
                selected_columns = ['product_id', 'name', 'price', 'price_per_unit', 'measure_unit','categoria', 'supermercado', 'url', 'images.desktop']
                renamed_columns = {
                    'product_id': 'Id', 
                    'name': 'Nombre',
                    'price': 'Precio',
                    'price_per_unit': 'Precio Pack',
                    'measure_unit': 'Formato',
                    'categoria': 'Categoria',
                    'supermercado': 'Supermercado',
                    'url': 'Url', 
                    'images.desktop': 'Url_imagen'
                    }

                df_products_by_categoria = df_productos[selected_columns].rename(columns=renamed_columns)
                
                #Comprobar que no se ha pasado el offset
                # Supongamos que df_otro es tu otro DataFrame
                valor_id_first = df_products_by_categoria.loc[0, 'Id']
                if 'Id' in df_products.columns:
                    existe_valor = valor_id_first in df_products['Id'].values
                else:
                    existe_valor = False
                
                if existe_valor == False:
                    # Unir los DataFrames verticalmente
                    df_products = pd.concat([df_products, df_products_by_categoria], ignore_index=True)
                    offsetPagina = offsetPagina + 24
                else:
                    # print("ERROR - Offset sobrepasado")
                    existeOffset = False
                
            except:
                print("[FIN] - Fin de la obtencion de productos de la categoria")
                existeOffset = False
    
    #Export Excel
    export_excel(df_products, ruta, "products_carrefour_", "Productos_Carrefour")
    
    return df_products

def get_ids_categorys_carrefour():

    try:
        list_category_carrefour_data = requests.get(URL_CATEGORY_CARREFOUR, headers=HEADERS_REQUEST_CARREFOUR)
        list_category_carrefour = list_category_carrefour_data.json()
    except:
        print("ERROR - La cookie proporcionada para el supermercado Carrefour ha caducado")
        return []
    
    df = pd.json_normalize(list_category_carrefour["menu"], sep="_")

    # Obtener las columnas específicas de "categories"
    df_categories = pd.json_normalize(list_category_carrefour["menu"], "childs", sep="_", record_prefix="childs_")
    
    # Combinar los DataFrames
    df = pd.concat([df, df_categories], axis=1)
    
    # Filtrar por las que comienzan por "/supermercado" y no incluyen "ofertas"
    filtro = df['childs_url_rel'].str.startswith('/supermercado') & ~df['childs_url_rel'].fillna('').astype(str).str.contains('ofertas')

    # Aplicar el filtro al DataFrame
    df = df[filtro]

    #category_ids = df["childs_url_rel"].explode().dropna().astype(str).tolist()
    category_ids = df["childs_id"].explode().dropna().astype(str).tolist()
    
    sub_category_ids = []
    
    for stringCategoria in category_ids:    
        
        URL_SUB_CATEGORY_CARREFOUR = "https://www.carrefour.es/cloud-api/categories-api/v1/categories/menu?sale_point=005704&depth=1&current_category="+stringCategoria+"&limit=3&lang=es&freelink=true"
    
        list_sub_category_carrefour_data = requests.get(URL_SUB_CATEGORY_CARREFOUR, headers=HEADERS_REQUEST_CARREFOUR)
        list_sub_category_carrefour = list_sub_category_carrefour_data.json()
         
        # Normalizar el primer nivel ("menu")
        df_menu = pd.json_normalize(list_sub_category_carrefour, "menu", sep="_")

        # Normalizar el siguiente nivel ("childs")
        df_childs = pd.json_normalize(df_menu["childs"].explode(), sep="_", record_prefix="childs_")

        # Normalizar el siguiente nivel ("childs") de nuevo para profundizar
        df_childs_deep = pd.json_normalize(df_childs["childs"].explode(), sep="_", record_prefix="childs_")

        # Normalizar el siguiente nivel ("childs") de nuevo para profundizar
        df_categories = pd.json_normalize(df_childs_deep["childs"].explode(), sep="_", record_prefix="childs_")
        
        # Obtener las columnas específicas de "categories"
        sub_category_ids = sub_category_ids + df_categories["url_rel"].explode().dropna().astype(str).tolist()

    return sub_category_ids

    
