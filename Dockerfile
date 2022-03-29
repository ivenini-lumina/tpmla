RUN mkdir /opt/airflow/data
RUN mkdir /opt/airflow/conf
RUN chmod 755 /data
RUN chmod 755 /conf
#RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
#RUN unzip awscliv2.zip
#RUN sudo ./aws/install