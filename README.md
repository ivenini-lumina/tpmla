# TP ML Engineering
### ITBA - Cloud Data Engineering

## Problema a resolver
Se debe procesar con periodicidad anual un conjunto de datos de vuelos de avión que comprende los años 2009 a 2018. Link al set de datos: https://www.kaggle.com/yuanyuwendymu/airline-delay-and-cancellation-data-2009-2018?select=2009.csv

Luego del procesamiento de esos datos se debe generar la siguiente información:
- Un registro por cada día del año y aeropuerto que contenga la cantidad de vuelos para ese día,
la demora promedio y un indicador que diga si la demora experimentada ese día fue anómala o no.
- Un gráfico por cada aeropuerto donde se pueda visualizar la información anterior en una estructura
de archivos que permita identificar de manera sencilla el año y aeropuerto del que se trata.

## Análisis general y contexto
El trabajo lo encarga una pequeña empresa de viajes. Se trata de la primera incursión de dicha empresa en lo
referente a ingeniería de datos. Se busca que con este trabajo sea posible convencer a la empresa de la 
importancia de los datos a modo de lograr futuras inversiones en este sentido. Puesto que por el momento las
inversiones en este aspecto son pequeñas se pide que la solución adoptada pueda correr en una computadora
propia hasta tanto se consigan mayores inversiones.
De la naturaleza del problema a resolver también se desprende que a grandes rasgos la solución contaría
de una parte de procesamiento de datos, una parte de almacenamiento y una parte de visualización/reportería. 
- **Procesamiento:** Esta parte correrería solamente una vez al año. El volumen de datos a procesar como entrada, en un análisis preliminar es de alrededor de 6 millones y medio de registros por año. Una tarea de este estilo se 
puede completar en una cuestion de un par de horas sin contar con gran capacidad de procesamiento. Cabe esperar entonces que esta parte no necesite de tanto poder de computo ni represente un gran porcentaje del costo final de la solución. Sin embargo, se debe tener en cuenta la posibilidad de que el volumen aumente, por lo que se debe considerar también una solucion que presente cierta flexibilidad para escalamiento en caso de ser necesario.
- **Almacenamiento:** Abarcaría tanto a los datos de entrada como a la información procesada. Es probable que se necesite almacenar y tal vez acceder a ambos duránte todo el año. En mantenimiento de la base de datos probablemente sea la responsable del mayor porcentaje de costo de la solución, con lo cual posiblemente sea la parte que más importancia convenga optimizar. 
- **Visualización/Reportería:** Esta parte probablemente sea utilizada con intensidad durante algunos meses en el año
y no tanto en el resto. Por lo tanto, no sería conveniente adoptar alguna solución que requiera mucho mantenimiento anual sino más bien algo que pueda manejar las ráfagas de mayor uso de manera eficiente sin gran cantidad de costos fijos asociados.   

## Arquitectura desarrollada
Considerando la naturaleza del problema a resolver y además los factores del apartado anterior la arquitectura de solución desarrollada se describe a continuación:

![Alt text](Arquitectura-Arquitectura.png?raw=true "Title")

**Base de datos:** Servicio RDS de tipo postgresql ya que era un requerimiento. En principio se encuentra en una AZ
como se ve en el digrama pero parcialmente usa además al menos una AZ adicional para ciertas cuestiones de mantenimiento debido a la manera en que funciona el servicio de RDS. Si fuera necesario un deploy multi AZ por 
requerir mayor disponibilidad, redundancia o tolerancia a fallos, esta parte de la arquitectura se podría adaptar
con mínimas modificaciones. Se encuentra en una subred privada y no puede ser accedida de manera pública. 
Un aspecto positivo del uso de RDS con postgresql en lugar de otras opciones más especificas como Aurora que podría ser menos costosa, es que existe menor dependencia del cloud provider en este aspecto, en caso de necesitar mudar de proveedor en algun momento.

**Bucket para archivo en S3:** Se utiliza un bucket para almacenar tanto los archivos .csv con los datos de entrada
para procesar asi como también para almacenar los gráficos generados al final de la etapa del procesamiento de 
datos en una estructura de carpetas por año. Si fuera necesario separar estos dos usos en dos buckets diferentes, eso se podría hacer de manera sencilla también sin que el cambio implique un gran impacto en el sistema en su conjunto. Este bucket tampoco tiene acceso público. 

**Bastion host:** Este host se encuentra en la subred pública y puede ser accedido desde internet desde una IP propia conocida únicamente. Se usa para acceder o administrar el resto de los componentes. Esto permite que el acceso a los componentes desde el exterior esté limitado a un solo punto para disminuir posibles riesgos de seguridad.

