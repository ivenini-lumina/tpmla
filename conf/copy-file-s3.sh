#/bin/bash
# Descarga un archivo desde s3 al directorio local

# aws s3 cp s3://data-bucket-tp-mla-ivenini/data/2007.csv .

# $1 = <LocalPath> or <S3Uri>
# $2 = <LocalPath> or <S3Uri>

echo "Param 1"
echo $1
echo "Param 2"
echo $2

aws s3 cp $1 $2