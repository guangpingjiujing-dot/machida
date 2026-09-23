# Spark / PySpark / Spark SQL 学習資料

## 分散処理システムの歴史

大規模データを処理するための分散処理システムは、以下のような歴史をたどってきました。

### MapReduce (2004年)

- **Google** が発表した分散処理のプログラミングモデル
- 大規模データを複数のマシンに分散して処理する仕組み
- Map フェーズと Reduce フェーズの2段階で処理
- 論文として公開され、後の分散処理システムの基礎となった

#### MapReduce の仕組み

MapReduce は **Map フェーズ**と **Reduce フェーズ**の2段階で処理を行います。

**具体例: 単語数カウント**

以下のような文章から、各単語の出現回数を数える処理を考えてみましょう。

**入力データ**:
```
"hello world"
"hello spark"
"world spark"
```

**処理の流れ**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Map フェーズ                              │
│  (各マシンで独立して処理)                                     │
└─────────────────────────────────────────────────────────────┘

マシン1: "hello world"
  ↓ Map処理（各単語を (単語, 1) のペアに変換）
  ("hello", 1)
  ("world", 1)

マシン2: "hello spark"
  ↓ Map処理
  ("hello", 1)
  ("spark", 1)

マシン3: "world spark"
  ↓ Map処理
  ("world", 1)
  ("spark", 1)

┌─────────────────────────────────────────────────────────────┐
│               Shuffle フェーズ（自動）                        │
│  (同じキーを持つデータを同じマシンに集約)                       │
└─────────────────────────────────────────────────────────────┘

  ("hello", 1) ───┐
  ("hello", 1) ───┼──→ マシン1: [("hello", 1), ("hello", 1)]
                 │
  ("world", 1) ───┼──→ マシン2: [("world", 1), ("world", 1)]
  ("world", 1) ───┘
                 │
  ("spark", 1) ───┼──→ マシン3: [("spark", 1), ("spark", 1)]
  ("spark", 1) ───┘

┌─────────────────────────────────────────────────────────────┐
│                   Reduce フェーズ                            │
│  (各マシンで同じキーの値を集計)                                │
└─────────────────────────────────────────────────────────────┘

マシン1: [("hello", 1), ("hello", 1)]
  ↓ Reduce処理（同じキーの値を合計）
  ("hello", 2)

マシン2: [("world", 1), ("world", 1)]
  ↓ Reduce処理
  ("world", 2)

マシン3: [("spark", 1), ("spark", 1)]
  ↓ Reduce処理
  ("spark", 2)

┌─────────────────────────────────────────────────────────────┐
│                      最終結果                                │
└─────────────────────────────────────────────────────────────┘