**Worker:** Este componente se encarga de correr Airflow y hacer el procesamiento de los datos utilizando para esto contenedores. Toma desde s3 el archivo de entrada, inserta en la base de datos en RDS los registros y sube a s3 los gráficos generados. Se encuentra en una red privada  y solo puede recibir conexiones entrantes desde la VPC pero cuenta con acceso a internet para actualizaciones, mantenimiento o instalación de paquetes mediante el NAT gateway de la subred pública. El procesamiento de datos puede correr de manera sencilla en una computadora propia
también y no solo en cloud debido al uso de contenedores. Adicionalmente, para usos de desarrollo y pruebas locales es posible correr en modo "stand-alone" mediante archivo de configuración el cual permite que no se necesite acceso a s3 para tomar los datos de entrada o subir los gráficos de salida (se puede tomar o dejar los archivos de un directorio local) ni acceso al RDS (puede usarse una base de datos que viene creada dentro del container). Para la parte del algoritmo de detección de anomalias se eligió usar scikit-learn en lugar de SageMaker porque permite que esa parte tenga independencia respecto del cloud provider y mayor visibilidad acerca de cómo está implementada la funcionalidad. El resto de los paquetes python necesarios son matplotlib para la creación de los gráficos y boto3, necesario para acceder a los servicios de AWS desde python. 
En caso de que creciera el volumen de datos a procesar y fuera necesario mayor poder de procesamiento, escalabilidad o tolerancia a fallos en esta parte, se podrían hacer adaptaciones para pasar a ejecutar esto mediante el servicio manejado por AWS MWAA. Al ser Airflow también una herramienta abierta, este componente facilita un poco el cambio de cloud provider en caso de ser necesario eventualmente.

**Quicksight:** Esta herramienta permite la visualizacion de la información procesada. Puede acceder a los datos del RDS y en caso de ser necesario también al s3. No requiere el manejo de servidores y demás cuestiones de mantenimiento que podrían no justificar los costos asociados. Debido a la necesidad de  uso esperada de la información, estas son caracteristicas apropiadas ya que además provee alta disponibilidad y escalabilidad en caso de ser necesaria en algun periodo de alta actividad y el costo asociado es en función del uso que se le de. Si bien es una herramienta específica de AWS, esta parte representa un porcentaje significativamente pequeño 
del esfuerzo total requerido para montar todo el sistema por lo que si hubiera necesidad de migrar a otro cloud provider, no sería tan costosa esa migración asociada a esta parte respecto del total.

## Flujo de datos
![Alt text](Arquitectura-FlujoDatos.png?raw=true "Title")

1) Los datos originales de entrada se encuentran en s3 en un archivo CSV. Son tomados de s3 por el Worker para generar datos agrupados por día y aeropueto
2) Los datos agrupados se insertan en la base de datos en la tabla "fligth_avg_delay"
3) Los datos de todo el año se leen para alimentar al algoritmo de detección de anomalías. 
4) Con la salida del algoritmo de detección se hace update de la columna "anomaly" en la base de datos para cada día
5) Por cada aeropuerto, se toman los datos de cantidad de vuelos, fecha y la marca de si es anómalo ese día o no. Se genera el gráfico correspondiente a ese aeropuerto usando esos datos
6) Se suben los gráficos en formato PNG al bucket de s3 en una carpeta referente al año analizado
7) Una vez que se tienen los datos en la base de datos y los gráficos generados, se puede usar Quicksight para visualizar la información en un dashboard

## Configuración
- Red: Se debe crear una VPC que contenga una Internet Gateway, una subred pública con un NAT Gateway y al menos 2 subredes privadas, cada una en diferente AZ. Las tablas de ruteo de las subredes privadas deben tenen la entrada 0.0.0.0 apuntando al NAT Gateway para poder iniciar conexiones salientes a internet desde los componentes de esa subred
- Bastion: Ubicarlo en la subred pública y habilitar conexiones entrantes al mismo solamente desde una IP propia conocida a nivel security group. 
- RDS: Hacer un grupo de subredes que contenga a las subredes privadas y luego crear la instancia RDS. Colocar la base de datos en ese grupo de subredes. Deshabilitar el acceso público. Conectarse al RDS y correr el archivo "create-db.sql" para generar la base de datos de vuelos y el usuario asociado
- Worker: Colocarlo en la subred privada que sea de la misma AZ donde se encuentra el RDS. Desde el Bastion host conectarse al Worker para configurar e instalar todo lo necesario como scripts de python, dockerfiles, shell scripts y archivos de configuración como el "config.ini". Configurar en Airflow la conexión a la base de datos
- Bucket: Crear un bucket y crear una carperta "data" donde se deberán subir todos los archivos .csv con los datos de entrada con nombre yyyy.csv donde yyyy identifica al año. Crear además una subcarpeta dentro de data por cada año. 
- Quicksight: Para poder acceder a los datos del RDS se debe primero crear una conexión VPC y asignarle un security group que permita el acceso al RDS

