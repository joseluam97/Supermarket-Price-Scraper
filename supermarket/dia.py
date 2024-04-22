from excel_data import *
import os
from datetime import *
import requests
from dotenv import load_dotenv
import pandas as pd
import time

URL_CATEGORY_DIA = "https://www.dia.es/api/v1/plp-insight/initial_analytics/charcuteria-y-quesos/jamon-cocido-lacon-fiambres-y-mortadela/c/L2001?navigation=L2001"
URL_PRODUCTS_BY_CATEGORY_DIA = "https://www.dia.es/api/v1/plp-back/reduced"

HEADERS_REQUEST_DIA = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': "es-GB,es;q=0.9",
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

def gestion_dia(ruta):
    
    #Add cookie into header json
    HEADERS_REQUEST_DIA["Cookie"] = os.getenv('COOKIE_DIA')
    
    # Registra el tiempo de inicio
    tiempo_inicio_dia = time.time()

    # Ejecutar las acciones para obtener los productos
    list_categories = get_ids_categorys_dia()
    df_dia = get_products_by_category_dia(list_categories, ruta)

    # Registra el tiempo de finalización
    tiempo_fin_dia = time.time()

    # Calcula la duración total
    duracion_total_dia = tiempo_fin_dia - tiempo_inicio_dia

    # Obtener minutos y segundos
    minutos_dia = int(duracion_total_dia // 60)
    segundos_dia = int(duracion_total_dia % 60)

    # Mostrar el log con el tiempo de ejecución en minutos y segundos
    print(f"La ejecución de DIA ha tomado un tiempo de {minutos_dia} minutos y {segundos_dia} segundos")
    
    return df_dia


def get_products_by_category_dia(list_categories, ruta):
    
    df_products = pd.DataFrame()
    
    for index, stringCategoria in enumerate(list_categories):
        print(str(index+1)+"/" + str(len(list_categories)) + " - Procesando los productos de la categoria "+str(stringCategoria)+".")
        url = URL_PRODUCTS_BY_CATEGORY_DIA + str(stringCategoria)

        #Obtener los productos de la categoria
        list_products_data = requests.get(url, headers=HEADERS_REQUEST_DIA)
        list_products = list_products_data.json()
            
        try:
            df_productos = pd.json_normalize(list_products["plp_items"], sep="_")
            
            # Concatenar "https://www.dia.es" a la columna "url"
            df_productos['url'] = 'https://www.dia.es' + df_productos['url']
            df_productos['image'] = 'https://www.dia.es' + df_productos['image']
            df_productos['categoria'] = stringCategoria
            df_productos['supermercado'] = "Dia"
            
            # Seleccionar y renombrar columnas
            selected_columns = ['object_id', 'display_name', 'prices_price', 'prices_price_per_unit', 'prices_measure_unit','categoria', 'supermercado', 'url', 'image']
            renamed_columns = {
                'object_id': 'Id', 
                'display_name': 'Nombre',
                'prices_price': 'Precio',
                'prices_price_per_unit': 'Precio Pack',
                'prices_measure_unit': 'Formato',
                'categoria': 'Categoria',
                'supermercado': 'Supermercado',
                'url': 'Url', 
                'image': 'Url_imagen'
                }

            df_products_by_categoria = df_productos[selected_columns].rename(columns=renamed_columns)
            
            # Unir los DataFrames verticalmente
            df_products = pd.concat([df_products, df_products_by_categoria], ignore_index=True)
            
        except:
            print("ERROR - En la obtencion de productos de la categoria")
            
    #Export Excel
    export_excel(df_products, ruta, "products_dia_", "Productos_Dia")
    
    return df_products
            

def get_ids_categorys_dia():
    
    try:
        list_category_dia_data = requests.get(URL_CATEGORY_DIA, headers=HEADERS_REQUEST_DIA)
        list_category_dia = list_category_dia_data.json()
    except:
        print("ERROR - La cookie proporcionada para el supermercado DIA ha caducado")
        return []
    
    info = list_category_dia['menu_analytics']

    # Crear el DataFrame resultante
    data = procesar_nodo(info)
    df_resultado = pd.DataFrame(data, columns=['id', 'parameter', 'path'])

    # Utilizar pandas para operaciones de datos
    # Filtrar solo las filas con valores en la columna 'parameter'
    df_resultado = df_resultado[df_resultado['parameter'].notna()]

    category_ids = df_resultado["path"].explode().dropna().astype(str).tolist()
    

    return category_ids

def procesar_nodo(nodo, parent_path=""):
    data = []
    for key, value in nodo.items():
        path = f"{parent_path}/{key}" if parent_path else key
        parameter = value.get('parameter', None)
        path_list = value.get('path', None)
        data.append((key, parameter, path_list))
        children = value.get('children', {})
        if children:
            data.extend(procesar_nodo(children, parent_path=path))
        elif 'children' in value:  # Caso donde 'children' está presente pero vacío
            data.append(('', None, path))  # Agregar una fila con 'parameter' y 'path' vacíos
    return data