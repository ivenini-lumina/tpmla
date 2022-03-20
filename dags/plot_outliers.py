"""Obtener de la DB los datos de cada aeropuerto y generar un grafico"""
import datetime
import os
from postgres_client import PostgresClient
import matplotlib.pyplot as plt
import numpy as np
import commons as com


def main(**context):
    """Program entrypoint"""
    execution_date = context["data_interval_start"]
    print(f"Execution Date for plot_outliers:  {execution_date} ")

    cfg = com.load_config()

    from_date = datetime.datetime(execution_date.year, 1, 1)
    to_date = datetime.datetime(execution_date.year, 12, 31)

    print(f"Plot date range: {from_date} --- {to_date}")

    client = PostgresClient()
    aep_list = client.get_aep_list(from_date, to_date)

    print("Airport list for date range:")
    print(aep_list)

    # Crear directorios si no existen
    year_string = str(from_date.year)
    data_dir = f"{com.get_data_dir(cfg)}/{year_string}"

    if not os.path.exists(data_dir):
        # Create a new directory because it does not exist
        os.makedirs(data_dir)

    for aep_vec in aep_list:
        print(f"Plotting start for {aep_vec}")
        aep_code = aep_vec[0]
        flight_list = client.get_flight_list(aep_code, from_date, to_date)
        flight_array = np.array(flight_list)

        print(f"Data rows to plot: {len(flight_array)}")

        flight_date_column = flight_array[:, 0]
        flight_count_column = flight_array[:, 1]
        flight_anomal_column = flight_array[:, 2]
        flight_anomal_int_column = np.array(flight_anomal_column, dtype=np.int8)

        values = [flight_date_column, flight_count_column]

        colors = np.array([com.COLOR_RED, com.COLOR_GREEN])
        color_idx = (flight_anomal_int_column + 1) // 2

        color_vec = colors[color_idx]

        plt.bar(
            values[0],
            values[1],
            # s=10,
            label=aep_code,
            color=color_vec,
        )

        plt.xticks(rotation=90)
        plt.legend()
        plt.xlim(from_date, to_date)

        plt.suptitle(f"Aeropuerto {aep_code}", fontsize=15, fontweight="bold")
        plt.title(
            (
                f"Vuelos entre {str(from_date.day)}-{str(from_date.month)}-{str(from_date.year)} "
                f"y {str(to_date.day)}-{str(to_date.month)}-{str(to_date.year)}"
            )
        )

        png_file_path = f"{data_dir}/{aep_code}.png"
        plt.savefig(png_file_path)

        print(f"File saved: {png_file_path}")
        plt.figure()

    print("Plotting done")