("hello", 2)
("world", 2)
("spark", 2)
```

**各フェーズの役割**:

1. **Map フェーズ**
   - 入力データを分割して複数のマシンに分散
   - 各マシンで独立して処理を実行
   - キー・値ペア `(key, value)` を生成

2. **Shuffle フェーズ**（自動）
   - 同じキーを持つデータを同じマシンに集約
   - MapReduce フレームワークが自動的に実行

3. **Reduce フェーズ**
   - 同じキーを持つデータを集計
   - 最終的な結果を生成

**MapReduce の特徴**:
- データを複数のマシンに分散して並列処理できる
- 各フェーズが独立しているため、スケールアウトしやすい
- ただし、各フェーズの間でディスクへの読み書きが発生するため、処理速度が遅い

### Hadoop (2006年)

- **Apache** が開発したオープンソースの分散処理フレームワーク
- Google の MapReduce を実装した **Hadoop MapReduce** が中核
- **HDFS (Hadoop Distributed File System)** という分散ファイルシステムも提供
- 大規模データ処理の標準的なソリューションとして広く普及

**Hadoop の特徴:**
- ディスクベースの処理（データをディスクに書き込んでから処理）
- バッチ処理に適している
- 安定性が高いが、処理速度が比較的遅い

### Spark (2014年)

- **Apache** が開発した分散処理フレームワーク
- Hadoop の後継として開発され、より高速な処理を実現
- メモリ内での処理により、Hadoop MapReduce よりも最大100倍高速
- バッチ処理だけでなく、ストリーミング処理もサポート

## Spark と Hadoop の違い

| 項目 | Hadoop MapReduce | Spark |
|------|------------------|-------|
| **処理方式** | ディスクベース | メモリベース |
| **処理速度** | 遅い | 最大100倍高速 |
| **処理タイプ** | バッチ処理のみ | バッチ + ストリーミング |
| **API** | MapReduce API のみ | RDD、DataFrame、Dataset、Spark SQL |
| **学習曲線** | やや難しい | 比較的簡単 |
| **用途** | 大規模バッチ処理 | リアルタイム処理、機械学習、SQL クエリ |

### 主な違いの詳細

1. **処理方式**
   - **Hadoop**: 各処理ステップでデータをディスクに書き込むため、I/O がボトルネックになる
   - **Spark**: データをメモリに保持して処理するため、高速

2. **API の豊富さ**
   - **Hadoop**: MapReduce のプログラミングモデルに従う必要がある
   - **Spark**: SQL ライクな操作、DataFrame API、機械学習ライブラリなど、多様な API を提供

3. **用途**
   - **Hadoop**: 大規模なバッチ処理に適している
   - **Spark**: リアルタイム処理、インタラクティブなクエリ、機械学習など、幅広い用途に対応

**注意**: Spark は Hadoop の完全な代替ではなく、Hadoop の HDFS と組み合わせて使用することもできます。Spark は Hadoop の上で動作することも可能です。

## Spark とは

Apache Spark は、大規模データを高速に処理するための分散処理フレームワークです。

### 主な特徴

- **高速処理**: メモリ内での処理により、従来の MapReduce よりも最大100倍高速
- **分散処理**: 複数のマシンに処理を分散させて並列実行
- **多様なデータソース**: CSV、JSON、Parquet、データベースなど様々なデータソースに対応
- **複数の API**: RDD、DataFrame、Dataset など複数の抽象化レイヤーを提供

## Spark のアーキテクチャ

Spark は複数のマシン（ノード）で構成される**クラスター**上で動作します。各ノードには異なる役割があります。

### Spark クラスターの構成

```
┌────────────────────────────────────────────────────────┐
│                    Spark クラスター                    │
│                                                        │
│   ┌──────────────────────┐                             │
│   │      Driver Node     │  アプリ全体の制御を担当     │
│   └──────────┬───────────┘                             │
│              │ タスクの指示                            │
│              ↓                                         │
│   ┌──────────────────────────────────────────┐         │
│   │             Cluster Manager              │         │
│   │ (YARN / Mesos / Standalone / Kubernetes) │         │
│   └──────────┬───────────────────────────────┘         │
│              │ リソースの割り当て                      │
│              ↓                                         │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│   │ Worker Node │  │ Worker Node │  │ Worker Node │    │
│   │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │    │
│   │ │Executor │ │  │ │Executor │ │  │ │Executor │ │    │
│   │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │    │
│   └─────────────┘  └─────────────┘  └─────────────┘    │
│     ↑ Executor がタスクを実際に実行する                │
└────────────────────────────────────────────────────────┘
```

### 主要なコンポーネント

#### 1. Driver（ドライバー）

- **役割**: Spark アプリケーションの制御を担当するプログラム
- **場所**: 通常はクライアントマシン（開発者のPCなど）で実行
- **主な処理**:
  - アプリケーションのコードを実行
  - SparkContext や SparkSession を作成
  - タスクを Executor に割り当て
  - 結果を集約して返す

```python
# Driver で実行されるコードの例
from pyspark.sql import SparkSession

# Driver で SparkSession を作成
spark = SparkSession.builder.appName("MyApp").getOrCreate()

