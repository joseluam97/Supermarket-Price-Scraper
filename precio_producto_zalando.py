# -*- coding: utf-8 -*-

class PrecioProductoZalando:
    
    def __init__(self):
        self.talla = ''
        self.precio = ''
        self.disponibilidad = ''
    
    def __str__(self):
        return f"nTalla: {self.talla}\nPrecio: {self.precio}\nDisponibilidad: {self.disponibilidad}"