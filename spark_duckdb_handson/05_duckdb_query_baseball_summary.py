"""Spark の野球集計 Parquet を DuckDB の永続テーブルに取り込み、SQL で確認する。"""

# Ubuntu 側のホームディレクトリを安全に取得するために使う
from pathlib import Path

# DuckDB のデータベースと SQL を使うために読み込む
import duckdb


# Spark が作成した年別集計の Parquet フォルダを指定する
PARQUET_DIRECTORY = (
    Path.home()
    / "workspace"
    / "spark_duckdb_output"
    / "baseball"
    / "event_and_game_counts_by_year"
)

# DuckDB のデータベースファイルを Ubuntu 側に作成する
# このファイルに、これから作る baseball_year_summary テーブルが保存される
DATABASE_PATH = (
    Path.home()
    / "workspace"
    / "spark_duckdb_output"
    / "baseball"
    / "baseball.duckdb"
)


def print_rows(heading: str, column_names: list[str], rows: list[tuple]) -> None:
    """SQL の実行結果を、見やすい文字列表として表示する。"""

    print(f"\n{heading}")
    print(" | ".join(column_names))
    print("-" * 60)
    for row in rows:
        print(" | ".join(str(value) for value in row))


def main() -> None:
    """Parquet の取込み、テーブル作成、SQL 実行を順番に行う。"""

    # Spark の出力がない状態で実行した場合、次の操作を案内する
    if not PARQUET_DIRECTORY.is_dir():
        print(f"Parquet フォルダが見つかりません: {PARQUET_DIRECTORY}")
        print("先に `python 04_read_baseball_csv.py --extract` を実行してください。")
        return

    # Spark が出力した part-...parquet を、ワイルドカードでまとめて指定する
    parquet_pattern = PARQUET_DIRECTORY / "*.parquet"

    # Ubuntu 側に baseball.duckdb を開く（初回は新規作成される）
    connection = duckdb.connect(database=str(DATABASE_PATH))

    try:
        # Parquet を読み込み、DuckDB 内に永続テーブルを作る SQL
        # OR REPLACE により、Spark で再集計した後も同じコマンドで最新データへ更新できる
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE baseball_year_summary AS
            SELECT *
            FROM read_parquet('{parquet_pattern}')
            """
        )

        print("DuckDB に永続テーブルを作成しました。")
        print(f"データベースファイル: {DATABASE_PATH}")
        print("テーブル名: baseball_year_summary")

        # SQL で、Spark の集計結果を年度・シーズン種別の順に確認する
        result = connection.execute(
            """
            SELECT
                year,
                seasonType,
                event_row_count,
                game_count
            FROM baseball_year_summary
            ORDER BY year, seasonType
            """
        )
        rows = result.fetchall()
        column_names = [column[0] for column in result.description]
        print_rows("SQL の実行結果:", column_names, rows)

        # テーブル内の行数を SQL で確認する
        table_row_count = connection.execute(
            "SELECT COUNT(*) FROM baseball_year_summary"
        ).fetchone()[0]
        print(f"\nテーブルの行数: {table_row_count}")
    finally:
        # データベースファイルへの接続を閉じ、内容を保存する
        connection.close()


if __name__ == "__main__":
    # このファイルを直接実行したときだけ main() を動かす
    main()
