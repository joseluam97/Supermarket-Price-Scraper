from datetime import *

def export_excel(dataframe, ruta, fileName, sheetName):
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y-%H%M%S")
    nameFile = fileName+dt_string+'.xlsx'
        
    dataframe.to_excel(ruta + nameFile, sheet_name=sheetName, index=False)
    