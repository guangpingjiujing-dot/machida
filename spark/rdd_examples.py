"""
RDD (Resilient Distributed Dataset) を使った処理のサンプルコード

RDD は Spark の低レベル API です。
現在は DataFrame の使用が推奨されていますが、RDD の理解も重要です。
"""

from pyspark.sql import SparkSession

def create_spark_session():
    """SparkSession を作成"""
    spark = SparkSession.builder \
        .appName("RDDExamples") \
        .master("local[*]") \
        .getOrCreate()
    return spark

def example_1_create_rdd():
    """
    例1: RDD の作成方法
    """
    spark = create_spark_session()
    sc = spark.sparkContext
    
    print("=== 例1: RDD の作成方法 ===")
    
    # 方法1: リストから作成
    rdd1 = sc.parallelize([1, 2, 3, 4, 5])
    print(f"リストから作成: {rdd1.collect()}")
    
    # 方法2: テキストファイルから作成
    # 実際のファイルを読み込む場合:
    # rdd2 = sc.textFile("path/to/file.txt")
    
    # サンプルデータを作成
    with open("temp_text.txt", "w") as f:
        f.write("Hello Spark\n")
        f.write("Hello Python\n")
        f.write("Hello World\n")
    
    rdd2 = sc.textFile("temp_text.txt")
    print(f"\nテキストファイルから作成:")
    rdd2.foreach(print)
    
    spark.stop()

def example_2_transformations():
    """
    例2: RDD の変換操作（Transformations）
    
    変換操作は遅延評価されます（実際に実行されるのはアクションが呼ばれたとき）。
    """
    spark = create_spark_session()
    sc = spark.sparkContext
    
    print("=== 例2: RDD の変換操作 ===")
    
    rdd = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    # map: 各要素に関数を適用
    mapped = rdd.map(lambda x: x * 2)
    print(f"map (各要素を2倍): {mapped.collect()}")
    
    # filter: 条件に合う要素だけを残す
    filtered = rdd.filter(lambda x: x % 2 == 0)
    print(f"filter (偶数だけ): {filtered.collect()}")
    
    # flatMap: 各要素を複数の要素に展開
    flat_mapped = rdd.flatMap(lambda x: [x, x * 10])
    print(f"flatMap (各要素と10倍の要素): {flat_mapped.collect()}")
    
    # distinct: 重複を除去
    rdd_with_duplicates = sc.parallelize([1, 2, 2, 3, 3, 3])
    distinct = rdd_with_duplicates.distinct()
    print(f"distinct (重複除去): {distinct.collect()}")
    
    # union: 2つの RDD を結合
    rdd1 = sc.parallelize([1, 2, 3])
    rdd2 = sc.parallelize([4, 5, 6])
    union = rdd1.union(rdd2)
    print(f"union (結合): {union.collect()}")
    
    spark.stop()

def example_3_actions():
    """
    例3: RDD のアクション操作（Actions）
    
    アクション操作は実際に処理を実行し、結果を返します。
    """
    spark = create_spark_session()
    sc = spark.sparkContext
    
    print("=== 例3: RDD のアクション操作 ===")
    
    rdd = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    # collect: すべての要素をリストとして取得
    print(f"collect: {rdd.collect()}")
    
    # count: 要素の数を数える
    print(f"count: {rdd.count()}")
    
    # first: 最初の要素を取得
    print(f"first: {rdd.first()}")
    
    # take: 最初の n 個の要素を取得
    print(f"take(3): {rdd.take(3)}")
    
    # reduce: 要素を結合して1つの値にする
    sum_result = rdd.reduce(lambda x, y: x + y)
    print(f"reduce (合計): {sum_result}")
    
    # foreach: 各要素に対して関数を実行（副作用のため）
    print("foreach (各要素を表示):")
    rdd.foreach(lambda x: print(f"  {x}"))
    
    spark.stop()

def example_4_key_value_operations():
    """
    例4: キー・値ペアの RDD 操作
    
    キー・値ペアの RDD は、グループ化や集計などの操作に便利です。
    """
    spark = create_spark_session()
    sc = spark.sparkContext
    
    print("=== 例4: キー・値ペアの RDD 操作 ===")
    
    # キー・値ペアの RDD を作成
    data = [("apple", 3), ("banana", 2), ("apple", 5), ("orange", 1)]
    rdd = sc.parallelize(data)
    
    print(f"元のデータ: {rdd.collect()}")
    
    # groupByKey: 同じキーの値をグループ化
    grouped = rdd.groupByKey()
    print("\ngroupByKey:")
    for key, values in grouped.collect():
        print(f"  {key}: {list(values)}")
    
    # reduceByKey: 同じキーの値を結合
    reduced = rdd.reduceByKey(lambda x, y: x + y)
    print(f"\nreduceByKey (同じキーの値を合計): {reduced.collect()}")
    
    # mapValues: 値だけを変換
    mapped_values = rdd.mapValues(lambda x: x * 2)
    print(f"mapValues (値を2倍): {mapped_values.collect()}")
    
    # sortByKey: キーでソート
    sorted_rdd = rdd.sortByKey()
    print(f"sortByKey: {sorted_rdd.collect()}")
    
    spark.stop()

def example_5_rdd_to_dataframe():
    """
    例5: RDD から DataFrame への変換
    
    RDD と DataFrame は相互に変換できます。
    """
    spark = create_spark_session()
    sc = spark.sparkContext
    
    print("=== 例5: RDD から DataFrame への変換 ===")
    
    # RDD を作成
    rdd = sc.parallelize([("Alice", 25), ("Bob", 30), ("Charlie", 35)])
    
    # RDD から DataFrame に変換
    df = spark.createDataFrame(rdd, ["name", "age"])
    print("RDD から DataFrame に変換:")
    df.show()
    
    # DataFrame から RDD に変換
    rdd_from_df = df.rdd
    print("\nDataFrame から RDD に変換:")
    print(rdd_from_df.collect())
    
    spark.stop()

if __name__ == "__main__":
    print("RDD を使った処理のサンプルコード\n")
    
    example_1_create_rdd()
    print("\n" + "="*50 + "\n")
    
    example_2_transformations()
    print("\n" + "="*50 + "\n")
    
    example_3_actions()
    print("\n" + "="*50 + "\n")
    
    example_4_key_value_operations()
    print("\n" + "="*50 + "\n")
    
    example_5_rdd_to_dataframe()
