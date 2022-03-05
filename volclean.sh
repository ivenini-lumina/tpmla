#/bin/bash
# baja todos los servicios y borra los datos de los volumenes (no borra las imagenes)
poetry run docker-compose down --volumes
