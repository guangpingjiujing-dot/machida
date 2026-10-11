# Spark / DuckDB ハンズオンの環境構築まとめ

## 目的

Windows 上の WSL / Ubuntu に Spark の実行環境を作り、野球データを Spark で分散処理してから DuckDB で扱うための準備を行いました。

## 採用した構成

プロジェクトのコードと入力データは Windows 側に置いたまま、Spark・Python・Java は Ubuntu 側で実行する構成です。

| 対象 | 場所・役割 |
| --- | --- |
| プロジェクトの実体 | `C:\test_github\machida\spark_duckdb_handson` |
| Ubuntu から見たプロジェクト | `/mnt/c/test_github/machida/spark_duckdb_handson` |
| Spark 用 Python 仮想環境 | `~/venvs/spark-duckdb-handson` |
| Spark の Parquet 出力 | `~/workspace/spark_duckdb_output/` |
| VS Code | `spark_duckdb_handson [WSL: Ubuntu]` のウィンドウ |

この構成では、Ubuntu で Spark を実行し、Windows 側に置かれたコードと入力データを読みます。Spark が Linux の権限設定を行う Parquet 出力は、Ubuntu 側に保存します。プロジェクトを Ubuntu のホームディレクトリへコピーする必要はありません。

### 入出力の配置

```text
入力
/mnt/c/test_github/machida/spark_duckdb_handson/input/

出力
/home/sparkuser/workspace/spark_duckdb_output/
```

## 準備したソフトウェア

- WSL 2 / Ubuntu
- OpenJDK 21
- Python 3.14
- PySpark 4.2.0
- DuckDB 1.5.6
- VS Code と Microsoft 提供の WSL 拡張機能

## Python 仮想環境

Spark 用の Python 仮想環境は、WSL 側に作成しました。

```bash
# WSL 側に作成した Spark 用仮想環境を有効化する
source ~/venvs/spark-duckdb-handson/bin/activate

# 現在使用する Python を確認する
which python
```

有効化できると、ターミナル行頭は次のように表示されます。

```text
(spark-duckdb-handson) sparkuser@DESKTOP-...:/mnt/c/test_github/machida/spark_duckdb_handson$
```

Windows 用の `.venv` と、Windows 側の `/mnt/c/...` 内で作成に失敗した `venv` は使用しないため削除しました。Python 環境を Windows と Ubuntu で混在させないことが重要です。

## Spark の動作確認

Ubuntu 側の仮想環境で `01_hello_spark.py` を実行しました。

```bash
# Spark を起動し、最初の DataFrame を表示する
python 01_hello_spark.py
```

Spark 4.2.0 が起動し、`Alice`、`Bob`、`Carol` の DataFrame が表示されました。これにより、Java・PySpark・SparkSession の連携まで確認できています。

DuckDB も同じ WSL 側の仮想環境へインストール済みです。必要に応じて、次のコマンドで確認できます。

```bash
# DuckDB が Python から読み込めることを確認する
python -c "import duckdb; print('DuckDB:', duckdb.__version__)"
```

## VS Code の使い方

VS Code では Microsoft 提供の WSL 拡張機能を使用します。Ubuntu ターミナルから次を実行して、WSL 接続の VS Code を開きます。

```bash
# ハンズオンのフォルダを WSL 接続の VS Code で開く
cd /mnt/c/test_github/machida/spark_duckdb_handson
code .
```

VS Code の左上と左下に `spark_duckdb_handson [WSL: Ubuntu]`、`WSL: Ubuntu` と表示されれば接続成功です。VS Code のターミナルが `bash` であり、`sparkuser@...` と表示されることを確認してから、仮想環境を有効化します。

`(.venv) PS C:\...` と表示されるターミナルは Windows の PowerShell です。このハンズオンの Spark 実行には使用しません。

## 現在の到達点と次の作業

Spark / DuckDB の環境構築、Spark の起動確認、Parquet の Ubuntu 側への保存は完了しています。

次に `03_duckdb_read_parquet.py` を実行し、Spark が保存した Parquet を DuckDB の SQL で直接読めることを確認します。