### Archivo config.ini
Archivo de configuración donde se ingresan ciertos parámetros. Se encuentra en la carpeta "conf"

Modo de ejecución "cloud" en caso de correr con conexion a s3 o "stand-alone" para correr sin interacción con s3

    #env.run_mode=stand-alone
    env.run_mode=cloud

Region de AWS y nombre del bucket a usar

    env.default_region=us-east-1
    env.s3_data_bucket=data-bucket-tp-mla-ivenini

Configuración de algoritmos de anomalías. Se encuentran implementados el algoritmo "Robusut Covariance" que parece funcionar de manera más precisa para identificar las anomalías pero toma mucho mas tiempo de corrida que el otro algoritmo implmentado "Isolation Forest". El factor de contaminación o porcentaje de outliers normalmente esperado en los datos fue seteado en 0.06 segun un análisis exploratorio de los datos. Ver sección al respecto. El parámetro de random seed se setea en 42 por razones conocidas.

    #data.anomaly_algorithm=Robust Covariance
    data.anomaly_algorithm=Isolation Forest
    data.random_seed=42
    data.contamination=0.06

### Archivo credentials
En la carpeta "conf" se debe crear una archivo llamado "credentials" con el mismo formato que se usa para la AWS CLI que contenga los valores de "aws_access_key_id", "aws_secret_access_key" y "aws_session_token"

## Análisis Exploratorio de datos
Haciendo un análisis exploratorio de los datos se obtiene lo siguiente:
Cada archivo de datos de entrada contiene alrededor de 6 millones de registros que luego de ser agrupados por aeropuerto genera alrededor de 100.000 registros. Analizando luego esto datos agregados para el año 2009 se puede obtener lo siguiente:

![Alt text](exploratory00.png?raw=true "Title")

![Alt text](exploratory01.png?raw=true "Title")

![Alt text](exploratory02.png?raw=true "Title")

Como se puede ver en el cuadro y en el histograma, alrededor de un 71% de los datos presentan una demora promedio de entre -20h y +5h. Otro 23% se encuentra entre +5h y +30h y todo el resto corresponde a otros valores. De aquí podemos obtener que un valores de entre el 5% y 6% de anomalías resuelta adecuado y eso es lo que se usa para el valor del parámetro "contamination" del algoritmo de detección de anomalías

Una vez determinado un valor para el parámetro "contamination" se puede usar para evaluar cuál algoritmo de detección de los que ofrece scikit-learn es el más adecuado para el caso. Sería de esperar que la demora promedio de la gran mayoría de los datos (inliers) estuvieran concentrados en valores cercanos a 0 y que los datos anómalos (outliers) estuvieran alejados del 0 y que esto se repitiera a los largo de todo el periodo de tiempo analizado. El resultado de varios algoritmos de detección de anomalías se puede ver en la siguiente figura, en la cual se grafican en naraja los puntos inliers y en celeste los outliers siendo el eje horizontal el que corresponde al día del año y el eje vertical a la demora promedio:

![Alt text](outlier_algorithm.png?raw=true "Title")

Se puede ver que los algoritmos que mejor resutado arrojan son el "Robust Covariance" y el "Isolation Forest". El resto no parecen arrojar resultados adecuados. Además se puede ver que el "Isolation Forest" tarda significativamente menos tiempo en correr que el "Robust Covariance" aunque parece ser un poco menos preciso. A raíz de este análisis se decide implementar los dos algoritmos más apropiados y la posiblidad de seleccionar cuál usar mediante un archivo de configuración. 

## Resultados finales
Los gráficos de cada aeropuerto indicando en número de vuelos y la marca de anomalías se generan con un formato como el del ejemplo que sigue, indicando en verde los días normales y en rojo lo que tienen demoras anormales: 

![Alt text](LAX.png?raw=true "Title")

Una muestra del Dashboard armado en Quicksight a continuación:

![Alt text](dashboard01.png?raw=true "Title")

![Alt text](dashboard02.png?raw=true "Title")

![Alt text](dashboard03.png?raw=true "Title")


