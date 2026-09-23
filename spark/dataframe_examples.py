"""
DataFrame を使った処理のサンプルコード

DataFrame は Spark の高レベル API で、現在の Spark では推奨されている方法です。
自動最適化により、RDD よりも高速に処理できます。
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.functions import col, avg, sum, count, max, min, when, desc, asc

def create_spark_session():
    """SparkSession を作成"""
    spark = SparkSession.builder \
        .appName("DataFrameExamples") \
        .master("local[*]") \
        .getOrCreate()
    return spark

def example_1_create_dataframe():
    """
    例1: DataFrame の作成方法
    """
    spark = create_spark_session()
    
    print("=== 例1: DataFrame の作成方法 ===")
    
    # 方法1: リストから作成（スキーマを推論）
    data = [
        ("Alice", 25, "Engineering"),
        ("Bob", 30, "Marketing"),
        ("Charlie", 35, "Engineering")
    ]
    df1 = spark.createDataFrame(data, ["name", "age", "department"])
    print("リストから作成（スキーマ推論）:")
    df1.show()
    
    # 方法2: スキーマを明示的に指定
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True),
        StructField("department", StringType(), True)
    ])
    df2 = spark.createDataFrame(data, schema)
    print("\nスキーマを明示的に指定:")
    df2.printSchema()
    
    # 方法3: 辞書のリストから作成
    dict_data = [
        {"name": "Alice", "age": 25, "department": "Engineering"},
        {"name": "Bob", "age": 30, "department": "Marketing"},
        {"name": "Charlie", "age": 35, "department": "Engineering"}
    ]
    df3 = spark.createDataFrame(dict_data)
    print("\n辞書のリストから作成:")
    df3.show()
    
    spark.stop()

def example_2_select_and_filter():
    """
    例2: 列の選択とフィルタリング
    """
    spark = create_spark_session()
    
    data = [
        ("Alice", 25, "Engineering", 50000),
        ("Bob", 30, "Marketing", 45000),
        ("Charlie", 35, "Engineering", 60000),
        ("Diana", 28, "Sales", 40000),
        ("Eve", 32, "Engineering", 55000)
    ]
    df = spark.createDataFrame(data, ["name", "age", "department", "salary"])
    
    print("=== 例2: 列の選択とフィルタリング ===")
    print("元のデータ:")
    df.show()
    
    # 列の選択
    print("\n1. 特定の列を選択:")
    df.select("name", "age").show()
    
    # 複数の方法で列を選択
    print("\n2. 異なる方法で列を選択:")
    df.select(col("name"), df["age"]).show()
    
    # フィルタリング
    print("\n3. 年齢が30以上の人のみ:")
    df.filter(df.age >= 30).show()
    
    # 複数の条件でフィルタリング
    print("\n4. 年齢が30以上かつ給与が50000以上:")
    df.filter((df.age >= 30) & (df.salary >= 50000)).show()
    
    # where を使ったフィルタリング（filter と同じ）
    print("\n5. where を使ったフィルタリング:")
    df.where(df.department == "Engineering").show()
    
    spark.stop()

def example_3_aggregations():
    """
    例3: 集計操作
    """
    spark = create_spark_session()
    
    data = [
        ("Alice", "Engineering", 50000),
        ("Bob", "Marketing", 45000),
        ("Charlie", "Engineering", 60000),
        ("Diana", "Sales", 40000),
        ("Eve", "Engineering", 55000),
        ("Frank", "Marketing", 48000)
    ]
    df = spark.createDataFrame(data, ["name", "department", "salary"])
    
    print("=== 例3: 集計操作 ===")
    print("元のデータ:")
    df.show()
    
    # 全体の集計
    print("\n1. 全体の平均給与:")
    df.select(avg("salary").alias("average_salary")).show()
    
    print("\n2. 全体の統計情報:")
    df.select(
        count("*").alias("count"),
        avg("salary").alias("avg_salary"),
        max("salary").alias("max_salary"),
        min("salary").alias("min_salary"),
        sum("salary").alias("total_salary")
    ).show()
    
    # グループ化による集計
    print("\n3. 部署ごとの平均給与:")
    df.groupBy("department").avg("salary").show()
    
    print("\n4. 部署ごとの統計情報:")
    df.groupBy("department").agg(
        count("*").alias("count"),
        avg("salary").alias("avg_salary"),
        max("salary").alias("max_salary"),
        min("salary").alias("min_salary")
    ).show()
    
    spark.stop()

def example_4_joins():
    """
    例4: 結合操作（JOIN）
    """
    spark = create_spark_session()
    
    # 従業員データ
    employees_data = [
        (1, "Alice", "Engineering"),
        (2, "Bob", "Marketing"),
        (3, "Charlie", "Engineering"),
        (4, "Diana", "Sales")
    ]
    employees_df = spark.createDataFrame(employees_data, ["id", "name", "department"])
    
    # 部署データ
    departments_data = [
        ("Engineering", "Tokyo"),
        ("Marketing", "Osaka"),
        ("Sales", "Tokyo")
    ]
    departments_df = spark.createDataFrame(departments_data, ["department", "location"])
    
    print("=== 例4: 結合操作（JOIN） ===")
    print("従業員データ:")
    employees_df.show()
    print("\n部署データ:")
    departments_df.show()
    
    # 内部結合（INNER JOIN）
    print("\n1. 内部結合（INNER JOIN）:")
    inner_join = employees_df.join(departments_df, "department", "inner")
    inner_join.show()
    
    # 左外部結合（LEFT OUTER JOIN）
    print("\n2. 左外部結合（LEFT OUTER JOIN）:")
    left_join = employees_df.join(departments_df, "department", "left")
    left_join.show()
    
    # 右外部結合（RIGHT OUTER JOIN）
    print("\n3. 右外部結合（RIGHT OUTER JOIN）:")
    right_join = employees_df.join(departments_df, "department", "right")
    right_join.show()
    
    spark.stop()

def example_5_window_functions():
    """
    例5: ウィンドウ関数
    
    ウィンドウ関数を使うと、各行に対して相対的な計算ができます。
    """
    spark = create_spark_session()
    from pyspark.sql.window import Window
    
    data = [
        ("Alice", "Engineering", 50000),
        ("Bob", "Marketing", 45000),
        ("Charlie", "Engineering", 60000),
        ("Diana", "Sales", 40000),
        ("Eve", "Engineering", 55000)
    ]
    df = spark.createDataFrame(data, ["name", "department", "salary"])
    
    print("=== 例5: ウィンドウ関数 ===")
    print("元のデータ:")
    df.show()
    
    # 部署ごとに給与でソートしたウィンドウを定義
    window_spec = Window.partitionBy("department").orderBy(desc("salary"))
    
    # 部署内でのランクを計算
    from pyspark.sql.functions import rank, dense_rank, row_number
    
    df_with_rank = df.withColumn("rank", rank().over(window_spec)) \
                     .withColumn("dense_rank", dense_rank().over(window_spec)) \
                     .withColumn("row_number", row_number().over(window_spec))
    
    print("\n部署ごとのランク:")
    df_with_rank.show()
    
    # 部署ごとの平均給与を各行に追加
    window_avg = Window.partitionBy("department")
    df_with_avg = df.withColumn("dept_avg_salary", avg("salary").over(window_avg))
    
    print("\n部署ごとの平均給与を追加:")
    df_with_avg.show()
    
    spark.stop()

def example_6_udf():
    """
    例6: ユーザー定義関数（UDF）
    
    UDF を使うと、カスタムの関数を DataFrame の操作に使用できます。
    """
    spark = create_spark_session()
    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType
    
    data = [
        ("Alice", 25),
        ("Bob", 30),
        ("Charlie", 35)
    ]
    df = spark.createDataFrame(data, ["name", "age"])
    
    print("=== 例6: ユーザー定義関数（UDF） ===")
    print("元のデータ:")
    df.show()
    
    # UDF を定義
    def age_category(age):
        if age < 30:
            return "Young"
        elif age < 35:
            return "Middle"
        else:
            return "Senior"
    
    # UDF を登録
    age_category_udf = udf(age_category, StringType())
    
    # UDF を使用
    df_with_category = df.withColumn("age_category", age_category_udf(col("age")))
    print("\n年齢カテゴリを追加:")
    df_with_category.show()
    
    spark.stop()

def example_7_conditional_logic():
    """
    例7: 条件分岐
    """
    spark = create_spark_session()
    
    data = [
        ("Alice", 50000),
        ("Bob", 45000),
        ("Charlie", 60000),
        ("Diana", 40000)
    ]
    df = spark.createDataFrame(data, ["name", "salary"])
    
    print("=== 例7: 条件分岐 ===")
    print("元のデータ:")
    df.show()
    
    # when/otherwise を使った条件分岐
    df_with_bonus = df.withColumn(
        "bonus",
        when(df.salary >= 50000, df.salary * 0.1)
        .otherwise(df.salary * 0.05)
    )
    
    print("\nボーナスを計算:")
    df_with_bonus.show()
    
    # 複数の条件
    df_with_grade = df.withColumn(
        "grade",
        when(df.salary >= 55000, "A")
        .when(df.salary >= 45000, "B")
        .otherwise("C")
    )
    
    print("\nグレードを追加:")
    df_with_grade.show()
    
    spark.stop()

if __name__ == "__main__":
    print("DataFrame を使った処理のサンプルコード\n")
    
    # example_1_create_dataframe()
    print("\n" + "="*50 + "\n")
    
    example_2_select_and_filter()
    print("\n" + "="*50 + "\n")
    
    example_3_aggregations()
    print("\n" + "="*50 + "\n")
    
    example_4_joins()
    print("\n" + "="*50 + "\n")
    
    example_5_window_functions()
    print("\n" + "="*50 + "\n")
    
    example_6_udf()
    print("\n" + "="*50 + "\n")
    
    example_7_conditional_logic()
