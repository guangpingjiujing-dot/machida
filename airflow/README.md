# Apache Airflow 入門

## Airflow とは

Airflow は**ワークフロー（処理の流れ）を定義・スケジュール実行・監視するためのプラットフォーム**。

「毎日深夜にデータを取得して、変換して、DBに保存する」のような定期バッチ処理を、コードで管理できる。

### 何が嬉しいのか

| 課題 | Airflow を使うと |
|---|---|
| cron の定義が増えて管理できない | UIで一覧・実行状況を可視化できる |
| タスクが失敗しても気づかない | 失敗通知・自動リトライが設定できる |
| 処理の依存関係がわかりにくい | DAG でグラフとして明示できる |
| 過去分の再実行が面倒 | UIから任意の日付で再実行できる |

---

## 主なコンポーネント

```
┌─────────────────────────────────────────────┐
│                  Airflow                    │
│                                             │
│  ┌──────────┐      ┌──────────────────┐    │
│  │Webserver │      │    Scheduler     │    │
│  │  (UI)    │      │ (スケジュール管理)│    │
│  └──────────┘      └────────┬─────────┘    │
│                             │ タスクを実行   │
│                    ┌────────▼─────────┐    │
│                    │ LocalExecutor    │    │
│                    │ (タスク実行エンジン)│    │
│                    └──────────────────┘    │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │    Metadata DB (PostgreSQL)          │  │
│  │  DAGの状態・実行履歴・ユーザー情報   │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

| コンポーネント | 役割 |
|---|---|
| **Webserver** | DAGの一覧・実行状況・ログをブラウザで確認するUI |
| **Scheduler** | DAGを定期的にスキャンし、実行タイミングになったタスクをキューに入れる |
| **Executor** | 実際にタスクを実行する。`LocalExecutor` は同じマシン上で並列実行する最もシンプルな方式 |
| **Metadata DB** | すべての実行状態を記録するデータベース。Airflow の心臓部 |

---

## DAG とは

**DAG（Directed Acyclic Graph：有向非巡回グラフ）** は、Airflow における「ワークフローの定義」のこと。

Pythonファイルで書き、「どのタスクをどの順番で実行するか」を定義する。

```
      ┌──────────┐
      │  greet   │   タスクA
      └────┬─────┘
           │
      ┌────▼─────┐
      │ farewell │   タスクB（Aが成功してから実行）
      └──────────┘
```

### TaskFlow API（推奨される書き方）

Airflow 2.0 以降は `@dag` / `@task` デコレータを使った **TaskFlow API** が推奨される。  
タスク間のデータの受け渡し（XCom）も自動で処理してくれる。

```python
from airflow.decorators import dag, task

@dag(schedule="@daily", start_date=datetime(2024, 1, 1), catchup=False)
def my_pipeline():

    @task
    def extract() -> dict:
        return {"value": 42}

    @task
    def transform(data: dict) -> int:
        return data["value"] * 2

    @task
    def load(result: int) -> None:
        print(f"結果: {result}")

    load(transform(extract()))  # 依存関係を関数呼び出しで表現

my_pipeline()
```

### schedule の書き方

| 指定 | 意味 |
|---|---|
| `"@daily"` | 毎日1回（深夜0時） |
| `"@hourly"` | 毎時1回 |
| `"@weekly"` | 毎週日曜日 |
| `"0 9 * * *"` | 毎日9時（cron形式も使える） |
| `None` | 自動実行しない（手動トリガーのみ） |

---

## このフォルダの構成

```
airflow/
├── docker-compose.yml       # 起動設定
├── dags/                    # DAGファイル（ホストと同期）
│   ├── _01_hello_world.py   # 基本構造・TaskFlow API
│   ├── _02_task_dependencies.py
│   ├── _03_branching.py
│   ├── _04_xcom.py
│   ├── _05_retry_and_timeout.py
│   ├── _06_variables.py
│   ├── _07_connections.py
│   ├── _08_sensors.py
│   ├── _09_taskgroups.py
│   └── _10_dynamic_tasks.py
└── README.md
```

### ボリューム設計（パフォーマンスの注意点）

macOS 上の Docker は**bind mount（ホストのフォルダをコンテナにマウント）のファイルI/Oが遅い**。  
特にログのように多数の小ファイルが生成されると顕著に遅くなる。

| データ | 方式 | 理由 |
|---|---|---|
| `dags/` | bind mount | ホスト側で編集したいPythonファイルのため |
| ログ | Docker名前付きボリューム | ファイル数が多くなるためbind mountを避ける |
| PostgreSQLデータ | Docker名前付きボリューム | DBファイルはコンテナ内で完結すれば十分 |

---

## 起動手順

### 1. 初回のみ：DBの初期化とadminユーザーの作成

```bash
docker compose run --rm airflow-init
```

DBのマイグレーションと管理者ユーザー（admin / admin）の作成が行われる。  
2回目以降はスキップしてよい（`|| true` を仕込んであるので何度実行しても安全）。

### 2. Airflow の起動

```bash
docker compose up -d webserver scheduler
```

### 3. ブラウザでアクセス

http://localhost:8080

- ユーザー名: `admin`
- パスワード: `admin`

### 4. サンプルDAGの接続設定（_07_connections.py 用）

`connections_demo` DAG を動かすには事前に接続情報を1件登録する。

```bash
docker compose exec webserver airflow connections add demo_db \
  --conn-type postgres \
  --conn-host postgres \
  --conn-login airflow \
  --conn-password airflow \
  --conn-schema airflow \
  --conn-port 5432
