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
ENV_CFG_PROP_S3_BUCKET = "env.s3_data_bucket"
ENV_CFG_PROP_DEF_REGION = "env.default_region"

ENV_CFG_VAL_RUN_MODE_CLOUD = "cloud"
ENV_CFG_VAL_RUN_MODE_STAND_ALONE = "stand-alone"

FILE_CFG_SECTION = "FileSection"
FILE_CFG_PROP_DATA_DIR = "file.data_dir"

DATA_CFG_SECTION = "DataEngineeringSection"
DATA_CFG_PROP_ANOMALY_ALGORITHM = "data.anomaly_algorithm"
DATA_CFG_PROP_RANDOM_SEED = "data.random_seed"
DATA_CFG_PROP_CONTAMINATION = "data.contamination"

CONFIG_FILE_PATH = "conf/config.ini"
CREDENTIALS_FILE_PATH = "conf/credentials"

CRED_FILE_DEFAULT_SECTION = "default"

CRED_FILE_PROP_ACCESS_KEY_ID = "aws_access_key_id"
CRED_FILE_PROP_SECRET_ACCESS_KEY = "aws_secret_access_key"
CRED_FILE_PROP_SESSION_TOKEN = "aws_session_token"


def get_data_dir(cfg):
    """Get data directory"""
    data_dir = cfg.get(FILE_CFG_SECTION, FILE_CFG_PROP_DATA_DIR)
    return data_dir


def load_credentials():
    """Load credentials file"""
    return load_properties_file(CREDENTIALS_FILE_PATH)


def load_config():
    """Load configuration file"""
    return load_properties_file(CONFIG_FILE_PATH)


def load_properties_file(file_path):
    """Load properties file"""
    print(f"### Loading {file_path} file ###")
    cfg_file_name = file_path
    print(f"File name: {cfg_file_name}")
    file_found = os.path.isfile(cfg_file_name)
    print(f"File found: {file_found}")

    if file_found:
        config = configparser.RawConfigParser()
        config.read(cfg_file_name)
        print(f"Using file {cfg_file_name}")
        return config
    else:
        raise Exception(f"Could not find file {cfg_file_name}")
