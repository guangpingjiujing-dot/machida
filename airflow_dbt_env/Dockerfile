FROM apache/airflow:2.9.1

USER root

# 1. コンパイルに必要なシステムパッケージを入れ、さらに一時フォルダ(/tmp)の権限を解放
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && chmod 777 /tmp \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# 2. pipを最新化
RUN pip install --no-cache-dir --upgrade pip

# 3. バージョンパニックを防ぐための指定インストール
RUN pip install --no-cache-dir \
    "google-cloud-aiplatform>=1.127.0" \
    "google-cloud-bigquery>=3.26.0" \
    gcloud-aio-bigquery

# 4. Airflow Cosmos と dbt-bigquery をインストール
RUN pip install --no-cache-dir "astronomer-cosmos[dbt-bigquery]"