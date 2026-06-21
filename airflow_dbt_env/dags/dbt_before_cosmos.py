import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/test_dbt_pj"

# Cosmos 移行前の実装 (BashOperator で dbt を直接実行する方式)
# 参照用として残しているが、本番では dbt_after_cosmos.py を使うこと
with DAG(
    dag_id="dbt_before_cosmos",
    # JST タイムゾーンを明示 (timezone-naive のままだと UTC 扱いになり実行時刻がずれる)
    start_date=pendulum.datetime(2026, 5, 23, tz=pendulum.timezone("Asia/Tokyo")),
    schedule_interval=None,
    catchup=False,
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run_all",
        bash_command=f"cd {DBT_DIR} && dbt run",
    )