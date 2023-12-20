# -*- coding: utf-8 -*-

import xlwt

class ExportarDatosZapatos:
    
    def __init__(self, nombreFichero, ruta, listaLugares):
        self.nombreFichero = nombreFichero
        self.ruta = ruta
        self.listaLugares = listaLugares
    
    def exportarExcel(self):
        writeBook= xlwt.Workbook(encoding='utf-8')
        sheet = writeBook.add_sheet("document",cell_overwrite_ok=True)
        style = xlwt.XFStyle()

        sheet.write(0, 0, 'ID')
        sheet.write(0, 1, 'MARCA')
        sheet.write(0, 2, 'MODELO')
        sheet.write(0, 3, 'COLOR')
        sheet.write(0, 4, 'PRECIO')
        sheet.write(0, 5, 'IMAGEN')
        sheet.write(0, 6, 'LINK')

        cont=1
        for lugar in self.listaLugares:
            string_con_tallas = ""
            sheet.write(cont, 0, lugar.id)
            sheet.write(cont, 1, lugar.marca)
            sheet.write(cont, 2, lugar.modelo)
            sheet.write(cont, 3, lugar.color)
            sheet.write(cont, 4, lugar.precio)
            sheet.write(cont, 5, lugar.imagen)
            sheet.write(cont, 6, lugar.link)
            contCeldas = 7
            for tallaItem in lugar.preciosTalla:
                sheet.write(0, contCeldas, 'TALLA')
                sheet.write(cont, contCeldas, tallaItem.toString())
                contCeldas = contCeldas + 1
            cont = cont + 1

        writeBook.save(self.ruta+self.nombreFichero)