```

### 5. 停止

```bash
docker compose down
```

データを完全に消したい場合（DBリセット）:

```bash
docker compose down -v   # ボリュームも削除
```

---

## よく使うコマンド

```bash
# ログを確認
docker compose logs -f scheduler

# コンテナの中に入る
docker compose exec webserver bash

# DAGを手動でトリガー（コマンドラインから）
docker compose exec webserver airflow dags trigger hello_world

# DAGの一覧を表示
docker compose exec webserver airflow dags list

# タスクのテスト実行（DBに記録しない）
docker compose exec webserver airflow tasks test hello_world greet 2024-01-01
```

---

## サンプルDAGの確認

`dags/hello_world.py` は2つのタスクをデータを渡しながら順番に実行するシンプルなDAG。

1. `greet`: メッセージを生成して返す
2. `farewell`: `greet` の戻り値を受け取って表示する

UIのDAG一覧から `hello_world` を選んで再生ボタンを押すと手動実行できる。  
タスクをクリック → **Logs** タブで `print()` の出力を確認できる。

---

## dbt × Airflow の連携 ― Astronomer Cosmos

**astronomer-cosmos**（通称 Cosmos）は、**dbt プロジェクトを Airflow のネイティブ DAG / TaskGroup へ自動変換するライブラリ**（PyPI: `astronomer-cosmos`）。

`BashOperator` で `dbt run` を呼ぶだけだと dbt プロジェクト全体が 1 つのブラックボックスタスクになるが、Cosmos を使うと **dbt モデル 1 つ = Airflow タスク 1 つ** に変換される。`ref()` / `source()` の依存関係もそのままタスク依存関係になるため、失敗したモデルの特定・リトライ・ログ確認がモデル単位でできるようになる。

### 主なコンセプト

| | 説明 |
|---|---|
| `DbtDag` | dbt プロジェクト全体を 1 つの独立した DAG として生成する |
| `DbtTaskGroup` | 既存 DAG の中に dbt 処理を TaskGroup として埋め込む（Extract → dbt → Load のような構成に使う） |
| `ProjectConfig` | dbt プロジェクトのパスや manifest.json の場所を指定 |
| `ProfileConfig` | Airflow Connection を dbt profile に自動マッピングする（DWH ごとに `ProfileMapping` クラスが用意されている） |
| `ExecutionConfig` | dbt バイナリのパスと実行モード（LOCAL / VIRTUALENV / DOCKER / KUBERNETES）を指定 |

### 実行モード

実際のプロジェクトで最も多いのは **`LOCAL` + 別 venv のバイナリパスを指定する** パターン。大規模プロジェクトでは Cosmos 1.11+ で追加された **`WATCHER` モード**（最大 80% 高速化）が有効。

### manifest.json の活用

DAG ロード時に dbt プロジェクトを解析する方法はいくつかあるが、本番環境では **CI/CD で事前に `dbt compile` して生成した manifest.json** を読み込む `DBT_MANIFEST` モードが最速（~0.35 秒 vs ~6 秒）で推奨される。

> 公式ドキュメント: https://astronomer.github.io/astronomer-cosmos/  
> GitHub: https://github.com/astronomer/astronomer-cosmos