# Driver で処理を指示（実際の処理は Executor で実行される）
df = spark.read.csv("data.csv")
result = df.groupBy("department").avg("salary")
result.show()  # Driver で結果を表示
```

#### 2. Executor（エグゼキューター）

- **役割**: 実際のデータ処理を実行するプロセス
- **場所**: Worker ノード（ワーカーノード）上で実行
- **主な処理**:
  - Driver から割り当てられたタスクを実行
  - データの読み込み、変換、集計などの処理
  - メモリ上にデータをキャッシュ
  - 結果を Driver に返す

**Executor の特徴**:
- 1つの Worker ノードに複数の Executor を配置できる
- 各 Executor は独立した JVM プロセスで動作
- Executor 内には複数のタスクを並列実行できるスレッドがある

#### 3. Worker Node（ワーカーノード）

- **役割**: 実際の処理を実行するマシン
- **構成**: 1つ以上の Executor を実行
- **役割**: データの処理とストレージの提供

#### 4. Cluster Manager（クラスター マネージャー）

- **役割**: クラスター全体のリソース管理を担当
- **種類**:
  - **Standalone**: Spark に組み込まれているシンプルなマネージャー
  - **YARN**: Hadoop のリソースマネージャー
  - **Mesos**: Apache Mesos を使用
  - **Kubernetes**: コンテナオーケストレーション

**Cluster Manager の主な機能**:
- Worker ノードの管理
- Executor へのリソース（CPU、メモリ）の割り当て
- ノードの障害時の処理

### 処理の流れ

1. **アプリケーションの起動**
   - Driver プログラムが実行される
   - SparkContext または SparkSession が作成される

2. **クラスターへの接続**
   - Driver が Cluster Manager に接続
   - Cluster Manager が Worker ノード上に Executor を起動

3. **タスクの実行**
   - Driver が処理計画（DAG: Directed Acyclic Graph）を作成
   - 処理を複数のタスクに分割
   - Executor にタスクを割り当て

4. **結果の返却**
   - Executor が処理結果を Driver に返す
   - Driver が結果を集約して返す

### 実行モード

Spark は以下の3つのモードで実行できます：

#### 1. Local Mode（ローカルモード）

- **用途**: 開発やテスト
- **構成**: 1台のマシンで Driver と Executor の両方を実行
- **設定**: `master("local[*]")` または `master("local[4]")`

```python
spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \  # 利用可能なすべてのCPUコアを使用
    .getOrCreate()
```

#### 2. Standalone Mode（スタンドアロンモード）

- **用途**: 小規模なクラスター
- **構成**: Spark 独自のクラスター マネージャーを使用
- **設定**: `master("spark://master-host:7077")`

#### 3. Cluster Mode（クラスターモード）

- **用途**: 本番環境
- **構成**: YARN、Mesos、Kubernetes などのクラスター マネージャーを使用
- **設定**: クラスター マネージャーに応じた設定

### リソースの設定

Executor に割り当てるリソースを設定できます：

```python
spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.executor.memory", "4g") \      # Executor のメモリ
    .config("spark.executor.cores", "2") \         # Executor のCPUコア数
    .config("spark.executor.instances", "3") \     # Executor の数
    .getOrCreate()
