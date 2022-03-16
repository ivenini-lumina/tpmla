"""Flight delay anomaly detection DAG."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

import calc_avg_delay as cad
import create_tables as ct
import insert_avg_delay as iad

# import fetch_prices as fp
# import plot_stocks as ps

with DAG(
    "flight_delay_dag",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2007, 1, 1),
    end_date=datetime(2007, 1, 2),
    catchup=True,
) as dag:
    create_tables = PythonOperator(task_id="create-tables", python_callable=ct.main)
    calc_avg_delay = PythonOperator(
        task_id="calc-avg-delay", python_callable=cad.main, provide_context=True
    )
    insert_avg_delay = PythonOperator(
        task_id="insert-avg-delay", python_callable=iad.main, provide_context=True
    )
    # detect_anomalies = PythonOperator(
    #    task_id="detect-anomalies", python_callable=cad.main, provide_context=True
    # )
    # fetch_prices = PythonOperator(task_id="fetch-prices", python_callable=fp.main)
    # plot_stocks = PythonOperator(
    #    task_id="plot-stocks", python_callable=ps.main, provide_context=True
    # )

    # deps = create_tables >> fetch_prices >> plot_stocks
    deps = create_tables >> calc_avg_delay >> insert_avg_delay
    print(f"Flight delay DAG dependencies {deps}")
