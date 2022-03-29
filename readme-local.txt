Copiar archivos SQL para correr en la base hacia el EC2

    scp -i tp-mla-ec2-keys.pem ./tpmla/sql/create-db.sql ubuntu@ec2-67-202-5-192.compute-1.amazonaws.com:~/.
    scp -i tp-mla-ec2-keys.pem ./tpmla/sql/db.sql ubuntu@ec2-67-202-5-192.compute-1.amazonaws.com:~/.
