#/bin/bash
# ejecuta el dag para hacer backfill
airflow dags backfill --start-date 2007-01-01T00:00:00+00:00 --end-date 2007-01-31T00:00:00+00:00 flight_delay_dag
