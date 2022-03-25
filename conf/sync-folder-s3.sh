#/bin/bash
# activa la sincronizacion entre la carpeta data local y s3
aws s3 sync ./data s3://data-bucket-tp-mla-ivenini/data/

