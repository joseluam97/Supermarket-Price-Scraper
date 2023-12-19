# -*- coding: utf-8 -*-
import random
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from precio_producto_zalando import PrecioProductoZalando
from producto_zalando import ProductoZalando
from selenium.common.exceptions import NoSuchElementException
import chromedriver_autoinstaller

from selenium.webdriver.chrome.service import Service as ChromeService

VECTOR_MARCAS_SELECCIONADAS = ["adidas","nike","converse","new-balance","puma","vans"]
#VECTOR_MARCAS_SELECCIONADAS = ["nike","adidas"]

class ZalandoDataScraper:

    def __init__(self, idioma, imgOutput):
        self.driver = None
        self.errorCont = 0
        self.imgOutput = imgOutput
        self.configuracion = self.setConfiguracion(idioma)
    
    def setConfiguracion(self, idioma):
        conf = {
            'idioma': '--lang=es-ES',
            'textoEstrellas': 'estrellas',
            'textoReviews': 'reseñas',
            'textoDireccion': 'Dirección: ',
            'textoWeb': 'Sitio web: ',
            'textoTelefono': 'Teléfono: ',
            'textoPlusCode': 'Plus Code: ',
            'textoHorario': 'Ocultar el horario de la semana',
            'remplazarHorario': [' Ocultar el horario de la semana', 'El horario podría cambiar', '; ']
        }
        if(idioma == 'EN'):
            conf['idioma'] = '--lang=en-GB'
            conf['textoEstrellas'] = 'stars'
            conf['textoReviews'] = 'reviews'
            conf['textoDireccion'] = 'Address: '
            conf['textoWeb'] = 'Website: '
            conf['textoTelefono'] = 'Phone: '
            conf['textoPlusCode'] = 'Plus code: '
            conf['textoHorario'] = 'Hide open hours for the week'
            conf['remplazarHorario'] = ['. Hide open hours for the week', 'Hours might differ', '; ']
        
        return conf
    
    def initDriver(self, url_destino):
        try:
            chrome_path = "/usr/bin/chromium-browser"
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument(self.configuracion['idioma'])
            #chromedriver_path = r"C:\Users\josel\.cache\selenium\chromedriver\win64\119.0.6045.105\chromedriver.exe"
            #s = Service(chromedriver_path)
            #s=Service(ChromeDriverManager().install())
            #self.driver = webdriver.Chrome(service=s, options=chrome_options)
            # Crear una instancia del controlador
            self.driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options, service=ChromeService(chrome_path))
            time.sleep(2)
            self.driver.get(url_destino)
            time.sleep(2)
            return True
        except Exception as e:
            print(f'Error with the Chrome Driver: {e}')
            return False
    
    def quitarTildes(self, s):
        replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),)
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s

    def scrappearPaginasZalando(self, url_destino):
        try:
            self.errorCont = 0
            time.sleep(1)
            self.driver.get(url_destino)
            time.sleep(2)

            paginas_disponibles = self.driver.find_element(By.XPATH, ".//div[contains(@class, '_0xLoFW FCIprz')]//span[contains(@class, 'sDq_FX _2kjxJ6 FxZV-M HlZ_Tf JCuRr_ _0xLoFW uEg2FS FCIprz')]").text
            
            return paginas_disponibles.split()[3]

        except:
            print("ERROR - Obtener paginas")
            return 0

    def scrapearProductoZalando(self, url_destino):
        try:
            
            print("--------url_destino----------")
            print(url_destino)
            self.driver.get(url_destino)
            time.sleep(2)
            selector_talla = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="picker-trigger"]')))
            time.sleep(2)

            try:
                contenido_producto = self.driver.find_element(By.XPATH, '//div[@class="L5YdXz _0xLoFW _7ckuOK mROyo1 s8As-K"]')
            except NoSuchElementException:
                contenido_producto = self.driver.find_element(By.XPATH, '//div[@class="L5YdXz _0xLoFW _7ckuOK mROyo1 s8As-K mxVWRR"]')
                print("LOG-EXCEPT EN GET CONTENT INICIAL")

            producto_zalando = ProductoZalando()

            elemento_articulo = contenido_producto.find_element(By.XPATH, '//div[@data-testid="pdp-accordion-details"]')

            elemento_boton_caracteristica = elemento_articulo.find_element(By.XPATH, ".//button[contains(@class, '_ZDS_REF_SCOPE_ SX0LGY vfoVrE DJxzzA u9KIT8 uEg2FS U_OhzR')]")
            elemento_boton_caracteristica.click()

            id_articulo = 0
            elemento_clase_vacia = elemento_articulo.find_elements(By.XPATH, "//div[normalize-space(@class)='']")

            for itemDivVacio in elemento_clase_vacia:
                try:
                    titulo_caracteristica = itemDivVacio.find_element(By.XPATH, ".//dt[contains(@class, 'sDq_FX lystZ1 dgII7d HlZ_Tf zN9KaA')]").text
                    if titulo_caracteristica == "Número de artículo:":
                        numero_articulo = itemDivVacio.find_element(By.XPATH, ".//dd[contains(@class, 'sDq_FX lystZ1 FxZV-M HlZ_Tf zN9KaA')]").text
                        id_articulo = numero_articulo
                except:
                    pass

            marca = contenido_producto.find_element(By.XPATH, ".//h3[contains(@class, 'FtrEr_')]").text
            #GESTION MODELO
            try:
                modelo = contenido_producto.find_element(By.XPATH, ".//h3[contains(@class, 'EKabf7')]").text
            except:
                modelo = contenido_producto.find_element(By.XPATH, ".//h1[contains(@class, 'sDq_FX ')]//span[contains(@class, 'EKabf7 ')]").text

            color = contenido_producto.find_element(By.XPATH, ".//p[contains(@class, 'sDq_FX _2kjxJ6 FxZV-M HlZ_Tf')]//span[contains(@class, 'sDq_FX lystZ1 dgII7d HlZ_Tf zN9KaA')]").text
            imagen_value = contenido_producto.find_element(By.XPATH, ".//div[contains(@class, 'KVKCn3')]//img[contains(@class, 'sDq_FX')]").get_attribute('src')
            price = contenido_producto.find_element(By.XPATH, ".//p[contains(@class, '_0xLoFW')]//span[contains(@class, 'sDq_FX')]").text

            #Gestion de obtener precios
            selector_talla.click()
            time.sleep(1)
            contTallas = 1
            list_talla_precio = self.driver.find_elements(By.XPATH, ".//span[contains(@class, 'hDNRPv')]//div[contains(@class, '_0xLoFW')]")
            for itemList in list_talla_precio:
                precioProductoZalando = PrecioProductoZalando()
                try:
                    talla_numero = itemList.find_element(By.XPATH, ".//span[contains(@class, 'sDq_FX _2kjxJ6 dgII7d HlZ_Tf')]").text
                    if "desde" in price:
                        #INICIO => sDq_FX lystZ1 FxZV-M Yb63TQ uMACAo
                        #DESCUENTO => sDq_FX lystZ1 FxZV-M Km7l2y uMACAo
                        precio_talla = itemList.find_element(By.XPATH, ".//span[contains(@class, 'sDq_FX lystZ1 FxZV-M')]").text
                    else:
                        precio_talla = price

                    disponible = True
                except:
                    talla_numero = itemList.find_element(By.XPATH, ".//span[contains(@class, 'sDq_FX _2kjxJ6 dgII7d Yb63TQ')]").text
                    if "desde" in price:
                        precio_talla = 0
                    else:
                        precio_talla = price
                    disponible = False
                
                if precio_talla != 0:
                    precioProductoZalando.talla = talla_numero
                    precioProductoZalando.precio = precio_talla
                    precioProductoZalando.disponibilidad = disponible

                    producto_zalando.preciosTalla.append(precioProductoZalando)

                contTallas = contTallas + 1

            producto_zalando.id = id_articulo
            producto_zalando.marca = marca
            producto_zalando.modelo = modelo
            producto_zalando.color = color
            producto_zalando.precio = price
            producto_zalando.imagen = imagen_value
            producto_zalando.link = url_destino

            return producto_zalando

        except Exception as e:
                    print(e)
                    self.errorCont += 1
                    return None
        

    def scrapearZalando(self, url_destino):
        try:
            self.errorCont = 0
            time.sleep(1)
            self.driver.get(url_destino)
            time.sleep(2)

            #Vector con las urls de todos los productos
            listUrlProductos = []

            #Aceptar cookies
            aceptar_cookies = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "uc-btn-accept-banner")))
            aceptar_cookies.click()

            #Encuentra todos los elementos que contienen la información de los productos
            #productos = self.driver.find_elements(By.TAG_NAME, "article")
            #productos = self.driver.find_elements(By.XPATH, ".//div[contains(@class, '_5qdMrS w8MdNG cYylcv BaerYO _75qWlu iOzucJ JT3_zV _Qe9k6')]")
            productos = self.driver.find_elements(By.XPATH, ".//div[contains(@class, '_5qdMrS w8MdNG cYylcv BaerYO _75qWlu iOzucJ JT3_zV _Qe9k6') and not(contains(@class, 'data-experiment-hint'))]")

            # Itera sobre los elementos y extrae la información
            contProductos = 1
            totalProductos = str(len(productos))
            for producto in productos:
                try:
                    print("----------------------------"+str(contProductos)+"/"+totalProductos+"----------------------------")

                    link_producto = producto.find_element(By.XPATH, ".//a[contains(@class, '_LM')]").get_attribute('href')

                    listUrlProductos.append(link_producto)
                
                except:
                    print("ERROR - En obtener detalles producto")

                contProductos = contProductos + 1

            listUrlProductos_filter = [elemento for elemento in listUrlProductos if any(palabra in elemento for palabra in VECTOR_MARCAS_SELECCIONADAS)]

            return listUrlProductos_filter

        except Exception as e:
            print(e)
            self.errorCont += 1
            return None
    
    def buscar_xpath(self, xpath):
        try:
            resultado = self.driver.find_element(By.XPATH, xpath).text
            return resultado
        except:
            return ''
    
    def endDriver(self):
        self.driver.quit()