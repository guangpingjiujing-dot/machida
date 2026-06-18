from datetime import timedelta
import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

# JST タイムゾーンを明示 (timezone-naive のままだと UTC 扱いになり実行時刻がずれる)
local_tz = pendulum.timezone("Asia/Tokyo")

# 1. ジョブの基本設定
default_args = {
    'owner': 'machida',
    'depends_on_past': False,
    # 本番では True にして障害時にアラートを受け取ること
    # 'email': ['data-alert@your-company.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 2. DAG（定期ジョブのまとまり）の定義
with DAG(
    'run_dbt_daily',
    default_args=default_args,
    description='Daily dbt run for test_dbt_pj',
    schedule_interval='@daily',
    # start_date に timezone を付与して UTC/JST のずれを防ぐ
    start_date=pendulum.datetime(2026, 5, 1, tz=local_tz),
    max_active_runs=1,  # 同時実行数を最大1つに制限（詰まり防止）
    catchup=False,
    tags=['dbt'],
) as dag:

    # 3. 実行するコマンド（dbt run）の定義
    #    profiles-dirに「.」を指定し、プロジェクト直下のprofiles.ymlを読み込ませます
    execute_dbt = BashOperator(
        task_id='dbt_run_task',
        bash_command='cd /opt/airflow/test_dbt_pj && dbt run --profiles-dir .',
    )

    execute_dbt