from excel_data import *
from datetime import *
import requests
import pandas as pd
import time
import numpy as np

URL_CATEGORY_MERCADONA = "https://tienda.mercadona.es/api/categories/"
URL_PRODUCTS_BY_CATEGORY_MERCADONA = "https://tienda.mercadona.es/api/categories/"


def gestion_mercadona(ruta):
    # Registra el tiempo de inicio
    tiempo_inicio_mercadona = time.time()

    # Ejecutar las acciones para obtener los productos
    list_categories = get_ids_categorys_mercadona()
    df_mercadona = get_products_by_category_mercadona(list_categories, ruta)

    # Registra el tiempo de finalización
    tiempo_fin_mercadona = time.time()

    # Calcula la duración total
    duracion_total_mercadona = tiempo_fin_mercadona - tiempo_inicio_mercadona

    # Obtener minutos y segundos
    minutos_mercadona = int(duracion_total_mercadona // 60)
    segundos_mercadona = int(duracion_total_mercadona % 60)

    # Mostrar el log con el tiempo de ejecución en minutos y segundos
    print(f"La ejecución de Mercadona ha tomado un tiempo de {minutos_mercadona} minutos y {segundos_mercadona} segundos")
    
    return df_mercadona;


def get_products_by_category_mercadona(list_categories, ruta):
    
    df_products = pd.DataFrame()
    
    for index, idCategoria in enumerate(list_categories):
        print(str(index+1)+"/" + str(len(list_categories)) + " - Procesando los productos de la categoria "+str(idCategoria)+".")
        url = URL_PRODUCTS_BY_CATEGORY_MERCADONA + str(idCategoria)

        #Obtener los productos de la categoria
        list_products_data = requests.get(url)
        list_products = list_products_data.json()
        
        #print(list_products)
        
        # Obtener las columnas específicas de "categories"
        df_productos = pd.json_normalize(list_products["categories"], "products")
        
        # Modificar las propiedades oportunas cuando los productos son precios aproximados
        condicion = df_productos['price_instructions.approx_size']
        df_productos.loc[condicion, 'price_instructions.unit_size'] = 1
        df_productos.loc[condicion, 'price_instructions.unit_price'] = df_productos.loc[condicion, 'price_instructions.bulk_price']
        
        #Add column to category
        df_productos['categoria'] = str(idCategoria)
        df_productos['supermercado'] = "Mercadona"

        # Seleccionar y renombrar columnas
        #selected_columns = ['id', 'display_name','packaging', 'price_instructions.unit_price', 'price_instructions.bulk_price', 'price_instructions.unit_size','price_instructions.size_format','price_instructions.approx_size', 'categoria', 'supermercado', 'share_url', 'thumbnail']
        selected_columns = ['id', 'display_name', 'price_instructions.unit_price', 'price_instructions.bulk_price', 'price_instructions.size_format', 'categoria', 'supermercado', 'share_url', 'thumbnail']
        renamed_columns = {
            'id': 'Id',
            'display_name': 'Nombre', 
            'price_instructions.unit_price': 'Precio',
            'price_instructions.bulk_price': 'Precio Pack',
            #'price_instructions.unit_size': 'Tamano',
            'price_instructions.size_format': 'Formato',
            #'price_instructions.approx_size': 'Approx Size',
            'categoria': 'Categoria',
            'supermercado': 'Supermercado',
            'share_url': 'Url', 
            'thumbnail': 'Url_imagen'
            }

        df_products_by_categoria = df_productos[selected_columns].rename(columns=renamed_columns)
        
        # Unir los DataFrames verticalmente
        df_products = pd.concat([df_products, df_products_by_categoria], ignore_index=True)
        
        time.sleep(1)
    
    #Export Excel
    export_excel(df_products, ruta, "products_mercadona_", "Productos_Mercadona")
    
    return df_products
    

def get_ids_categorys_mercadona():

    list_category_mercadona_data = requests.get(URL_CATEGORY_MERCADONA)
    list_category_mercadona = list_category_mercadona_data.json()

    df = pd.json_normalize(list_category_mercadona["results"], sep="_")

    # Obtener las columnas específicas de "categories"
    df_categories = pd.json_normalize(list_category_mercadona["results"], "categories", sep="_", record_prefix="category_")

    # Combinar los DataFrames
    df = pd.concat([df, df_categories], axis=1)

    category_ids = df["category_id"].explode().dropna().astype(int).tolist()

    return category_ids

