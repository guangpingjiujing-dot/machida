FROM apache/airflow:2.9.1

USER root

# 1. コンパイルに必要なシステムパッケージを入れ、さらに一時フォルダ(/tmp)の権限を解放
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && chmod 777 /tmp \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# pip を最新化してから requirements.txt を一括インストール
# 本番では requirements.txt のバージョンを "==" で固定すること
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt