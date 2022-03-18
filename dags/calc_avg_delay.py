"""
    Modulo para calcular la demora promedio anual de vuelo
    Toma como input un archivo que tiene el contenido anual de datos
    Escribe como output un archivo en el promedio de demora por aeropuerto y dia
"""
from csv import reader
import sys

DATA_DIR = "data"

FL_DATE_COL_IDX = 0
ORIGIN_COL_IDX = 3
DEP_DELAY_COL_IDX = 7

DELAY_LIST_AEP_COUNT_IDX = 0
DELAY_LIST_AEP_TOTAL_DELAY = 1
DELAY_LIST_AEP_AVG_DELAY = 2


def main(**context):
    """
    Abre el archivo file_name y lo itera linea por linea sin cargarlo todo a memoria
    Calcula el promedio de demora por dia y por aeropuerto
    Escribe el resultado en un archivo nuevo
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
    aep_dic = generate_aep_dic(file_path)
    print_aep_dic(aep_dic)
    write_aep_dic_to_file(file_name, aep_dic)


def generate_aep_dic(file_name):
    """
    Abre el archivo file_name y lo iter linea por linea sin cargarlo todo a memoria
    Calcula el promedio de demora por dia y por aeropuerto y lo devuele
    """
    aep_dic = {}

    # open file in read mode
    with open(file_name, "r", encoding="UTF-8") as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        # Iterate over each row in the csv using reader object

        rows_parsed = 0
        min_delay = None
        max_delay = None
        avg_delay = None

        if header is not None:
            print(f"Header was: {header}")

            for row in csv_reader:
                fl_date = row[FL_DATE_COL_IDX]
                origin = row[ORIGIN_COL_IDX]
                dep_delay_str = row[DEP_DELAY_COL_IDX]
                rows_parsed = rows_parsed + 1

                if dep_delay_str == "":
                    dep_delay = 0.0
                else:
                    dep_delay = float(row[DEP_DELAY_COL_IDX])

                if min_delay is None:
                    min_delay = dep_delay
                else:
                    min_delay = min(dep_delay, min_delay)

                if max_delay is None:
                    max_delay = dep_delay
                else:
                    max_delay = max(dep_delay, max_delay)

                if avg_delay is None:
                    avg_delay = dep_delay
                else:
                    avg_delay = avg_delay * (
                        rows_parsed - 1
                    )  # obtener sumatoria actual partiendo del promedio
                    avg_delay = (
                        avg_delay + dep_delay
                    )  # sumar la nueva contribucion para obtener la nueva suma
                    avg_delay = (
                        avg_delay / rows_parsed
                    )  # a la nueva suma se la divide por uno mas

                parse_row = [
                    fl_date,
                    origin,
                    dep_delay,
                ]
                # row variable is a list that represents a row in csv
                # imprimir primeras 5 filas de datos
                if rows_parsed <= 5:
                    print(parse_row)

                date_dic = aep_dic.get(origin)  # columna de aeropuerto

                if date_dic is None:  # el aeropuerto no existe en el diccionario
                    date_dic = {}

                    init_list = [
                        1,  # conteo de veces que aparece el aeropueto en una fecha dada
                        dep_delay,  # demora acumulada para una fecha
                        dep_delay / 1,  # demora promedio en esa fecha
                    ]

                    date_dic[fl_date] = init_list
                    aep_dic[origin] = date_dic
                else:
                    delay_list = date_dic.get(fl_date)

                    if delay_list is None:
                        init_list = [
                            1,  # conteo de veces que aparece el aeropueto en una fecha dada
                            dep_delay,  # demora acumulada para una fecha
                            dep_delay / 1,  # demora promedio en esa fecha
                        ]
                        date_dic[fl_date] = init_list
                    else:
                        aep_count = delay_list[DELAY_LIST_AEP_COUNT_IDX] + 1
                        aep_sum = delay_list[DELAY_LIST_AEP_TOTAL_DELAY] + dep_delay
                        aep_avg = aep_sum / aep_count

                        delay_list[DELAY_LIST_AEP_COUNT_IDX] = aep_count
                        delay_list[DELAY_LIST_AEP_TOTAL_DELAY] = aep_sum
                        delay_list[DELAY_LIST_AEP_AVG_DELAY] = aep_avg

            parse_header = [
                header[FL_DATE_COL_IDX],
                header[ORIGIN_COL_IDX],
                header[DEP_DELAY_COL_IDX],
            ]
            print("HEADER")
            print(parse_header)
            print("STATS")
            file_stats = (
                f"Rows: {rows_parsed} -- avg delay: {avg_delay} -- "
                f"min delay: {min_delay} -- max delay: {max_delay}"
            )

            print(file_stats)

    return aep_dic


def print_aep_dic(aep_dic):
    """
    Imprime el contenido del diccionario de aeropuertos
    asi como tambien lo que ocupa el diccionario en memoria en bytes
    """

    print("AEP DIC")
    print(aep_dic)
    print("### ###")
    print(f"aep_dic total keys: {len(aep_dic.keys())}")
    print(f"aep_dic memory usage: {sys.getsizeof(aep_dic)} bytes")
    num = 13546546546
    print(type(num))
    print(f"size of int {num} : {sys.getsizeof(num)} bytes")
    print(f"size of new int instance: {sys.getsizeof(int())} bytes")


def write_aep_dic_to_file(src_file_name, aep_dic):
    """
    Escribe el diccionario de aeropuertos a un archivo .CSV
    con el promedio de demorar por fecha y por aeropuerto

    """
    dest_file = "avg_" + src_file_name
    dest_path = DATA_DIR + "/" + dest_file
    print(f"Dest file path: {dest_path}")

    with open(dest_path, "w", encoding="UTF-8") as out_file:
        header = "AEP_CODE,FL_DATE,AVG_DELAY,NBR_FLIGHTS\n"
        out_file.write(header)
        for aep in aep_dic.keys():
            fd_dic = aep_dic.get(aep)
            for fl_date in fd_dic.keys():
                delay_list = fd_dic.get(fl_date)
                row = (
                    aep
                    + ","
                    + fl_date
                    + ","
                    + str(delay_list[DELAY_LIST_AEP_AVG_DELAY])
                    + ","
                    + str(delay_list[DELAY_LIST_AEP_COUNT_IDX])
                    + "\n"
                )
                out_file.write(row)


# if __name__ == "__main__":
#    main("2007.csv")

# calc_avg_delay("2009.csv")
# calc_avg_delay("2007.csv")
