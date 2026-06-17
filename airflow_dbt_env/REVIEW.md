# airflow_dbt_env コードレビュー

レビュー日: 2026-06-17

---

## 総評

ローカル開発・学習用途として必要な構成は整っている。ただし本番運用を想定すると、セキュリティ・可用性・運用監視の面で対処が必要な点が複数ある。以下に優先度別でまとめる。

---

## 🔴 Critical（本番リリース前に必ず対処）

### 1. シークレット類のハードコード (`docker-compose.yml`)

```yaml
# 現状
- AIRFLOW__CORE__FERNET_KEY=FB1c1ZsR2HiaNJD3LceY_2wOfb96A-N-v6U-e74_p9w=
- POSTGRES_PASSWORD=airflow
- _AIRFLOW_WWW_USER_PASSWORD=admin
```

**問題点:**
- FERNET_KEY が git リポジトリに載ると、DB 内の接続情報（パスワード等）が復号できてしまう
- デフォルトの `airflow` / `admin` パスワードは攻撃者に真っ先に試される

**本番での対応:**
```yaml
# .env ファイルに切り出し、.gitignore に追加する
# docker-compose.yml 側
environment:
  - AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

```bash
# Fernet Key の生成方法
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

さらに本番では AWS Secrets Manager / GCP Secret Manager / HashiCorp Vault 等からシークレットを注入するのが標準的。

---

### 2. GCP サービスアカウントキーのファイルマウント (`docker-compose.yml`)

```yaml
# 現状
- GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/dbt-sa-key.json
- source: ./dbt-sa-key.json
  target: /opt/airflow/dbt-sa-key.json
```

**問題点:**
- JSON キーファイルはコンテナに直接マウントされており、コンテナが侵害されるとキーが漏洩する
- ローカルのキーファイル自体が誤って git にコミットされるリスクがある（`.gitignore` 済みでも注意）

**本番での対応:**
- GKE 上では **Workload Identity** を使い、Pod にサービスアカウントを紐づける（JSON キー不要）
- Cloud Run / Cloud Composer では **インスタンスのサービスアカウント** をアタッチする
- どうしても JSON キーが必要な場合は GCP Secret Manager に保存し、起動時に取得する

---

### 3. root ユーザーでの実行 (`docker-compose.yml`)

```yaml
# 現状
user: "0:0"   # root:root
```

**問題点:**
- コンテナが侵害された際に、root 権限でホスト OS に影響が及ぶリスクがある

**本番での対応:**
```yaml
# Airflow 公式推奨は UID 50000
user: "50000:0"
```

root が必要な初期化処理は `airflow-init` サービスのみに限定し、それ以外は非 root で動かす。

---

## 🟠 High（できるだけ早期に対処）

### 4. Executor が LocalExecutor (`docker-compose.yml`)

```yaml
# 現状
- AIRFLOW__CORE__EXECUTOR=LocalExecutor
```

**問題点:**
- LocalExecutor はタスクをスケジューラと同一プロセスで実行するため、スケールアウトができない
- タスクが増えるとスケジューラのリソースを食い潰す

**本番での対応:**
| 規模 | 推奨 Executor |
|------|--------------|
| 小規模（数十 DAG） | CeleryExecutor + Redis |
| 中〜大規模 | KubernetesExecutor |
| GCP 利用 | Cloud Composer（マネージド Airflow） |

---

### 5. Postgres データの非永続化 (`docker-compose.yml`)

```yaml
# 現状: postgres サービスに volumes 指定なし
postgres:
  image: postgres:13
  environment: ...
  # ← volumes がない
```

**問題点:**
- `docker-compose down` または再起動でメタデータ（DAG 実行履歴、接続情報、変数）がすべて消える

**本番での対応:**
```yaml
postgres:
  image: postgres:13
  volumes:
    - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

本番では RDS / Cloud SQL 等のマネージド DB を使い、自動バックアップを有効にする。

---

### 6. restart ポリシーの未設定 (`docker-compose.yml`)

```yaml
# 現状: restart 指定なし
```

**本番での対応:**
```yaml
x-airflow-common: &airflow-common
  restart: unless-stopped   # または always
