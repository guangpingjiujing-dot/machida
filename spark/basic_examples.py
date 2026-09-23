"""
PySpark の基本的な使い方のサンプルコード

このファイルでは、SparkSession の作成方法や基本的な操作を学びます。
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

def create_spark_session():
    """
    SparkSession を作成する関数
    
    SparkSession は Spark アプリケーションのエントリーポイントです。
    """
    # local[*] は利用可能なすべてのCPUコアを使用
    spark = SparkSession.builder \
        .appName("BasicExamples") \
        .master("local[*]") \
        .getOrCreate()
    
    return spark

def example_1_create_dataframe_from_list():
    """
    例1: リストから DataFrame を作成する
    """
    spark = create_spark_session()
    
    # リストから DataFrame を作成
    data = [
        ("Alice", 25),
        ("Bob", 30),
        ("Charlie", 35)
    ]
    
    # スキーマを指定しない場合（推論される）
    df = spark.createDataFrame(data, ["name", "age"])
    print("=== 例1: リストから DataFrame を作成 ===")
    df.show()
    
    # スキーマを明示的に指定する場合
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True)
    ])
    df_with_schema = spark.createDataFrame(data, schema)
    print("\nスキーマを明示的に指定した場合:")
    df_with_schema.show()
    df_with_schema.printSchema()
    
    spark.stop()

def example_2_read_csv():
    """
    例2: CSV ファイルを読み込む
    
    employees.csv ファイルからデータを読み込みます。
    """
    spark = create_spark_session()
    
    # CSV ファイルを読み込む
    csv_path = "employees.csv"
    # df = spark.read.csv(csv_path, header=True, inferSchema=True)
    df = spark.read.csv(csv_path, header=True)
    
    print("=== 例2: CSV ファイルを読み込む ===")
    df.show()
    
    # データを一時的に CSV として保存して読み込む例
    df.write.mode("overwrite").csv("temp_data.csv", header=True)
    # df_read = spark.read.csv("temp_data.csv", header=True, inferSchema=True)
    df_read = spark.read.csv("temp_data.csv", header=True)
    print("\nCSV から読み込んだデータ:")
    df_read.show()
    df_read.printSchema()
    
    spark.stop()

def example_3_basic_operations():
    """
    例3: DataFrame の基本的な操作
    """
    spark = create_spark_session()
    
    data = [
        ("Alice", 25, "Engineering"),
        ("Bob", 30, "Marketing"),
        ("Charlie", 35, "Engineering"),
        ("Diana", 28, "Sales")
    ]
    # df = spark.createDataFrame(data, ["name", "age", "department"])
    df = spark.createDataFrame(data)
    
    print("=== 例3: 基本的な操作 ===")
    
    # スキーマを指定しなかった場合の列名を確認
    print("\n0. 列名を指定しなかった場合のデフォルト列名:")
    df.printSchema()
    df.show()
    
    # 後から列名を指定する方法: toDF() メソッドを使用
    df = df.toDF("name", "age", "department")
    print("\n列名を指定した後:")
    df.printSchema()
    
    # データを表示
    print("\n1. 全データを表示:")
    df.show()
    
    # 最初の数行を表示
    print("\n2. 最初の2行を表示:")
    df.show(2)
    
    # スキーマを表示
    print("\n3. スキーマを表示:")
    df.printSchema()
    
    # 列を選択
    print("\n4. 特定の列を選択:")
    df.select("name", "age").show()
    
    # フィルタリング
    print("\n5. フィルタリング（年齢が30以上）:")
    df.filter(df.age >= 30).show()
    
    # グループ化と集計
    print("\n6. 部署ごとの平均年齢:")
    df.groupBy("department").avg("age").show()
    
    # 並び替え
    print("\n7. 年齢で降順に並び替え:")
    df.orderBy(df.age.desc()).show()
    
    spark.stop()

def example_4_spark_context_vs_session():
    """
    例4: SparkContext と SparkSession の関係
    
    SparkSession は内部的に SparkContext を持っています。
    """
    spark = create_spark_session()
    
    print("=== 例4: SparkContext と SparkSession の関係 ===")
    
    # SparkSession から SparkContext を取得
    sc = spark.sparkContext
    
    print(f"SparkContext のアプリケーション名: {sc.appName}")
    print(f"SparkContext のマスター: {sc.master}")
    
    # SparkContext を使って RDD を作成
    rdd = sc.parallelize([1, 2, 3, 4, 5])
    print(f"\nRDD の内容: {rdd.collect()}")
    
    # SparkSession を使って DataFrame を作成
    df = spark.createDataFrame([(1,), (2,), (3,), (4,), (5,)], ["value"])
    print("\nDataFrame の内容:")
    df.show()
    
    spark.stop()

if __name__ == "__main__":
    print("PySpark の基本的な使い方のサンプルコード\n")
    
    example_1_create_dataframe_from_list()
    print("\n" + "="*50 + "\n")
    
    example_2_read_csv()
    print("\n" + "="*50 + "\n")
    
    example_3_basic_operations()
    print("\n" + "="*50 + "\n")
    
    example_4_spark_context_vs_session()
