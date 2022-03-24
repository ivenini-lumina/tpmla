"""
    Modulo para detectar vuelos con demoras fuera de lo normal a nivel de aeropuerto
    Toma como input el archivo de salida de calc_avg_delay.py que tiene el promedio
    de demoras por fecha y aeropuerto
    Escribe como output un archivo XXXXX
"""
import os
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from postgres_client import PostgresClient
import commons as com


# Parametros de graficos
PLOT_EXPECTED_MIN_X = 1
PLOT_EXPECTED_MAX_X = 366

# TODO Calcular estos valores en base a los datos de los vuelos
PLOT_EXPECTED_MIN_Y = -100
PLOT_EXPECTED_MAX_Y = 650

# Parametros de configuracion de algoritmos
ALGO_COVARIANCE_NAME = "Robust Covariance"
ALGO_COVARIANCE_IDX = 0
ALGO_FOREST_NAME = "Isolation Forest"
ALGO_FOREST_IDX = 1


def create_mesh_vectors():
    """Ver que hace esto"""
    # Compare given classifiers under given settings
    # TODO Ver que hace esto y si hace falta calcular el numero de puntos en funcion de los datos
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
        (ALGO_COVARIANCE_NAME, EllipticEnvelope(contamination=anomaly_percent)),
        (
            ALGO_FOREST_NAME,
            IsolationForest(contamination=anomaly_percent, random_state=random_seed),
        ),
    ]
    return anomaly_algorithms


def load_dataset(dic_key, year):
    """
    Carga el archivo file_name y lo itera linea por linea sin cargarlo todo a memoria
    Genera una lista que tiene un array con los datos para luego alimentar a los algoritmos de
    deteccion de anomalias
    """
    outlier_list = []
    outlier_sub_list = []
    outlier_list.append(outlier_sub_list)

    dataset_dic = {}

    client = PostgresClient()

    first_day = datetime.datetime(year, 1, 1)
    last_day = datetime.datetime(year, 12, 31)

    print(f"Fetching avg delay data for year {year} from DB")

    query_result = client.get_avg_delay_for_date_range(
        from_date=first_day, to_date=last_day
    )
    data_list_from_db = query_result

    debug_log = False

    for idx, db_row in enumerate(data_list_from_db):
        # id
        fl_id = db_row[0]

        # fecha y numero de dia
        fl_date = db_row[1]
        day_of_year = (fl_date - datetime.date(fl_date.year, 1, 1)).days + 1

        # demora promedio
        dep_delay = db_row[2]

        transformed_row = [day_of_year, dep_delay]

        numpy_row = np.array([day_of_year, dep_delay, fl_id])

        if debug_log:
            print(f"#{idx}: --> {db_row} --> {transformed_row} --> {numpy_row}")

        out_sublist = outlier_list[0]
        out_sublist.append(numpy_row)

    dataset_list = []
    result_sub_array = np.array(out_sublist)
    print(f"Data set loaded: {result_sub_array}")
    dataset_list.append(result_sub_array)

    dataset_dic[dic_key] = dataset_list

    return dataset_dic


