from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/test_dbt_pj"

with DAG(
    dag_id="dbt_before_cosmos",
    start_date=datetime(2026, 5, 23),
    schedule_interval=None,
    catchup=False,
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run_all",
        bash_command=f"cd {DBT_DIR} && dbt run",
    )