## 野球データのハンズオンでの制御

野球データでは、Windows 側に置いた 50 個の CSV を Ubuntu 上の Spark が読み込みます。Spark の実行環境だけが Ubuntu 側にあり、元の ZIP と展開した CSV は Windows 側のプロジェクト内に置いたままです。

```text
Windows 側の入力 ZIP / CSV
/mnt/c/test_github/machida/spark_duckdb_handson/input/
            ↓
Ubuntu 上で動く Spark（local[2]）が 50 CSV を一括して読む
            ↓
イベント行数と、gameId の重複を除いた試合数を年別に集計する
            ↓
Ubuntu 側に Parquet として保存する
/home/sparkuser/workspace/spark_duckdb_output/baseball/
            ↓
DuckDB が Parquet を SQL で読む
```

### 分散処理として体験すること

`local[2]` は、クラウド上の複数台のコンピューターではなく、この PC 内で最大 2 個のタスクを同時に実行する設定です。これは「同時に働ける作業員の数」であり、パーティション数ではありません。

今回の実行では、Spark の Driver が 50 個の CSV のファイル数・サイズ・読込設定などを見て、**17 個のパーティション**（読み込みの仕事）を自動で作りました。この17はコードで固定した値ではなく、入力や設定が変われば別の数になります。

```text
17 パーティション = 読み込みの仕事の総数
local[2]           = 同時に実行できる仕事の最大数
```

したがって、17個の仕事は最大2個ずつ順番に実行されます。各パーティションで数えた途中結果は、`groupBy("year", "seasonType")` で同じキーごとに集め直されます。この集め直しを Shuffle（シャッフル）と呼びます。この「分けて処理し、最後に集める」流れが Spark の分散処理の基本です。

ターミナルの `(14 + 2) / 17` は、17個中14個完了・2個実行中・1個待機中という進捗表示です。`collect()` が実際の読み込み・分散集計を開始し、Python 側へ戻すのは元データ全体ではなく小さな年別集計結果だけです。

### データを数えるときの注意

CSV の1行は1試合ではなく、投球・打席などのイベントを含む行です。そのため、観客数などの試合情報を単純に合計すると、同じ試合の情報を何度も数える可能性があります。

最初のプログラムでは、次の2種類を区別して表示します。

- `event_row_count`: CSV に含まれるイベント行の件数
- `game_count`: `gameId` の重複を除いた試合数

### 最初に実行するプログラム

`04_read_baseball_csv.py` を追加しました。最初の1回だけ `--extract` を付けて実行すると、`input/baseball_data.zip` を Windows 側の `input/baseball/` へ展開してから、Spark が50 CSVを読み込みます。

```bash
# 初回のみ: ZIP を展開し、50 CSV を Spark で集計して Parquet に保存する
python 04_read_baseball_csv.py --extract
```

展開済みの場合は、`--extract` を付けずに再実行できます。

```bash
# 2回目以降: 展開済み CSV を読み込んで再集計する
python 04_read_baseball_csv.py
```

> ZIP の展開で Windows 側の `input/baseball/` に約 1.7 GB の CSV が追加されます。Spark の出力先はこれまでどおり Ubuntu 側の `~/workspace/spark_duckdb_output/baseball/` です。

この後は、Spark が保存した野球データ用 Parquet を DuckDB から SQL で読み込み、さらにチーム・年度などの切り口で分析します。

### DuckDB の永続テーブルとして確認する

`05_duckdb_query_baseball_summary.py` を実行すると、Spark が保存した Parquet を DuckDB の永続テーブルへ取り込みます。

```bash
# Spark の Parquet を DuckDB テーブルに取り込み、SQL の結果を表示する
python 05_duckdb_query_baseball_summary.py
```

この操作により、Ubuntu 側に `~/workspace/spark_duckdb_output/baseball/baseball.duckdb` が作成されます。データベース内のテーブル名は `baseball_year_summary` です。Parquet を直接読むだけではなく、DuckDB のデータベースへ保存して SQL で確認する段階です。

> ZIP の展開と野球データの処理は、環境構築ではなく次のハンズオン用データ準備です。
