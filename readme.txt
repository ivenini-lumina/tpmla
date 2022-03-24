*** AIRFLOW ***

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
    
3- Configurar en airflow una conexion a la base de datos postgres para persistencia
    id = flightsdb-conn
    type = postgres
    host = ip-database (puede ser una local para pruebas o una RDS)
    schema = flightsdb
    login = flightsusr
    password = flightsusr

*** AWS general config ***

VPC: 

id = vpc-0dd42b693835b8f63 | name = tp-mla-private-vpc | CIDR = 172.30.0.0/16
    * RDS - tp-mla-ivenini-flights-db - ip = 172.30.5.20
    * EC2 - administration instance - ip = 172.30.0.158 


Conectarse al EC2 desde el host local

    ssh -i tp-mla-ec2-keys.pem ubuntu@[ec2-host-name] (cambia cada vez que se reinicia)

Copiar archivos SQL para correr en la base hacia el EC2
    scp -i tp-mla-ec2-keys.pem ./tpmla/sql/create-db.sql ubuntu@[ec2-host-name]:~/.

Conectarse al RDS desde el EC2
    psql "host=tp-mla-ivenini-flights-db.cgtec7v8dxgd.us-east-1.rds.amazonaws.com port=5432 sslmode=disable dbname=flightsdb user=flightsusr password=flightsusr"

Correr un archivo SQL en el RDS desde el EC2
    psql -f [file.sql] -a "host=tp-mla-ivenini-flights-db.cgtec7v8dxgd.us-east-1.rds.amazonaws.com port=5432 sslmode=disable dbname=flightsdb user=flightsusr password=flightsusr"


- Acceso desde un host local (mi ip) hacia el EC2 de administration -> configurar security group / descargar .pem
- Acceso del EC2 hacia el RDS -> configurar security group

*** AWS S3 Sync ***
Sincronizar un directorio de un host con s3 para poder hacer upload de los datos

    - Conseguir archivo "credentials" con las credenciales para acceder mediante cli
    - Ejecutar script "upd-creds.sh" o copiar a mano el archivo al [home del usuario]/.aws
    - Ejecutar "syn-folder-s3.sh" para activar sincronizacion del directorio "data"
    con el bucket de s3


*** AWS S3 Quicksight ***

- Acceso desde quicksights hacia el RDS -> configurar VPC connections usando security group


Links a dashboard armado con quicksight

v1:
https://us-east-1.quicksight.aws.amazon.com/sn/accounts/671665414070/dashboards/db6cb275-6caa-4431-be20-f32ab83b612d?directory_alias=tp-mla-ivenini-quicksight-2

v2:
https://us-east-1.quicksight.aws.amazon.com/sn/accounts/671665414070/dashboards/b661ccf3-ae10-4c67-98f6-f7f3f75e78ba?directory_alias=tp-mla-ivenini-quicksight-2








