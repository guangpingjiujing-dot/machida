# Spark / DuckDB ハンズオン

PySpark で DataFrame を作成・集計し、Parquet 形式で保存するハンズオンです。Spark が出力した Parquet を DuckDB で読むところまで進めます。

## 前提条件

WSL / Ubuntu の起動方法、Java・Python・PySpark のインストールは、先に [WSL_UBUNTU_SETUP.md](WSL_UBUNTU_SETUP.md) を完了してください。

この README では、プロジェクトのフォルダに移動し、WSL 側の Python 仮想環境を有効化済みであることを前提にします。

```bash
# このハンズオンのフォルダへ移動する
cd /mnt/c/test_github/machida/spark_duckdb_handson

# WSL 側に作成した Python 仮想環境を有効化する
source ~/venvs/spark-duckdb-handson/bin/activate
```

> Python 仮想環境はプロジェクト内ではなく、WSL 側の `~/venvs/spark-duckdb-handson` を使用します。Windows 用の仮想環境は使用しません。

### 現在の構成

このハンズオンでは、ファイルを Windows 側に置いたまま、Spark の実行環境だけを WSL / Ubuntu 側に置きます。

| 対象 | 場所・使い方 |
| --- | --- |
| プロジェクトの実体 | Windows: `C:\test_github\machida\spark_duckdb_handson` |
| Ubuntu から見たプロジェクト | `/mnt/c/test_github/machida/spark_duckdb_handson` |
| Python 仮想環境 | WSL: `~/venvs/spark-duckdb-handson` |
| Spark の Parquet 出力 | WSL: `~/workspace/spark_duckdb_output/` |
| VS Code | `spark_duckdb_handson [WSL: Ubuntu]` のウィンドウで開く |

この構成では、Ubuntu で Spark を実行し、Windows 側にあるコードと入力データを読みます。Parquet の出力だけは、Spark が Linux の権限設定を行えるよう Ubuntu 側に保存します。プロジェクトを Ubuntu のホームディレクトリへコピーする必要はありません。

### 入出力の配置

```text
入力
/mnt/c/test_github/machida/spark_duckdb_handson/input/

出力
/home/sparkuser/workspace/spark_duckdb_output/
```

### この環境で確認済みのバージョン

- Java: OpenJDK 21
- PySpark: 4.2.0
- DuckDB: 1.5.6

次のコマンドで、現在の環境のバージョンを確認できます。

```bash
# Java・PySpark・DuckDB のバージョンを確認する
java -version
python -c "import pyspark, duckdb; print('PySpark:', pyspark.__version__); print('DuckDB:', duckdb.__version__)"
```

## 現在の進捗

Spark の起動確認、PySpark / DuckDB のインストール、サンプル Parquet の保存・読込、野球データ50 CSVのSpark集計まで完了しています。ZIP の展開は環境構築ではなく、ハンズオン用データの準備です。

## ハンズオンの流れ

| 手順 | ファイル | 学ぶこと |
| --- | --- | --- |
| 1 | `01_hello_spark.py` | Spark を起動し、DataFrame を表示する |
| 2 | `02_spark_to_parquet.py` | 集計結果を Parquet 形式で保存する |
| 3 | `03_duckdb_read_parquet.py` | Spark が作った Parquet を DuckDB の SQL で読む |
| 4 | `04_read_baseball_csv.py` | 50 個の野球 CSV を Spark で一括読込・集計して Parquet 保存する |
| 5 | `05_duckdb_query_baseball_summary.py` | 野球の Parquet を DuckDB の永続テーブルに取り込み、SQL で確認する |

> `02_spark_to_parquet.py` は Spark の入出力を学ぶためのコードです。DuckDB は、Spark が出力した Parquet を確認する手順で使用します。

## 1. Spark を起動して DataFrame を表示する

`01_hello_spark.py` を実行します。このスクリプトでは、`SparkSession.builder.getOrCreate()` が Spark を起動します。

```bash
# Spark を起動して最初のサンプルを実行する
python 01_hello_spark.py
```

実行結果の例です。今回の WSL 環境では Spark 4.2.0 を確認しています。

