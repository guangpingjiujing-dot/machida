from airflow import DAG
from datetime import datetime

# 動作確認用の空 DAG
# 本番環境ではスキャン対象のノイズになるため削除すること
with DAG(
    dag_id="test_dag_simple",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    pass