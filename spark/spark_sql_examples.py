"""
Spark SQL を使った処理のサンプルコード

Spark SQL を使うと、SQL クエリで DataFrame を操作できます。
SQL に慣れている人には、より直感的な方法です。
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

def create_spark_session():
    """SparkSession を作成"""
    spark = SparkSession.builder \
        .appName("SparkSQLExamples") \
        .master("local[*]") \
        .getOrCreate()
    return spark

def example_1_create_temp_view():
    """
    例1: 一時ビュー（Temporary View）の作成
    
    Spark SQL を使うには、DataFrame を一時ビューとして登録する必要があります。
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
    
    print("=== 例1: 一時ビュー（Temporary View）の作成 ===")
    print("元のデータ:")
    df.show()
    
    # 一時ビューとして登録
    df.createOrReplaceTempView("employees")
    
    # SQL クエリを実行
    result = spark.sql("SELECT * FROM employees")
    print("\nSQL で全データを取得:")
    result.show()
    
    spark.stop()

def example_2_basic_sql_queries():
    """
    例2: 基本的な SQL クエリ
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
    df.createOrReplaceTempView("employees")
    
    print("=== 例2: 基本的な SQL クエリ ===")
    
    # SELECT
    print("\n1. 特定の列を選択:")
    spark.sql("SELECT name, age FROM employees").show()
    
    # WHERE
    print("\n2. 条件でフィルタリング（年齢が30以上）:")
    spark.sql("SELECT * FROM employees WHERE age >= 30").show()
    
    # ORDER BY
    print("\n3. 並び替え（給与の降順）:")
    spark.sql("SELECT * FROM employees ORDER BY salary DESC").show()
    
    # LIMIT
    print("\n4. 最初の3行を取得:")
    spark.sql("SELECT * FROM employees LIMIT 3").show()
    
    spark.stop()

def example_3_aggregate_functions():
    """
    例3: 集計関数
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
    df.createOrReplaceTempView("employees")
    
    print("=== 例3: 集計関数 ===")
    
    # 全体の集計
    print("\n1. 全体の統計情報:")
    spark.sql("""
        SELECT 
            COUNT(*) as count,
            AVG(salary) as avg_salary,
            MAX(salary) as max_salary,
            MIN(salary) as min_salary,
            SUM(salary) as total_salary
        FROM employees
    """).show()
    
    # GROUP BY
    print("\n2. 部署ごとの平均給与:")
    spark.sql("""
        SELECT 
            department,
            COUNT(*) as count,
            AVG(salary) as avg_salary,
            MAX(salary) as max_salary,
            MIN(salary) as min_salary
        FROM employees
        GROUP BY department
    """).show()
    
    # HAVING
    print("\n3. 平均給与が50000以上の部署:")
    spark.sql("""
        SELECT 
            department,
            AVG(salary) as avg_salary
        FROM employees
        GROUP BY department
        HAVING AVG(salary) >= 50000
    """).show()
    
    spark.stop()

