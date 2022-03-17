"""Script to fetch stock prices"""
import datetime
from csv import reader
from postgres_client import PostgresClient
import commons as com
from models import FlightAvgDelay


def load_avg_delay_file(file_path):
    """
    Carga el archivo indicado por file_path y lo itera linea por linea sin cargarlo todo a memoria
    Genera una lista de FlightAvgDelay y la devuelve
    """
    result_list = []

    # open file in read mode
    with open(file_path, "r", encoding="UTF-8") as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        # Iterate over each row in the csv using reader object

        if header is not None:
            print(f"Header was: {header}")
            # header = "AEP_CODE,FL_DATE,AVG_DELAY\n"

            for idx, row in enumerate(csv_reader):
                origin_str = row[com.AVG_FILE_AEP_CODE_IDX]
                fl_date_str = row[com.AVG_FILE_FL_DATE_IDX]
                dep_delay_str = row[com.AVG_FILE_AVG_DELAY_IDX]
                nbr_flights_str = row[com.AVG_FILE_NBR_FLIGHTS_IDX]

                # parseo de avg_delay, completado de datos
                if dep_delay_str == "":
                    # completado de datos faltantes y limpieza
                    dep_delay = 0.0
                else:
                    dep_delay = float(row[com.AVG_FILE_AVG_DELAY_IDX])

                # parseo de fecha desde str
                parse_fl_date = datetime.datetime.strptime(fl_date_str, "%Y-%m-%d")

                # generacion de nuevo valor entero para el numero de dia
                day_of_year = (
                    parse_fl_date - datetime.datetime(parse_fl_date.year, 1, 1)
                ).days + 1

                parse_dep_delay = dep_delay

                # numero de vuelos totales en el dia
                parse_nbr_flights = int(nbr_flights_str)

                fad = FlightAvgDelay()
                fad.aep_code = origin_str  # data directly from file
                fad.avg_delay = parse_dep_delay  # float created from str data from file
                fad.flight_date = (
                    parse_fl_date  # datetime created from str data from file
                )
                fad.flight_day_nbr = day_of_year  # calculated int in [1, 366] range
                fad.nbr_flights = parse_nbr_flights  # nbr of flights in date from file

                print(f"#{idx}: {fad}")
                result_list.append(fad)

    return result_list


def main(**context):
    """
    Obtiene los parametros necesarios para correr la insercion a la base de datos
    del contenido de los archivos avg_xxx_.csv generados por el paso "calc_avg_delay"
    Luego invoca al metodo "main_local" que realiza realmente la insercion
    """

    print(f"Context: {context} ")
    print(f"Context type: {type(context)} ")

    run_date = context["data_interval_start"]
    print(f"Execution Date:  {run_date} ")

    main_local(execution_date=run_date)


def main_local(execution_date):
    """
    Proposito: Insertar los datos contenidos en los archivos avg_xxx_.csv que se determinan
    por el parametro de fecha execution_date
    """

    # Localizar archivo de datos a procesar. Un archivo contiene los datos de un periodo anual
    year_str = str(execution_date.year)
    data_file_name = f"avg_{year_str}.csv"
    print(f"File name for input data:  {data_file_name} ")
    data_file_path = com.DATA_DIR + "/" + data_file_name
    data_list = load_avg_delay_file(file_path=data_file_path)

    if len(data_list) > 0:
        print(f"START bulk data insert for file {data_file_path}")
        client = PostgresClient()
        client.bulk_save(data_list)
        print(f"END bulk data insert for file {data_file_path}")
    else:
        print(f"WARNING: No data to insert found for file: {data_file_path}")


if __name__ == "__main__":
    # solo para pruebas locales sin airflow
    main_local(datetime.datetime(2007, 1, 1))
