"""Spark が出力した Parquet を DuckDB で読むサンプル。"""

# Ubuntu 側のホームディレクトリを安全に取得するために使う
from pathlib import Path

# Parquet を SQL で読むための DuckDB を読み込む
import duckdb


# Spark が作成した Parquet フォルダを指定する
# Path.home() は、この環境では /home/sparkuser を指す
PARQUET_DIRECTORY = (
    Path.home()
    / "workspace"
    / "spark_duckdb_output"
    / "people_by_city"
)


def main() -> None:
    """Parquet の内容を DuckDB の SQL で表示する。"""

    # 先に Spark の出力が存在するか確認し、原因が分かるエラーにする
    if not PARQUET_DIRECTORY.is_dir():
        print(f"Parquet フォルダが見つかりません: {PARQUET_DIRECTORY}")
        print("先に `python 02_spark_to_parquet.py` を実行してください。")
        return

    # Spark は part-...parquet という名前のファイルを作るため、* でまとめて指定する
    parquet_pattern = PARQUET_DIRECTORY / "*.parquet"

    # DuckDB をメモリ上で起動する
    # database=":memory:" のため、この確認では .duckdb ファイルは作成しない
    connection = duckdb.connect(database=":memory:")

    try:
        # read_parquet() で Spark が作った Parquet を直接テーブルのように読む
        # city の昇順に並べ、Spark の集計結果と同じ順序で表示する
        query = f"""
            SELECT city, people_count, average_age
            FROM read_parquet('{parquet_pattern}')
            ORDER BY city
        """
        result = connection.execute(query)

        # SQL の結果を取得する
        rows = result.fetchall()
        column_names = [column[0] for column in result.description]

        # 取得した列名と行を、初心者にも読める形で表示する
        print("DuckDB で読み込んだ集計結果:")
        print(" | ".join(column_names))
        print("-" * 40)
        for row in rows:
            print(" | ".join(str(value) for value in row))

        print(f"\n読み込んだ Parquet: {parquet_pattern}")
        print(f"件数: {len(rows)} 行")
    finally:
        # DuckDB との接続を閉じる
        connection.close()


if __name__ == "__main__":
    # このファイルを直接実行したときだけ main() を動かす
    main()
