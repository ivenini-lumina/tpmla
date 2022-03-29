"""
    Modulo para subir los graficos generados a s3
    Si ejecuta en modo "stand-alone" no hace nada
    Si ejecuta en modo "cloud" sube los archivos del periodo a s3
"""
import os

import commons as com
import boto3


def main(**context):
    """
    Si el modo de ejecucion es "cloud" sube los archivos dentro del directorio
    {data_dir}/yyyy hacia s3
    """

    cfg = com.load_config()

    print(f"Context: {context} ")
    print(f"Context type: {type(context)} ")

    execution_date = context["data_interval_start"]
    print(f"Execution Date:  {execution_date} ")

    year = execution_date.year
    upload_enabled = True

    run_mode = cfg.get(com.ENV_CFG_SECTION, com.ENV_CFG_PROP_RUN_MODE)

    if run_mode == com.ENV_CFG_VAL_RUN_MODE_CLOUD:
        print("Cloud mode")

        if upload_enabled:

            data_dir = cfg.get(com.FILE_CFG_SECTION, com.FILE_CFG_PROP_DATA_DIR)
            # En principio son iguales, se podria separar local de remoto
            data_folder_local = f"{data_dir}/{str(year)}"
            data_folder_s3 = f"{data_dir}/{str(year)}"

            print(f"Data folder to get plot data:  {data_folder_local}")
            print(f"Remote folder in s3 for uploading:  {data_folder_s3}")

            def_region = cfg.get(com.ENV_CFG_SECTION, com.ENV_CFG_PROP_DEF_REGION)
            s3_bucket_name = cfg.get(com.ENV_CFG_SECTION, com.ENV_CFG_PROP_S3_BUCKET)

            print(f"Bucket for uploading: {s3_bucket_name}")
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

            print("<<< Credentials >>>")
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

            plot_file_extension = ".png"
            for plot_file_name in os.listdir(data_folder_local):
                if plot_file_name.endswith(plot_file_extension):
                    local_file_path = f"{data_folder_local}/{plot_file_name}"
                    s3_file_path = f"{data_folder_s3}/{plot_file_name}"

                    print(f"Upload start for file: {plot_file_name}")
                    s3_cli.upload_file(
                        local_file_path,
                        s3_bucket_name,
                        s3_file_path,
                    )
                    print(f"Upload end for file: {plot_file_name}")
                else:
                    print(f"Skipping file. Not a png: {plot_file_name}")
                    continue
        else:
            print("Upload disabled by configuration")
    else:
        print("Stand-alone mode. Nothing to do")

    print("End task")
