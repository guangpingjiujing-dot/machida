# 1. ベースとしてApache Airflowの公式イメージ（Python3.11環境）を使用
FROM apache/airflow:2.9.1-python3.11

# 2. 一時的に管理者権限（root）に切り替えて、Linuxの必要なツールをアップデート
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. 再びAirflowユーザーに戻す（セキュリティと実行権限のため）
USER airflow

# 4. Airflowの環境内に、BigQuery用のdbt（dbt-bigquery）をインストール
#    ※これによってAirflowのタスクから直接dbtが叩けるようになります
RUN pip install --no-cache-dir dbt-bigquery