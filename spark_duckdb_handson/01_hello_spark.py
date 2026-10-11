# Spark を操作するための入口（SparkSession）を読み込む
from pyspark.sql import SparkSession

# Spark を起動する
spark = (
    SparkSession.builder
    # Spark の実行名。Spark UI などで識別するときに使う
    .appName("SparkDuckDBHandson")
    # 自分のPC上で実行する設定。local[2] は2つの実行スレッドを使う意味
    .master("local[2]")
    .getOrCreate()
)

# サンプルとなる人のデータ
# 1行は「名前、居住都市、年齢」の順番
people = [
    ("Alice", "Tokyo", 30),
    ("Bob", "Osaka", 25),
    ("Carol", "Tokyo", 35),
]

# Python のリストを、Spark が扱える表形式のデータ（DataFrame）へ変換する
# 右側のリストは列名
df = spark.createDataFrame(people, ["name", "city", "age"])

# 現在動いている Spark のバージョンを表示する
print(f"Spark version: {spark.version}")

# DataFrame の内容を表形式で表示する
df.show()

# Spark を終了し、使用したメモリやプロセスを解放する
spark.stop()