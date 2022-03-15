"""
    Modulo para detectar vuelos con demoras fuera de lo normal a nivel de aeropuerto
    Toma como input el archivo de salida de calc_avg_delay.py que tiene el promedio
    de demoras por fecha y aeropuerto
    Escribe como output un archivo XXXXX
"""
import time
import datetime
from csv import reader
import matplotlib.pyplot as plt
import numpy as np
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest


# Parametros generales
DATA_DIR = "data"
COLOR_CERULEAN = "#377eb8"  # outliers
COLOR_ORANGE = "#ff7f00"  # inliers


# Parametros de graficos
PLOT_EXPECTED_MIN_X = 1
PLOT_EXPECTED_MAX_X = 366

PLOT_EXPECTED_MIN_Y = -100
PLOT_EXPECTED_MAX_Y = 650

# Parametros de configuracion de algoritmos
ANSWER_TO_EVERYTHING = 42
OUTLIERS_FRACTION = 0.06

# Constantes de indices del archivo de promedio de demoras
AEP_CODE_IDX = 0
FL_DATE_IDX = 1
AVG_DELAY_IDX = 2


def create_mesh_vectors():
    """Ver que hace esto"""
    # Compare given classifiers under given settings
    xx1, yy1 = np.meshgrid(
        np.linspace(PLOT_EXPECTED_MIN_X, PLOT_EXPECTED_MAX_X, 365),
        np.linspace(PLOT_EXPECTED_MIN_Y, PLOT_EXPECTED_MAX_Y, 1500),
    )
    # xx1, yy1 = np.meshgrid(np.linspace(-7, 7, 150), np.linspace(-7, 7, 150))
    # xx1, yy1 = np.meshgrid(np.linspace(-1500, 1500, 150), np.linspace(-50, 50, 150))
    return xx1, yy1


def create_algorithms(random_seed, anomaly_percent):
    """Crea un listado de algoritmos para detectar anomalias segun los parametros indicado"""

    anomaly_algorithms = [
        ("Robust covariance", EllipticEnvelope(contamination=anomaly_percent)),
        (
            "Isolation Forest",
            IsolationForest(contamination=anomaly_percent, random_state=random_seed),
        ),
    ]
    return anomaly_algorithms


def load_dataset(file_name):
    """
    Carga el archivo file_name y lo itera linea por linea sin cargarlo todo a memoria
    Genera una lista que tiene un array con los datos para luego alimentar a los algoritmos de
    deteccion de anomalias
    """
    outlier_list = []
    outlier_sub_list = []
    outlier_list.append(outlier_sub_list)

    # open file in read mode
    with open(file_name, "r", encoding="UTF-8") as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        # Iterate over each row in the csv using reader object

        if header is not None:
            print(f"Header was: {header}")
            # header = "AEP_CODE,FL_DATE,AVG_DELAY\n"

            for idx, row in enumerate(csv_reader):
                # origin = row[AEP_CODE_IDX]
                fl_date_str = row[FL_DATE_IDX]
                dep_delay_str = row[AVG_DELAY_IDX]

                if dep_delay_str == "":
                    dep_delay = 0.0
                else:
                    dep_delay = float(row[AVG_DELAY_IDX])

                fl_date = datetime.datetime.strptime(fl_date_str, "%Y-%m-%d")
                day_of_year = (fl_date - datetime.datetime(fl_date.year, 1, 1)).days + 1

                parse_fl_date = day_of_year
                parse_dep_delay = dep_delay

                parse_row = [parse_fl_date, parse_dep_delay]
                # row variable is a list that represents a row in csv

                nprow = np.array([parse_fl_date, parse_dep_delay])

                print(f"#{idx}: --> {row} --> {parse_row} --> {nprow}")

                out_sublist = outlier_list[0]
                out_sublist.append(nprow)

    dataset_list = []
    result_sub_array = np.array(out_sublist)
    dataset_list.append(result_sub_array)

    return dataset_list


