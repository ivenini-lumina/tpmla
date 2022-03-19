"""Flight delay anomaly detection DAG."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

import calc_avg_delay as cad
import create_tables as ct
import insert_avg_delay as iad
import detect_outliers as do
import plot_outliers as po


with DAG(
    "flight_delay_dag",
    # TODO implementar schedule anual
    schedule_interval=timedelta(days=1),
    start_date=datetime(2007, 1, 1),
    end_date=datetime(2007, 1, 1),
    catchup=True,
) as dag:
    create_tables = PythonOperator(task_id="create-tables", python_callable=ct.main)
    calc_avg_delay = PythonOperator(
        task_id="calc-avg-delay", python_callable=cad.main, provide_context=True
    )
    insert_avg_delay = PythonOperator(
        task_id="insert-avg-delay", python_callable=iad.main, provide_context=True
    )
    detect_outliers = PythonOperator(
        task_id="detect-outliers", python_callable=do.main, provide_context=True
    )
    plot_outliers = PythonOperator(
        task_id="plot-outliers", python_callable=po.main, provide_context=True
    )

    deps = (
        create_tables
        >> calc_avg_delay
        >> insert_avg_delay
        >> detect_outliers
        >> plot_outliers
    )
    print(f"Flight delay DAG dependencies {deps}")
