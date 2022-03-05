"""Flight delay anomaly detection DAG."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

import calc_avg_delay as cad

# import fetch_prices as fp
# import plot_stocks as ps

with DAG(
    "flight_delay_dag",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2007, 1, 1),
    end_date=datetime(2007, 1, 31),
    catchup=True,
) as dag:
    calc_avg_delay = PythonOperator(
        task_id="calc-avg-delay", python_callable=cad.main, provide_context=True
    )
    detect_anomalies = PythonOperator(
        task_id="detect-anomalies", python_callable=cad.main, provide_context=True
    )
    # fetch_prices = PythonOperator(task_id="fetch-prices", python_callable=fp.main)
    # plot_stocks = PythonOperator(
    #    task_id="plot-stocks", python_callable=ps.main, provide_context=True
    # )

    # deps = create_tables >> fetch_prices >> plot_stocks
    deps = calc_avg_delay
    print(f"Flight delay DAG dependencies {deps}")