def detect_outliers(anomaly_algorithms, datasets, xx_param, yy_param):
    """
    Corre los algoritmos para detectar outliers y grafica el resultado
    Puede recibir varios datasets a iterar y por cada dataset genera
    un grafico con los resultados de cada algoritmo usado
    """

    print(">>> - Run each algorithm in each dataset")

    for i_dataset, data_vec_x in enumerate(datasets):
        print(
            f"    >>> - Start Running Dataset # {i_dataset} with size: {len(data_vec_x)}"
        )

        plot_num = 1

        for algo_name, algorithm in anomaly_algorithms:
            fit_start_time = time.time()
            algorithm.fit(data_vec_x)
            fit_end_time = time.time()
            plt.subplot(len(datasets), len(anomaly_algorithms), plot_num)
            if i_dataset == 0:
                plt.title(algo_name, size=18)

            print(f"        >>> - Run algorithm {algo_name}")

            # fit the data and tag outliers
            if algo_name == "Local Outlier Factor":
                y_pred = algorithm.fit_predict(data_vec_x)
                print(f"INPUT : {data_vec_x}")
                print(f"OUTPUT: {y_pred}")
            else:
                y_pred = algorithm.fit(data_vec_x).predict(data_vec_x)
                print(f"INPUT : {data_vec_x}")
                print(f"OUTPUT: {y_pred}")

            print(f"        >>> - Plot algorithm {algo_name}")

            # plot the levels lines and the points
            if algo_name != "Local Outlier Factor":  # LOF does not implement predict
                print("        >>> - Draw contour")
                ravel_xx = xx_param.ravel()
                ravel_yy = yy_param.ravel()
                point_xy = np.c_[ravel_xx, ravel_yy]
                print(f"CTR PARAM X # : {len(xx_param)} --> {xx_param.shape}")
                print(f"CTR PARAM X: {xx_param}")
                print(f"CTR PARAM Y # : {len(yy_param)} --> {yy_param.shape}")
                print(f"CTR PARAM Y: {yy_param}")
                print(f"CTR RAVEL X #: {len(ravel_xx)} --> {ravel_xx.shape}")
                print(f"CTR RAVEL X: {ravel_xx}")
                print(f"CTR RAVEL Y #: {len(ravel_yy)} --> {ravel_yy.shape}")
                print(f"CTR RAVEL Y: {ravel_yy}")
                print(f"CTR INPUT XY #: {len(point_xy)} --> {point_xy.shape}")
                print(f"CTR INPUT XY: {point_xy}")

                prediction_vec_z = algorithm.predict(point_xy)
                print(
                    f"RAW PREDICTION Z # {len(prediction_vec_z)} --> {prediction_vec_z.shape}"
                )
                print(f"RAW OUTPUT Z: {prediction_vec_z}")
                prediction_vec_z = prediction_vec_z.reshape(xx_param.shape)
                print(
                    f"RESHAPE PREDICTION Z # {len(prediction_vec_z)} --> {prediction_vec_z.shape}"
                )
                print(f"CTR FINAL OUTPUT Z: {prediction_vec_z}")
                plt.contour(
                    xx_param,
                    yy_param,
                    prediction_vec_z,
                    levels=[0],
                    linewidths=2,
                    colors="black",
                )

            colors = np.array([COLOR_CERULEAN, COLOR_ORANGE])
            scatter_x0_in = data_vec_x[:, 0]
            scatter_x1_in = data_vec_x[:, 1]

            print(f"INPUT SCATTER X0: {scatter_x0_in}")
            print(f"INPUT SCATTER X1: {scatter_x1_in}")

            plt.scatter(
                scatter_x0_in, scatter_x1_in, s=10, color=colors[(y_pred + 1) // 2]
            )

            plt.xlim(PLOT_EXPECTED_MIN_X, PLOT_EXPECTED_MAX_X)
            plt.ylim(PLOT_EXPECTED_MIN_Y, PLOT_EXPECTED_MAX_Y)

            # plt.xticks(())
            # plt.yticks(())

            plt.text(
                0.99,
                0.01,
                ("%.2fs" % (fit_end_time - fit_start_time)).lstrip("0"),
                transform=plt.gca().transAxes,
                size=15,
                horizontalalignment="right",
            )
            print(f"        END - Plot algorithm {algo_name}")
            print(f"        END - Run algorithm {algo_name}")
            print(f"    END - Run dataset # {i_dataset}")
            plot_num += 1

    print("END - Run each algorithm in each dataset")

    print(">>> - Save plot to PNG")

    # plt.show()
    plt.savefig("./data/example.png")

    print("END - Save plot to PNG")


def main(**context):
    """
    Obtiene los parametros necesarios para correr la deteccion de anomalias
    y luego invoca al metodo main_local para correr los algoritmos de deteccion
    """

    print(f"Context: {context} ")
    print(f"Context type: {type(context)} ")

    run_date = context["data_interval_start"]
    print(f"Execution Date:  {run_date} ")

    main_local(execution_date=run_date)


def main_local(execution_date):
    """
    Abre el archivo file_name y lo iter linea por linea sin cargarlo todo a memoria
    Instancia el modelo de deteccion de anormalidades
    Corre el modelo
    """
    # diccionario con key : aeropuerto -- value : diccionario por fecha
    # contiene el promedio del tiempo de demora de salida (columna
    # DEP_DELAY) por aeropuerto de salida (columna ORIGIN) y dia

    data_file_name = f"avg_{str(execution_date.year)}.csv"
    print(f"File name for input data:  {data_file_name} ")

    data_file_path = DATA_DIR + "/" + data_file_name

    algo_list = create_algorithms(ANSWER_TO_EVERYTHING, OUTLIERS_FRACTION)
    data_list = load_dataset(data_file_path)
    mesh_vec_xx, mesh_vec_yy = create_mesh_vectors()

    detect_outliers(algo_list, data_list, mesh_vec_xx, mesh_vec_yy)


if __name__ == "__main__":
    main_local(datetime.datetime(2007, 1, 1))
