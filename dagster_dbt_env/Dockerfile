FROM python:3.10-slim

# コンテナ内でGitコマンドを使えるようにするための準備
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# ★ 追加: Dagsterホームディレクトリをコンテナ内に作成する
RUN mkdir -p /opt/dagster/dagster_home

# Dagster、dbt、BigQuery用アダプターを一括インストール（バージョンはpyproject.tomlに合わせる）
RUN pip install --no-cache-dir \
    "dagster==1.13.8" \
    dagster-graphql \
    dagster-webserver \
    "dagster-dbt>=0.29.8" \
    "dbt-bigquery>=1.11.1" \
    "pandas>=2.3.3"

# コンテナ内の作業ディレクトリ（基準となる場所）を設定
WORKDIR /opt/dagster/app

# BigQueryの認証情報ファイルの場所をコンテナに教えてあげる環境変数
ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/keys/dbt-sa-key.json

EXPOSE 3000