def detect_outliers(data_key, anomaly_algorithms, datasets, xx_param, yy_param, cfg):
    """
    - Corre los algoritmos para detectar outliers y grafica el resultado
    - Recibe un diccionario de datasets. La key es str y corresponde al codigo
    del aeropuerto. El valor de cada entrada es una lista con los valores
    [numero_dia - int , demora promedio - float]
    - El valor numero_dia es un valor entre 1 a 366
    - Puede recibir varios datasets a iterar y por cada dataset genera
    un grafico con los resultados de cada algoritmo usado
    - Se genera un archivo de salida png por cada dataset procesado
    - Existen dos modos de ejecucion. Se puede recibir un solo dataset
    que tiene los datos de todos los aeropuertos juntos o sino
    puede recibirse un dataset por cada aeropuerto
    """

    year_string = data_key[0:4]
    year = int(year_string)

    print(">>> - Run each algorithm in each dataset")

    for i_dataset, data_vec_x in enumerate(datasets):
        print(
            f"    >>> - Start Running Dataset # {i_dataset} with size: {len(data_vec_x)}"
        )
        print(f"    >>> - Data: {data_vec_x}")
        # Remover columna id del set de datos para train
        data_vec_without_id_x = data_vec_x[:, [0, 1]]
        print(f"    >>> - Data without id column: {data_vec_without_id_x}")

        plot_num = 1

        # TODO tomar tiempos de cada parte y ver si se puede omitir alguna
        for algo_name, algorithm in anomaly_algorithms:
            fit_start_time = time.time()
            print(f"    >>> - Algorithm {algo_name} fit START")
            algorithm.fit(data_vec_without_id_x)
            fit_end_time = time.time()
            print(f"    END - Algorithm {algo_name} fit END")
            plt.subplot(len(datasets), len(anomaly_algorithms), plot_num)
            if i_dataset == 0:
                plt.title(f"{data_key} -- {algo_name}", size=15)

            print(f"        >>> - Run algorithm {algo_name} for key={data_key}")

            # fit the data and tag outliers
            if algo_name == "Local Outlier Factor":
                print(f"INPUT data to predict: {data_vec_without_id_x}")
                y_pred = algorithm.fit_predict(data_vec_without_id_x)
                print(f"OUTPUT prediction: {y_pred}")
            else:
                print(f"INPUT data to predict: {data_vec_without_id_x}")
                y_pred = algorithm.fit(data_vec_without_id_x).predict(
                    data_vec_without_id_x
                )
                print(f"OUTPUT prediction: {y_pred}")

            print(f"        >>> - Plot algorithm {algo_name} for key={data_key}")

            # plot the levels lines and the points
            if algo_name != "Local Outlier Factor":  # LOF does not implement predict
                print("        >>> - Draw contour")
                ravel_xx = xx_param.ravel()
                ravel_yy = yy_param.ravel()
                point_xy = np.c_[ravel_xx, ravel_yy]
                print(f"Contour PARAM X # : {len(xx_param)} --> {xx_param.shape}")
                print(f"Contour PARAM X: {xx_param}")
                print(f"Contour PARAM Y # : {len(yy_param)} --> {yy_param.shape}")
                print(f"Contour PARAM Y: {yy_param}")
                print(f"Contour RAVEL X #: {len(ravel_xx)} --> {ravel_xx.shape}")
                print(f"Contour RAVEL X: {ravel_xx}")
                print(f"Contour RAVEL Y #: {len(ravel_yy)} --> {ravel_yy.shape}")
                print(f"Contour RAVEL Y: {ravel_yy}")
                print(f"Contour INPUT XY #: {len(point_xy)} --> {point_xy.shape}")
                print(f"Contour INPUT XY: {point_xy}")

                prediction_vec_z = algorithm.predict(point_xy)
                print(
                    f"RAW PREDICTION Z # {len(prediction_vec_z)} --> {prediction_vec_z.shape}"
                )
                print(f"RAW OUTPUT Z: {prediction_vec_z}")
                prediction_vec_z = prediction_vec_z.reshape(xx_param.shape)
                print(
                    f"RESHAPE PREDICTION Z # {len(prediction_vec_z)} --> {prediction_vec_z.shape}"
                )
                print(f"Contour FINAL OUTPUT Z: {prediction_vec_z}")
                plt.contour(
                    xx_param,
                    yy_param,
                    prediction_vec_z,
                    levels=[0],
                    linewidths=2,
                    colors="black",
                )

            colors = np.array([com.COLOR_CERULEAN, com.COLOR_ORANGE])
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

            # Agregar al grafico el tiempo que ha llevado el training del algoritmo
            elapsed_fit_time = fit_end_time - fit_start_time
            elapsed_fit_time_str = (f"{elapsed_fit_time:.2f} sec").lstrip("0")

            plt.text(
                0.99,
                0.01,
                elapsed_fit_time_str,
                transform=plt.gca().transAxes,
                size=15,
                horizontalalignment="right",
            )
            print(f"        END - Plot algorithm {algo_name} for key={data_key}")
            print(f"        END - Run algorithm {algo_name} for key={data_key}")

            print(f"Original array: {data_vec_x} --> {data_vec_x.shape}")
            print(f"Predicted array: {y_pred} --> {y_pred.shape}")

            print(f"Inlier count {(y_pred == 1).sum()}")
            print(f"Outlier count {(y_pred == -1).sum()}")

            first_day = datetime.datetime(year, 1, 1)
            last_day = datetime.datetime(year, 12, 31)

            client = PostgresClient()
            client.bulk_update(data_vec_x, y_pred, first_day, last_day)

            print(f"    END - Run dataset # {i_dataset}")
            plot_num += 1

    print("END - Run each algorithm in each dataset")

    print(">>> - Save plot to PNG")

    # Guardar en un directorio el grafico de la comparacion de algoritmos

    data_dir = com.get_data_dir(cfg)

    if not os.path.exists(data_dir):
        # Create a new directory because it does not exist
        os.makedirs(data_dir)

    png_file_path = f"{data_dir}/{data_key}.png"
    plt.savefig(png_file_path)

    print(f"END - Save plot to PNG for {data_key} in file: {png_file_path}")


