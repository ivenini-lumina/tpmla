""" Common utility code """
import configparser
import os.path

COLOR_CERULEAN = "#377eb8"  # outliers
COLOR_ORANGE = "#ff7f00"  # inliers

COLOR_GREEN = "#b6d7a8"  # inliers
COLOR_RED = "#ff0000"  # outliers

# Constantes de indices del archivo de promedio de demoras "avg_yyyy.csv"
AVG_FILE_AEP_CODE_IDX = 0
AVG_FILE_FL_DATE_IDX = 1
AVG_FILE_AVG_DELAY_IDX = 2
AVG_FILE_NBR_FLIGHTS_IDX = 3

ENV_CFG_SECTION = "EnvironmentSection"
ENV_CFG_PROP_RUN_MODE = "env.run_mode"

FILE_CFG_SECTION = "FileSection"
FILE_CFG_PROP_DATA_DIR = "file.data_dir"

DATA_CFG_SECTION = "DataEngineeringSection"
DATA_CFG_PROP_ANOMALY_ALGORITHM = "data.anomaly_algorithm"
DATA_CFG_PROP_RANDOM_SEED = "data.random_seed"
DATA_CFG_PROP_CONTAMINATION = "data.contamination"


def get_data_dir(cfg):
    """Get data directory"""
    data_dir = cfg.get(FILE_CFG_SECTION, FILE_CFG_PROP_DATA_DIR)
    return data_dir


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
