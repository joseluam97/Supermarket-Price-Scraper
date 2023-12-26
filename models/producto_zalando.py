# -*- coding: utf-8 -*-

class ProductoZalando:
    
    def __init__(self):
        self.id = ''
        self.marca = ''
        self.modelo = ''
        self.color = ''
        self.precio = ''
        self.imagen = ''
        self.link = ''
        self.preciosTalla = []
    
    def __str__(self):
        return f"Id: {self.id}\nMarca: {self.marca}\nModelo: {self.modelo}\nColor: {self.color}\nPrecio: {self.precio} \nImagen: {self.imagen}\nLink: {self.link}"