def main(**context):
    """
    Obtiene los parametros necesarios para correr la deteccion de anomalias
    y luego invoca al metodo "main_local" para correr los algoritmos de deteccion
    """

    print(f"Context: {context} ")
    print(f"Context type: {type(context)} ")

    run_date = context["data_interval_start"]
    print(f"Execution Date:  {run_date} ")

    main_local(execution_date=run_date)


def main_local(execution_date):
    """
    Proposito: Generar un archivo png graficando los vuelos por cada aeropuerto en un periodo anual
    En el grafico se identifican los vuelos con demoras promedio y los vuelos con demoras anomalas
    trazando una frontera divisoria mediante una linea separadora

    * Primero: Inicializa los algoritmos de deteccion
    * Segundo: Abre el archivo de datos "avg_XXX.csv" correspondiente al campo "year" del parametro
    execution_date y genera un diccionario con  key = aeropueto y value = lista de vuelos
    por fecha para ese aeropuerto. Se puede tambien generar un diccionario con key = "ALL_AEP" que
    en lugar de una lista por aeropuerto tenga uns sola key con todos los datos del periodo
    combinando todos los aeropuertos
    * Tercero: Genera una estructura de datos de vectores "mesh" para trazar las fronteras entre
    inliers y outliers
    * Cuarto: Invocan a "detect_outliers" que se encarga de correr los algoritmos de anomalias y
    generar el grafico correspondiente
    """

    cfg = com.load_config()
    anomaly_algorithm = cfg.get(
        com.DATA_CFG_SECTION, com.DATA_CFG_PROP_ANOMALY_ALGORITHM
    )
    random_seed = int(cfg.get(com.DATA_CFG_SECTION, com.DATA_CFG_PROP_RANDOM_SEED))
    contamination = float(
        cfg.get(com.DATA_CFG_SECTION, com.DATA_CFG_PROP_CONTAMINATION)
    )

    # 0) TODO Agregar que se borren las anomalias de la base al empezar

    # 1) Inicializar algoritmos
    algo_list = create_algorithms(random_seed, contamination)

    if anomaly_algorithm == ALGO_COVARIANCE_NAME:
        algo_idx = ALGO_COVARIANCE_IDX
    elif anomaly_algorithm == ALGO_FOREST_NAME:
        algo_idx = ALGO_FOREST_IDX

    # 2) Localizar archivo de datos a procesar. Un archivo contiene los datos de un periodo anual
    year_str = str(execution_date.year)
    aep_dic_key = year_str + "__" + "ALL_AEP"
    data_dic = load_dataset(dic_key=aep_dic_key, year=execution_date.year)

    # 3) Generacion de mesh vectors
    mesh_vec_xx, mesh_vec_yy = create_mesh_vectors()

    # 4) Invocar corrida de algoritmos de deteccion y graficacion
    for idx_aep, key_aep in enumerate(data_dic):
        data_list = data_dic.get(key_aep)
        print(f"START outlier detection for #{idx_aep} key={key_aep}")
        detect_outliers(
            key_aep, [algo_list[algo_idx]], data_list, mesh_vec_xx, mesh_vec_yy, cfg
        )
        print(f"END outlier detection for #{idx_aep} key={key_aep}")


if __name__ == "__main__":
    # solo para pruebas locales sin airflow
    main_local(datetime.datetime(2007, 1, 1))
