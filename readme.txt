Se usa la imagen de airflow 2.2.0 la cual viene con las siguientes versiones que se pueden instalar 
usando poetry (menos la version de python 3.6.15)
    python 3.6.15
    apache-airflow                           2.2.0
    apache-airflow-providers-docker          2.2.0
    apache-airflow-providers-postgres        2.3.0
    SQLAlchemy                               1.3.24
    SQLAlchemy-JSONField                     1.0.0
    SQLAlchemy-Utils                         0.37.8

Si el file docker-compose.yaml no puede ser interpretado por docker compose
puede ser necesario migrar a una version mas nueva de compose
Con la version 1.29.2 se puede correr (con la que viene al instalar docker en ubuntu, 1.25.x, no corre)

1- Setear el user id en el archivo .env
    echo -e "AIRFLOW_UID=$(id -u)" > .env

2- Credenciales: 
    airflow web -> airflow : airflow @ lolcahost:8080
    adminer web db=stocksdb -> flightsusr : flightsusr @ local-ip:9080 
    adminer web db=airflow -> airflow : airflow @ local-ip:9080 
    
3- Configurar en airflow una conexion a la base de datos postgres stocksdb
    id = flightsdb-conn
    type = postgres
    host = local-ip
    shcema = flightsdb
    user : pass = flightsusr : flightsusr


