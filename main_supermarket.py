from excel_data import *
from supermarket.mercadona import *
from supermarket.carrefour import *
from supermarket.dia import *
from datetime import *
from dotenv import load_dotenv
import pandas as pd

URL_CATEGORY_CARREFOUR = "https://www.carrefour.es/cloud-api/categories-api/v1/categories/menu/"
URL_PRODUCTS_BY_CATEGORY_CARREFOUR = "https://www.carrefour.es/cloud-api/plp-food-papi/v1"
URL_CATEGORY_DIA = "https://www.dia.es/api/v1/plp-insight/initial_analytics/charcuteria-y-quesos/jamon-cocido-lacon-fiambres-y-mortadela/c/L2001?navigation=L2001"
URL_PRODUCTS_BY_CATEGORY_DIA = "https://www.dia.es/api/v1/plp-back/reduced"

LIST_IDS_FAVORITES_PRODUCTS_MERCADONA = ["4749", "4193", "4954", "4957", "19733", "35343", "17382", "86190", "23575", "5044", "26029", "5325", "13577", "6261", "6250", "6245", "60722", "22836", "16883", "15430",
                    "11801", "67658", "11178", "13594", "2794", "4523", "2792", "25926", "2787", "3682", "3680", "2778", "2784", "2781", "25183", "25184", "25353", "25182", "30006", "4570", "3976", "8122", 
                    "35884", "2870", "15611", "86074", "53141", "59124", "59071", "50385", "50927", "51234", "51223", "61261", "61231", "18018", "18107", "16616", "16416", "7313", "86047", "7032", "16043", "13603", 
                    "10381", "20727", "10199", "40732", "40180", "71380", "43011", "43347", "43496", "16805", "49173", "49619", "47818", "49750", "83886", "80942", "21358"]

LIST_IDS_FAVORITES_PRODUCTS_CARREFOUR = []
LIST_IDS_FAVORITES_PRODUCTS_DIA = []


def check_favortites_products(df_supermercados):
    # Crear la columna 'Favorito' e inicializarla como False
    df_supermercados['Favorito'] = False

    # Marcar como True los registros con los Ids especificados
    df_supermercados.loc[df_supermercados['Id'].isin(LIST_IDS_FAVORITES_PRODUCTS_MERCADONA), 'Favorito'] = True
    df_supermercados.loc[df_supermercados['Id'].isin(LIST_IDS_FAVORITES_PRODUCTS_CARREFOUR), 'Favorito'] = True
    df_supermercados.loc[df_supermercados['Id'].isin(LIST_IDS_FAVORITES_PRODUCTS_DIA), 'Favorito'] = True
    
    return df_supermercados

def checkContions(ruta_env, ruta):
    # Si la carpeta export no existe
    if not os.path.exists(ruta):
        print("En la raiz del proyecto debe haber una carpeta llamada 'export'")
        return False
    
    # Si el archivo .env no existe
    if not os.path.exists(ruta_env):
        print("En la raiz del proyecto debe encontrarse el archivo .env del proyecto")
        return False
    
    # Si la carpeta export no existe
    if not os.path.exists(ruta):
        print("En la raiz del proyecto debe haber una carpeta llamada 'export'")
        return False
    
    # Si la variable de sesion COOKIE_CARREFOUR no existe
    if os.getenv('COOKIE_CARREFOUR') is None:
        print("En el archivo .env debe existir una variable llamada 'COOKIE_CARREFOUR' con la cookie correspondiente a Carrefour.")
        return False
    
    if os.getenv('COOKIE_CARREFOUR') == "TU_COOKIE_CARREFOUR":
        print("Debe cumplimentar en el archivo .env la variable llamada 'COOKIE_CARREFOUR' con la cookie correspondiente a Carrefour. Para mas informacion consulte el archivo 'Guia env.pdf'")
        return False
    
    # Si la variable de sesion COOKIE_DIA no existe
    if os.getenv('COOKIE_DIA') is None:
        print("En el archivo .env debe existir una variable llamada 'COOKIE_DIA' con la cookie correspondiente a Dia.")
        return False
    
    if os.getenv('COOKIE_DIA') == "TU_COOKIE_DIA":
        print("Debe cumplimentar en el archivo .env la variable llamada 'COOKIE_DIA' con la cookie correspondiente a Dia. Para mas informacion consulte el archivo 'Guia env.pdf'")
        return False
    
    return True
    
if __name__ == "__main__":

    load_dotenv()
    
    ruta_actual = os.getcwd()
    ruta = ruta_actual + "\export\\"
    ruta_env = ruta_actual + "\.env"
    
    if checkContions(ruta_env, ruta) == True:
        print("")
        print("------------------------------------MERCADONA------------------------------------")
        print("")
        df_mercadona = gestion_mercadona(ruta)
        print("")
        print("------------------------------------CARREFOUR------------------------------------")
        print("")
        df_carrefour = gestion_carrefour(ruta)
        print("")
        print("------------------------------------DIA------------------------------------")
        print("")
        df_dia = gestion_dia(ruta)
        
        # Unir los DataFrames verticalmente
        if(len(df_carrefour.columns) != 0):
            df_supermercados = pd.concat([df_mercadona, df_carrefour], ignore_index=True)
        else:
            df_supermercados = pd.concat([df_mercadona], ignore_index=True)
            
        if(len(df_dia.columns) != 0):
            df_supermercados = pd.concat([df_supermercados, df_dia], ignore_index=True)
        
        #Marcar los productos favoritos
        df_supermercados = check_favortites_products(df_supermercados)
        
        #Export Excel
        export_excel(df_supermercados, ruta, "products", "Productos")