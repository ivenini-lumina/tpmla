"""
    Modulo para obtener el archivo de datos
    Si ejecuta en modo "stand-alone" no hace nada
    Si ejecuta en modo "cloud" obtiene baja el archivo de s3
"""
import os

import commons as com
import boto3


def main(**context):
    """
    Obtiene el archivo de cfg
    Si el modo de ejecucion es "cloud" descarga el arhivo .csv desde s3
    """

    cfg = com.load_config()

    print(f"Context: {context} ")
    print(f"Context type: {type(context)} ")

    execution_date = context["data_interval_start"]
    print(f"Execution Date:  {execution_date} ")

    run_mode = cfg.get(com.ENV_CFG_SECTION, com.ENV_CFG_PROP_RUN_MODE)

    if run_mode == com.ENV_CFG_VAL_RUN_MODE_CLOUD:
        print("Cloud mode")

        data_file_name = str(execution_date.year) + ".csv"
        print(f"File name for input data:  {data_file_name} ")

        data_dir = cfg.get(com.FILE_CFG_SECTION, com.FILE_CFG_PROP_DATA_DIR)
        def_region = cfg.get(com.ENV_CFG_SECTION, com.ENV_CFG_PROP_DEF_REGION)

        s3_bucket_name = cfg.get(com.ENV_CFG_SECTION, com.ENV_CFG_PROP_S3_BUCKET)
        # s3_data_file_url = s3_bucket_name + "/" + data_file_name

        print(f"Getting file from bucket: {s3_bucket_name}")
        print(f"Data folder: {data_dir}")
        print(f"Region: {def_region}")

        creds = com.load_credentials()
        acces_key = creds.get(
            com.CRED_FILE_DEFAULT_SECTION, com.CRED_FILE_PROP_ACCESS_KEY_ID
        )
        secret_access = creds.get(
            com.CRED_FILE_DEFAULT_SECTION, com.CRED_FILE_PROP_SECRET_ACCESS_KEY
        )
        session_token = creds.get(
            com.CRED_FILE_DEFAULT_SECTION, com.CRED_FILE_PROP_SESSION_TOKEN
        )

        print(f"ak: {len(acces_key) * '*'}")
        print(f"sa: {len(secret_access) * '*'}")
        print(f"st: {len(session_token) * '*'}")

        s3_cli = boto3.client(
            "s3",
            aws_access_key_id=acces_key,
            aws_secret_access_key=secret_access,
            aws_session_token=session_token,
            region_name=def_region,
        )

        # En principio son iguales, se podria separar local de remoto
        local_file_path = f"{data_dir}/{data_file_name}"
        s3_file_location = f"{data_dir}/{data_file_name}"

        print("Download start")
        s3_cli.download_file(s3_bucket_name, s3_file_location, local_file_path)
        print("Download end")

        file_found = os.path.isfile(local_file_path)
        print(f"File download success: {file_found}")

    else:
        print("Stand-alone mode. Nothing to do")

    print("End task")