```

---

### 7. dbt の target が `dev` (`dbt_after_cosmos.py`)

```python
# 現状
target_name="dev",
```

**問題点:**
- `dev` プロファイルを本番環境で使うと、開発用データセットへ書き込んでしまう

**本番での対応:**
```python
# 環境変数で切り替える
import os
target_name=os.getenv("DBT_TARGET", "prod"),
```

profiles.yml 側で `dev` / `prod` ターゲットを明確に分離し、接続先データセットを変える。

---

### 8. アラートの未設定 (`run_dbt_dag.py`)

```python
# 現状
'email_on_failure': False,
'email_on_retry': False,
```

**本番での対応:**
```python
default_args = {
    'email_on_failure': True,
    'email': ['data-alert@your-company.com'],
    # または Slack / PagerDuty への通知
    'on_failure_callback': slack_alert_callback,
}
```

---

## 🟡 Medium（改善推奨）

### 9. Dockerfile のレイヤー構成

```dockerfile
# 現状: pip install が複数 RUN に分かれている
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir "google-cloud-aiplatform>=1.127.0" ...
RUN pip install --no-cache-dir "astronomer-cosmos[dbt-bigquery]"
```

**改善案:**
- `requirements.txt` に切り出してバージョン管理する
- バージョン範囲指定（`>=`）は本番では固定（`==`）にして再現性を担保する

```
# requirements.txt
google-cloud-aiplatform==1.127.0
google-cloud-bigquery==3.26.0
gcloud-aio-bigquery==6.2.1
astronomer-cosmos[dbt-bigquery]==1.9.0
```

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

---

### 10. Postgres のバージョンが古い (`docker-compose.yml`)

```yaml
# 現状
image: postgres:13
```

PostgreSQL 13 は 2025 年 11 月にサポート終了。本番では `postgres:16` 以上を使う。

---

### 11. リソース制限の未設定 (`docker-compose.yml`)

**本番での対応:**
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '0.5'
      memory: 1G
```

---

### 12. ログの外部転送未設定

**本番での対応:**
```yaml
# GCS にログを転送する
- AIRFLOW__LOGGING__REMOTE_LOGGING=True
- AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=gs://your-bucket/airflow-logs
- AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=my_gcp_connection
```

---

### 13. `airflow-init` の環境変数が共通アンカーを上書きしている (`docker-compose.yml`)

```yaml
# 現状: airflow-init の environment が FERNET_KEY 等を引き継がない
airflow-init:
  environment:
    - AIRFLOW__CORE__EXECUTOR=LocalExecutor
    - AIRFLOW__CORE__SQL_ALCHEMY_CONN=...
    # ← FERNET_KEY がない
```

`<<: *airflow-common` を継承しつつ `environment` に追記する形にすると漏れがなくなる:
```yaml
airflow-init:
  <<: *airflow-common
  command: db migrate
  environment:
    <<: *airflow-common-env   # 別アンカーで env だけ切り出す方法が一般的
    _AIRFLOW_DB_UPGRADE: "true"
    _AIRFLOW_WWW_USER_CREATE: "true"
```

---

## 🔵 Low（クリーンアップ・整理）

### 14. `test_dag.py` / `dbt_before_cosmos.py` の残留

- `test_dag.py`: 空の DAG。本番環境ではスキャン対象になりノイズになる
- `dbt_before_cosmos.py`: Cosmos 移行前の実装。参考として残すなら `_archive/` 等に移す

### 15. `__pycache__` が git 管理されている可能性

`.gitignore` に以下を追加する:
```
dags/__pycache__/
*.pyc
```

### 16. `dbt_after_cosmos.py` の `default_args` 未設定

`DbtDag` でも `default_args` は指定できる。retries や owner を明示すると運用時に管理しやすい:
```python
cosmos_dag = DbtDag(
    dag_id="dbt_after_cosmos",
    default_args={
        'owner': 'data-team',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    ...
)
```

### 17. タイムゾーン設定の不統一

- `dbt_after_cosmos.py`: `pendulum.timezone("Asia/Tokyo")` で JST 指定 ✅
- `run_dbt_dag.py`: `datetime(2026, 5, 1)` で timezone-naive（UTC 扱い）⚠️
- `dbt_before_cosmos.py`: 同様に timezone-naive ⚠️

DAG 全体でタイムゾーンを揃えること:
```python
import pendulum
start_date=datetime(2026, 5, 1, tzinfo=pendulum.timezone("Asia/Tokyo"))
```

または `airflow.cfg` の `default_timezone = Asia/Tokyo` で統一する。

---

## まとめ（優先度サマリー）

| 優先度 | 項目 | 対応コスト |
|--------|------|-----------|
| 🔴 Critical | シークレットのハードコード | 低（.env 化） |
| 🔴 Critical | SA キーのファイルマウント | 高（Workload Identity 移行） |
| 🔴 Critical | root 実行 | 低（user 変更） |
| 🟠 High | LocalExecutor | 高（Celery/K8s 移行） |
| 🟠 High | DB 非永続化 | 低（volume 追加） |
| 🟠 High | restart ポリシー | 低 |
| 🟠 High | dbt target が dev | 低（env var 化） |
| 🟠 High | アラート未設定 | 中 |
| 🟡 Medium | requirements.txt 化 | 低 |
| 🟡 Medium | Postgres バージョン | 低 |
| 🟡 Medium | リソース制限 | 低 |
| 🟡 Medium | ログ外部転送 | 中 |
| 🔵 Low | テスト DAG 削除 | 低 |
| 🔵 Low | タイムゾーン統一 | 低 |