""" Common utility code """
import configparser
import os.path

# Directorios

# TODO extrer a una funcion el directorio data
DATA_DIR = "data"

COLOR_CERULEAN = "#377eb8"  # outliers
COLOR_ORANGE = "#ff7f00"  # inliers

COLOR_GREEN = "#b6d7a8"
COLOR_RED = "#ff0000"

# Constantes de indices del archivo de promedio de demoras "avg_yyyy.csv"
AVG_FILE_AEP_CODE_IDX = 0
AVG_FILE_FL_DATE_IDX = 1
AVG_FILE_AVG_DELAY_IDX = 2
AVG_FILE_NBR_FLIGHTS_IDX = 3


def load_config():
    """Load config file"""
    print("### Loading configuration file ###")
    cfg_file_name = "dags/config.ini"
    print(f"Config file name: {cfg_file_name}")
    file_found = os.path.isfile(cfg_file_name)
    print(f"File found: {file_found}")

    if file_found:
        config = configparser.RawConfigParser()
        config.read(cfg_file_name)
        print(f"Using configuration file {cfg_file_name}")
        return config
    else:
        raise Exception(f"Could not find configuration file {cfg_file_name}")
