#/bin/bash
# baja todos los servicios, borra los datos de los volumenes y ademas borra todas las imagenes
poetry run docker-compose down --volumes --rmi all