```text
Spark version: 4.2.0
+-----+-----+---+
| name| city|age|
+-----+-----+---+
|Alice|Tokyo| 30|
|  Bob|Osaka| 25|
|Carol|Tokyo| 35|
+-----+-----+---+
```

### コードの見どころ

```python
# Spark を操作するための入口を読み込む
from pyspark.sql import SparkSession

# ローカル PC 上で Spark を起動する
spark = (
    SparkSession.builder
    .appName("SparkDuckDBHandson")
    .master("local[2]")  # 最大2個の Spark タスクを同時に実行する
    .getOrCreate()
)

# Python のリストを、列を持つ Spark DataFrame に変換する
df = spark.createDataFrame(people, ["name", "city", "age"])

# DataFrame の内容を表形式で表示する
df.show()
```

## 2. 都市ごとに集計して Parquet を保存する

次のスクリプトでは、都市ごとの人数と平均年齢を集計し、Parquet 形式で保存します。

```bash
# 都市ごとの人数・平均年齢を集計して Parquet を出力する
python 02_spark_to_parquet.py

# Ubuntu 側に出力されたファイルを確認する
find ~/workspace/spark_duckdb_output/people_by_city -maxdepth 1 -type f -printf '%f\n'
```

`~/workspace/spark_duckdb_output/people_by_city/` は **1 個の Parquet ファイルではなくフォルダ** です。Spark は並列に書き込むため、`part-...parquet` や `_SUCCESS` など複数のファイルを作成します。

> コードと入力 CSV は Windows 側の `/mnt/c/...` に置いたままです。Spark の出力だけを Ubuntu 側へ保存するのは、Windows 側のファイルシステムでは Spark の `chmod` による権限設定が失敗する場合があるためです。

### コードの見どころ

```python
# city 列が同じデータをグループ化して集計する
summary_df = (
    df.groupBy("city")
    .agg(
        F.count("*").alias("people_count"),  # 都市ごとの人数を数える
        F.round(F.avg("age"), 1).alias("average_age"),  # 平均年齢を計算する
    )
    .orderBy("city")  # 都市名の昇順に並べ替える
)

# Ubuntu 側に、Spark の分散出力として Parquet のフォルダを作成する
summary_df.write.mode("overwrite").parquet(str(output_path))
```

## 3. Spark を停止する

### このハンズオンのスクリプトを実行した場合

`01_hello_spark.py` と `02_spark_to_parquet.py` の末尾には、次のコードがあります。

```python
# Spark を終了し、使用したメモリやプロセスを解放する
spark.stop()
```

したがって、**スクリプトが正常終了すれば Spark も自動的に停止します**。通常は追加操作不要です。

実行中に止めたい場合は、ターミナルで `Ctrl + C` を押します。停止しきれないプロセスが残ったように見えるときだけ、次で確認します。

```bash
# Spark に関連する Java プロセスを確認する
jps -l

# 表示されたプロセス ID を指定して終了する（例: 12345 を実際の番号に置き換える）
kill 12345
```

> `kill -9` は強制終了なので、まずは `kill プロセスID` を使ってください。通常のスクリプト実行ではこの操作は不要です。

### 対話形式で Spark を起動した場合

`pyspark` を起動した場合は、終了前に `spark.stop()` を実行します。

```bash
# PySpark の対話シェルを起動する
pyspark
```

起動後、`>>>` の表示で次を入力します。

```python
# 起動中の SparkSession を明示的に停止する
spark.stop()

# Python シェルを終了する
exit()
```

## 4. DuckDB で Parquet を読む

`02_spark_to_parquet.py` が Ubuntu 側へ出力した Parquet を DuckDB で読みます。Python の仮想環境を有効にしてから実行してください。

```bash
# DuckDB から Spark が出力した Parquet を SQL で確認する
python 03_duckdb_read_parquet.py
```

このスクリプトは、`read_parquet()` という DuckDB の SQL 関数で `part-...parquet` を直接読み込みます。今回は確認用にメモリ上で DuckDB を起動するため、`.duckdb` ファイルは作りません。DuckDB は Parquet を直接読めるため、データベースへ取り込む前の確認にも便利です。

## 5. 50 個の野球 CSV を Spark で読む

野球データは `input/baseball_data.zip` から読み込みます。

### 野球データの準備

