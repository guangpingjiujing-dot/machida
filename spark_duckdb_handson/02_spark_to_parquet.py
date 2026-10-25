# Spark を起動するための機能を読み込む
from pyspark.sql import SparkSession

# 実行終了後も Spark History Server で結果を確認できるようにする
from spark_history import configure_event_logging

# Ubuntu 側のホームディレクトリを安全に取得するために使う
from pathlib import Path

# 件数・平均値などの集計関数を F という短い名前で読み込む
from pyspark.sql import functions as F

# Spark を起動する
spark = (
    configure_event_logging(SparkSession.builder)
    # Spark の実行名
    .appName("SparkToParquet")
    # 自分のPC上で2つの実行スレッドを使う設定
    .master("local[2]")
    .getOrCreate()
)

# 実行時の細かなログを減らし、結果を見やすくする
spark.sparkContext.setLogLevel("ERROR")

# 集計対象となる人のサンプルデータ
# 1行は「名前、居住都市、年齢」の順番
people = [
    ("Alice", "Tokyo", 30),
    ("Bob", "Osaka", 25),
    ("Carol", "Tokyo", 35),
    ("David", "Osaka", 28),
    ("Erin", "Tokyo", 27),
    ("Frank", "Fukuoka", 40),
]

# Python のリストを Spark の表形式データ（DataFrame）へ変換する
df = spark.createDataFrame(people, ["name", "city", "age"])

# 都市ごとに集計する
summary_df = (
    df.groupBy("city")  # city 列が同じデータをグループ化する
    .agg(
        # 各都市に何人いるかを数える
        F.count("*").alias("people_count"),
        # 各都市の平均年齢を計算し、小数第1位までに丸める
        F.round(F.avg("age"), 1).alias("average_age"),
    )
    # 都市名の昇順で並べ替える
    .orderBy("city")
)

# 集計結果をターミナルに表として表示する
summary_df.show()

# Parquet の出力先を Ubuntu 側のファイルシステムに設定する
# Windows 側の /mnt/c/... に Spark が出力すると、Linux の権限設定（chmod）が失敗する場合がある
# Path.home() は、この環境では /home/sparkuser を指す
output_path = (
    Path.home()
    / "workspace"
    / "spark_duckdb_output"
    / "people_by_city"
)

# 集計結果を Parquet 形式で保存する
# Spark は分散処理向けのため、通常は1つのファイルではなくフォルダとして出力する
# overwrite は、同じ出力先が既にある場合に上書きする設定
summary_df.write.mode("overwrite").parquet(str(output_path))

# 保存先を表示し、DuckDB で確認するときの場所を分かりやすくする
print(f"Parquet output: {output_path}")

# Spark を終了し、使用したメモリやプロセスを解放する
spark.stop()
