from airflow import DAG
from datetime import datetime

with DAG(
    dag_id="test_dag_simple",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    pass