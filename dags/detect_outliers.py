"""
    Modulo para detectar vuelos con demoras fuera de lo normal a nivel de aeropuerto
    Toma como input el archivo de salida de calc_avg_delay.py que tiene el promedio
    de demoras por fecha y aeropuerto
    Escribe como output un archivo XXXXX
"""
from csv import reader
import sys

DATA_DIR = "data"


def main(**context):
    """
    Abre el archivo file_name y lo iter linea por linea sin cargarlo todo a memoria
    Instancia el modelo de deteccion de anormalidades
    Corre el modelo
    """
    # diccionario con key : aeropuerto -- value : diccionario por fecha
    # contiene el promedio del tiempo de demora de salida (columna
    # DEP_DELAY) por aeropuerto de salida (columna ORIGIN) y dia

    print(f"Context: {context} ")
    print(f"Context type: {type(context)} ")

    execution_date = context["data_interval_start"]
    print(f"Execution Date:  {execution_date} ")

    file_name = str(execution_date.year) + ".csv"
    print(f"File name for input data:  {file_name} ")

    file_path = DATA_DIR + "/" + file_name


# if __name__ == "__main__":
#    main("2007.csv")

# calc_avg_delay("2009.csv")
# calc_avg_delay("2007.csv")