```

**設定項目の説明**:
- `spark.executor.memory`: 各 Executor に割り当てるメモリ量
- `spark.executor.cores`: 各 Executor が使用できるCPUコア数
- `spark.executor.instances`: クラスター全体の Executor の数

### まとめ

- **Driver**: アプリケーションの制御を担当
- **Executor**: 実際のデータ処理を実行
- **Worker Node**: Executor を実行するマシン
- **Cluster Manager**: クラスター全体のリソース管理

これらのコンポーネントが連携することで、大規模データの分散処理が実現されます。

## Spark でのファイル書き込みと _SUCCESS ファイル

Spark で CSV などのファイルを書き込む際、単一のファイルではなく**ディレクトリ**として書き込まれます。このディレクトリ内には、データファイルとともに `_SUCCESS` ファイルや `.crc` ファイルが自動的に作成されます。

### なぜディレクトリとして書き込むのか？

Spark は分散処理システムのため、データを複数のパーティションに分割して並列に書き込みます。そのため、単一のファイルではなく、ディレクトリとして書き込まれます。

```python
# CSV ファイルを書き込む例
df.write.mode("overwrite").csv("output.csv", header=True)
```

このコードを実行すると、`output.csv` という**ディレクトリ**が作成され、その中に以下のようなファイルが生成されます：

```
output.csv/
├── _SUCCESS
├── _SUCCESS.crc
├── part-00000-xxxxx-c000.csv
├── part-00000-xxxxx-c000.csv.crc
├── part-00001-xxxxx-c000.csv
├── part-00001-xxxxx-c000.csv.crc
└── ...
```

### _SUCCESS ファイルとは？

`_SUCCESS` ファイルは、書き込み処理が**正常に完了したこと**を示すマーカーファイルです。

- **役割**: すべてのパーティションの書き込みが成功したことを示す
- **内容**: 空のファイル（存在するかどうかが重要）
- **用途**: 
  - 書き込み処理の成功を確認する
  - 他のシステムやスクリプトが処理の完了を検知する
  - エラーハンドリングに使用

**注意**: `_SUCCESS` ファイルが存在しない場合、書き込み処理が失敗したか、まだ完了していない可能性があります。

### .crc ファイルとは？

`.crc` の CRC は **Cyclic Redundancy Check（巡回冗長検査）** の略で、データの誤りを検出するための代表的なアルゴリズムです。

`.crc` ファイルは、対応するデータファイルの CRC によるチェックサム（データから計算した短い値）を格納するファイルです。Hadoop の `LocalFileSystem` がファイル書き込み時に自動生成します。

- **役割**: データファイルの整合性を確認する
- **用途**: 
  - ファイルが破損していないか確認
  - 転送中にエラーが発生していないか確認
  - データの信頼性を保証

各データファイル（`part-00000-xxxxx-c000.csv` など）には、対応する `.crc` ファイル（`.part-00000-xxxxx-c000.csv.crc`）が作成されます。

### パーティションファイル（part-00000-...csv）

`part-00000-xxxxx-c000.csv` のようなファイルは、実際のデータが格納されているパーティションファイルです。

- **命名規則**: `part-{パーティション番号}-{UUID}-c{パーティションタイプ}.csv`
- **内容**: CSV データの一部
- **数**: データのサイズやパーティション数に応じて複数作成される

### 読み込み時の注意点

Spark で CSV を読み込む際は、**ディレクトリを指定**します。Spark は自動的にディレクトリ内のすべてのパーティションファイルを読み込みます。

```python
# ディレクトリを指定して読み込む（正しい方法）
df = spark.read.csv("output.csv", header=True, inferSchema=True)

# 個別のパーティションファイルを指定する必要はない
# df = spark.read.csv("output.csv/part-00000-xxxxx-c000.csv", ...)  # 不要
```

### 単一の CSV ファイルが欲しい場合

単一の CSV ファイルが必要な場合は、以下の方法があります：

#### 方法1: coalesce(1) を使用する

```python
# パーティション数を1に減らしてから書き込む
df.coalesce(1).write.mode("overwrite").csv("output.csv", header=True)
```

これにより、`part-00000-xxxxx-c000.csv` という1つのパーティションファイルのみが作成されます。ただし、`_SUCCESS` ファイルと `.crc` ファイルは引き続き作成されます。

#### 方法2: Pandas を使用する（小規模データの場合）

```python
# Spark DataFrame を Pandas DataFrame に変換してから書き込む
pandas_df = df.toPandas()
pandas_df.to_csv("output.csv", index=False)
```

**注意**: この方法は、データが1台のマシンのメモリに収まる場合のみ使用できます。大規模データには適していません。

### まとめ

- Spark は CSV を**ディレクトリ**として書き込む
- `_SUCCESS` ファイルは書き込み処理の成功を示す
- `.crc` ファイルはデータファイルの整合性を確認するためのチェックサム
- 読み込み時はディレクトリを指定する（個別のパーティションファイルを指定する必要はない）
- 単一ファイルが必要な場合は `coalesce(1)` を使用する

## SparkContext と SparkSession の違い

### SparkContext

- Spark 1.x の時代から存在する**低レベル API**
- RDD（Resilient Distributed Dataset）を操作するために使用
- Spark アプリケーションのエントリーポイント
- 1つのアプリケーションにつき1つの SparkContext のみ作成可能

```python
from pyspark import SparkContext