def example_4_joins():
    """
    例4: JOIN 操作
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
    employees_df.createOrReplaceTempView("employees")
    
    # 部署データ
    departments_data = [
        ("Engineering", "Tokyo"),
        ("Marketing", "Osaka"),
        ("Sales", "Tokyo")
    ]
    departments_df = spark.createDataFrame(departments_data, ["department", "location"])
    departments_df.createOrReplaceTempView("departments")
    
    print("=== 例4: JOIN 操作 ===")
    print("従業員データ:")
    employees_df.show()
    print("\n部署データ:")
    departments_df.show()
    
    # INNER JOIN
    print("\n1. 内部結合（INNER JOIN）:")
    spark.sql("""
        SELECT e.name, e.department, d.location
        FROM employees e
        INNER JOIN departments d
        ON e.department = d.department
    """).show()
    
    # LEFT JOIN
    print("\n2. 左外部結合（LEFT JOIN）:")
    spark.sql("""
        SELECT e.name, e.department, d.location
        FROM employees e
        LEFT JOIN departments d
        ON e.department = d.department
    """).show()
    
    # RIGHT JOIN
    print("\n3. 右外部結合（RIGHT JOIN）:")
    spark.sql("""
        SELECT e.name, e.department, d.location
        FROM employees e
        RIGHT JOIN departments d
        ON e.department = d.department
    """).show()
    
    spark.stop()

def example_5_subqueries():
    """
    例5: サブクエリ
    """
    spark = create_spark_session()
    
    data = [
        ("Alice", "Engineering", 50000),
        ("Bob", "Marketing", 45000),
        ("Charlie", "Engineering", 60000),
        ("Diana", "Sales", 40000),
        ("Eve", "Engineering", 55000)
    ]
    df = spark.createDataFrame(data, ["name", "department", "salary"])
    df.createOrReplaceTempView("employees")
    
    print("=== 例5: サブクエリ ===")
    
    # 平均給与以上の人のみを取得
    print("\n1. 平均給与以上の人のみ:")
    spark.sql("""
        SELECT name, salary
        FROM employees
        WHERE salary >= (SELECT AVG(salary) FROM employees)
    """).show()
    
    # 部署ごとの平均給与と比較
    print("\n2. 部署ごとの平均給与と比較:")
    spark.sql("""
        SELECT 
            e.name,
            e.department,
            e.salary,
            d.avg_dept_salary
        FROM employees e
        INNER JOIN (
            SELECT department, AVG(salary) as avg_dept_salary
            FROM employees
            GROUP BY department
        ) d
        ON e.department = d.department
        WHERE e.salary >= d.avg_dept_salary
    """).show()
    
    spark.stop()

def example_6_window_functions():
    """
    例6: ウィンドウ関数
    """
    spark = create_spark_session()
    
    data = [
        ("Alice", "Engineering", 50000),
        ("Bob", "Marketing", 45000),
        ("Charlie", "Engineering", 60000),
        ("Diana", "Sales", 40000),
        ("Eve", "Engineering", 55000)
    ]
    df = spark.createDataFrame(data, ["name", "department", "salary"])
    df.createOrReplaceTempView("employees")
    
    print("=== 例6: ウィンドウ関数 ===")
    
    # RANK
    print("\n1. 部署ごとのランク:")
    spark.sql("""
        SELECT 
            name,
            department,
            salary,
            RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank
        FROM employees
    """).show()
    
    # DENSE_RANK
    print("\n2. 部署ごとの DENSE_RANK:")
    spark.sql("""
        SELECT 
            name,
            department,
            salary,
            DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dense_rank
        FROM employees
    """).show()
    
    # ROW_NUMBER
    print("\n3. 部署ごとの ROW_NUMBER:")
    spark.sql("""
        SELECT 
            name,
            department,
            salary,
            ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as row_number
        FROM employees
    """).show()
    
    # 部署ごとの平均給与を各行に追加
    print("\n4. 部署ごとの平均給与を追加:")
    spark.sql("""
        SELECT 
            name,
            department,
            salary,
            AVG(salary) OVER (PARTITION BY department) as avg_dept_salary
        FROM employees
    """).show()
    
    spark.stop()

def example_7_case_when():
    """
    例7: CASE WHEN 文
    """
    spark = create_spark_session()
    
    data = [
        ("Alice", 50000),
        ("Bob", 45000),
        ("Charlie", 60000),
        ("Diana", 40000)
    ]
    df = spark.createDataFrame(data, ["name", "salary"])
    df.createOrReplaceTempView("employees")
    
    print("=== 例7: CASE WHEN 文 ===")
    print("元のデータ:")
    df.show()
    
    # CASE WHEN でカテゴリを追加
    print("\n給与に基づいてカテゴリを追加:")
    spark.sql("""
        SELECT 
            name,
            salary,
            CASE 
                WHEN salary >= 55000 THEN 'High'
                WHEN salary >= 45000 THEN 'Medium'
                ELSE 'Low'
            END as salary_category
        FROM employees
    """).show()
    
    spark.stop()

def example_8_cte():
    """
    例8: 共通テーブル式（CTE: Common Table Expression）
    
    WITH 句を使うと、複雑なクエリを読みやすく書けます。
    """
    spark = create_spark_session()
    
    data = [
        ("Alice", "Engineering", 50000),
        ("Bob", "Marketing", 45000),
        ("Charlie", "Engineering", 60000),
        ("Diana", "Sales", 40000),
        ("Eve", "Engineering", 55000)
    ]
    df = spark.createDataFrame(data, ["name", "department", "salary"])
    df.createOrReplaceTempView("employees")
    
    print("=== 例8: 共通テーブル式（CTE） ===")
    
    # CTE を使ったクエリ
    print("\n部署ごとの統計情報と、平均以上の人のみを取得:")
    spark.sql("""
        WITH dept_stats AS (
            SELECT 
                department,
                AVG(salary) as avg_salary,
                MAX(salary) as max_salary
            FROM employees
            GROUP BY department
        ),
        high_earners AS (
            SELECT 
                e.name,
                e.department,
                e.salary,
                d.avg_salary
            FROM employees e
            INNER JOIN dept_stats d
            ON e.department = d.department
            WHERE e.salary >= d.avg_salary
        )
        SELECT * FROM high_earners
        ORDER BY salary DESC
    """).show()
    
    spark.stop()

if __name__ == "__main__":
    print("Spark SQL を使った処理のサンプルコード\n")
    
    example_1_create_temp_view()
    print("\n" + "="*50 + "\n")
    
    example_2_basic_sql_queries()
    print("\n" + "="*50 + "\n")
    
    example_3_aggregate_functions()
    print("\n" + "="*50 + "\n")
    
    example_4_joins()
    print("\n" + "="*50 + "\n")
    
    example_5_subqueries()
    print("\n" + "="*50 + "\n")
    
    example_6_window_functions()
    print("\n" + "="*50 + "\n")
    
    example_7_case_when()
    print("\n" + "="*50 + "\n")
    
    example_8_cte()