`baseball_data.zip`（約 295MB）は GitHub のファイルサイズ上限（100MB）を超えるため、リポジトリには含めていません。各自で用意して `input/` に配置してください。

- 元データ: BigQuery の公開データセット `bigquery-public-data.baseball.games_wide`
- BigQuery からテーブルを CSV で GCS へエクスポートすると、`games_wide-000000000000.csv` のように分割された CSV が出力されます
- 出力された 50 個の CSV を ZIP にまとめ、`input/baseball_data.zip` として配置します

```text
spark_duckdb_handson/
└── input/
    └── baseball_data.zip   # Git 管理対象外
```

### Spark で読み込む

最初の一回だけ `--extract` を付けて実行すると、ZIP を `input/baseball/` へ展開してから、50 個の CSV を Spark が一括で読み込みます。

```bash
# 初回のみ: ZIP を展開してから Spark の集計を実行する
python 04_read_baseball_csv.py --extract
```

このスクリプトでは、CSV のイベント行数と `gameId` の重複を除いた試合数を、年・シーズン種別ごとに集計します。集計結果は次の Ubuntu 側フォルダに Parquet として保存されます。

```text
/home/sparkuser/workspace/spark_duckdb_output/baseball/event_and_game_counts_by_year/
```

2回目以降は ZIP 展開をせず、次のコマンドだけで再集計できます。

```bash
# 展開済みの CSV を使って再集計する
python 04_read_baseball_csv.py
```

> ZIP 展開により、Windows 側の `input/baseball/` に約 1.7 GB の CSV が追加されます。CSV の1行は試合全体ではなくイベント単位の行を含むため、試合数を数えるときは `gameId` の重複を除く必要があります。

### 分散処理はどのように動いたか

今回の実行では、Spark は 50 個の CSV を **17 個のパーティション**（読み込みの仕事）として扱いました。この 17 はコードで指定した数ではなく、Spark の Driver がファイル数・ファイルサイズ・読込設定などから自動で作った読込計画の結果です。同じコードでも、入力データや設定が変われば別の数になることがあります。

`local[2]` と17パーティションは役割が異なります。

```text
17 パーティション = 用意された「読み込みの仕事」の総数
local[2]           = 同時に実行できる仕事の最大数
```

したがって、17個の仕事を一度に実行するのではなく、最大2個ずつ順番に実行します。例えば、仕事1と2を同時に始め、先に空いた実行枠へ仕事3、次に仕事4を渡していくイメージです。ターミナルの `(14 + 2) / 17` は、17個中14個完了・2個実行中・1個待機中を表します。

```text
50 CSV
  ↓ Spark Driver が読込計画を作る
17 パーティション（読込タスク）
  ↓ local[2] により最大2個ずつ実行
各パーティションでイベントを数える
  ↓ groupBy() による Shuffle
同じ year / seasonType ごとに途中結果を集める
  ↓
年別集計を Parquet として保存する
```

`groupBy("year", "seasonType")` は、各パーティションで数えた途中結果を同じキーごとに集め直す処理です。この集め直しを **Shuffle（シャッフル）** と呼びます。`collect()` は実処理の開始を指示する操作で、Python 側へ戻すのは元の 761,618 行ではなく、小さな年別集計結果だけです。

## 6. DuckDB のテーブルとして SQL で確認する

次のスクリプトは、Spark が保存した Parquet を DuckDB の `baseball_year_summary` テーブルへ取り込み、SQL を実行します。

```bash
# Spark の年別集計 Parquet を DuckDB のテーブルへ取り込み、SQL で表示する
python 05_duckdb_query_baseball_summary.py
```

実行すると、Ubuntu 側に次のデータベースファイルが作られます。

```text
/home/sparkuser/workspace/spark_duckdb_output/baseball/baseball.duckdb
```

テーブル名は `baseball_year_summary` です。スクリプト内では、次の SQL を実行しています。

```sql
SELECT
    year,
    seasonType,
    event_row_count,
    game_count
FROM baseball_year_summary
ORDER BY year, seasonType;
```

`CREATE OR REPLACE TABLE` を使っているため、Spark で再集計した後にもう一度スクリプトを実行すると、同じテーブルを最新の Parquet の内容で更新できます。