sc = SparkContext("local", "MyApp")
rdd = sc.parallelize([1, 2, 3, 4, 5])
```

### SparkSession

- Spark 2.0 以降で導入された**高レベル API**
- SparkContext、SQLContext、HiveContext などを統合
- DataFrame と Dataset API を使用するために必要
- Spark SQL を使用する際のエントリーポイント

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .getOrCreate()

df = spark.read.csv("data.csv")
```

### 使い分け

- **SparkContext**: RDD を直接操作したい場合（レガシーコードや細かい制御が必要な場合）
- **SparkSession**: DataFrame/Dataset や Spark SQL を使用する場合（**推奨**）

現在の Spark では、SparkSession を使用することが推奨されています。SparkSession は内部的に SparkContext を持っているため、SparkContext が必要な場合は `spark.sparkContext` でアクセスできます。

## RDD と DataFrame の違い

### RDD (Resilient Distributed Dataset)

- **低レベル API**: より細かい制御が可能
- **型安全性**: コンパイル時には型チェックされない（Python では実行時エラー）
- **最適化**: 開発者が手動で最適化する必要がある
- **使い方**: 関数型プログラミングスタイル（map、filter、reduce など）

```python
# RDD の例
rdd = sc.parallelize([1, 2, 3, 4, 5])
result = rdd.map(lambda x: x * 2).filter(lambda x: x > 5).collect()
```

**特徴:**
- 柔軟性が高いが、最適化が難しい
- 細かい制御が必要な場合に使用

### DataFrame

- **高レベル API**: より抽象化された操作
- **スキーマ**: 構造化データ（列と行）を持つ
- **最適化**: Catalyst オプティマイザーによる自動最適化
- **使い方**: SQL ライクな操作や、Pandas に似た操作

```python
# DataFrame の例
df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
result = df.filter(df.id > 1).select("name").collect()
```

**特徴:**
- 自動最適化により高速
- SQL ライクな操作が可能
- **現在の Spark では DataFrame の使用が推奨**

### 比較表

| 項目 | RDD | DataFrame |
|------|-----|-----------|
| API レベル | 低レベル | 高レベル |
| 最適化 | 手動 | 自動（Catalyst） |
| スキーマ | なし | あり |
| SQL サポート | なし | あり |
| 型安全性 | 低い | 高い |
| 推奨度 | レガシー | **推奨** |

## 学習の進め方

1. **基礎編**: `basic_examples.py` - Spark の基本的な使い方
2. **RDD 編**: `rdd_examples.py` - RDD を使った処理
3. **Lambda 式ガイド**: `lambda_expressions_guide.md` - RDD でよく使う Lambda 式の説明
4. **DataFrame 編**: `dataframe_examples.py` - DataFrame を使った処理（推奨）
5. **Spark SQL 編**: `spark_sql_examples.py` - Spark SQL を使った処理

各ファイルには実行可能なサンプルコードとコメントが含まれています。

## 実行方法

```bash
# PySpark がインストールされていることを確認
pip install pyspark

# サンプルコードを実行
python basic_examples.py
python rdd_examples.py
python dataframe_examples.py
python spark_sql_examples.py
```

## 参考資料

- [Apache Spark 公式ドキュメント](https://spark.apache.org/docs/latest/)
- [PySpark API リファレンス](https://spark.apache.org/docs/latest/api/python/)
