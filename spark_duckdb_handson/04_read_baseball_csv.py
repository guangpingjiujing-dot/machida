"""50 個の野球 CSV を Spark で読み込み、年別の件数を Parquet へ保存する。"""

# コマンドライン引数（--extract）を受け取るために使う
import argparse

# ZIP を展開するために使う
import zipfile

# ファイルやフォルダのパスを扱うために使う
from pathlib import Path

# Spark を起動するための機能を読み込む
from pyspark.sql import SparkSession

# 実行終了後も Spark History Server で結果を確認できるようにする
from spark_history import configure_event_logging

# 件数を数える集計関数を F という短い名前で読み込む
from pyspark.sql import functions as F


# この Python ファイルが置かれているプロジェクトのフォルダを取得する
PROJECT_DIRECTORY = Path(__file__).resolve().parent

# Windows 側のプロジェクト内にある、元の ZIP ファイルを指定する
ZIP_PATH = PROJECT_DIRECTORY / "input" / "baseball_data.zip"

# ZIP を展開する Windows 側の入力フォルダを指定する
CSV_DIRECTORY = PROJECT_DIRECTORY / "input" / "baseball"

# Spark の Parquet 出力は Linux の権限を扱える Ubuntu 側に置く
OUTPUT_DIRECTORY = (
    Path.home()
    / "workspace"
    / "spark_duckdb_output"
    / "baseball"
    / "event_and_game_counts_by_year"
)


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数を読み取る。"""

    parser = argparse.ArgumentParser(
        description="野球 CSV を Spark で読み込み、年別件数を Parquet に保存します。"
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="input/baseball_data.zip を input/baseball/ へ展開してから処理します。",
    )
    return parser.parse_args()


def get_csv_files() -> list[Path]:
    """展開済みの野球 CSV ファイル一覧を返す。"""

    return sorted(CSV_DIRECTORY.glob("games_wide-*.csv"))


def extract_csv_files() -> None:
    """ZIP 内の CSV を input/baseball/ へ展開する。"""

    if not ZIP_PATH.is_file():
        raise FileNotFoundError(f"入力 ZIP が見つかりません: {ZIP_PATH}")

    # ZIP と CSV の保存先は Windows 側のプロジェクト内に置く
    CSV_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH) as archive:
        csv_entries = [entry for entry in archive.infolist() if entry.filename.endswith(".csv")]
        print(f"ZIP を展開します: {ZIP_PATH}")
        print(f"展開先: {CSV_DIRECTORY}")

        # 進捗が見えるよう、10 ファイルごとに現在位置を表示する
        for index, entry in enumerate(csv_entries, start=1):
            archive.extract(entry, CSV_DIRECTORY)
            if index % 10 == 0 or index == len(csv_entries):
                print(f"  展開済み: {index} / {len(csv_entries)} ファイル")


def main() -> None:
    """データ準備、Spark による集計、Parquet 保存を順番に実行する。"""

    arguments = parse_arguments()
    csv_files = get_csv_files()

    # --extract が指定された場合だけ、容量の大きい ZIP 展開を実行する
    if arguments.extract and not csv_files:
        extract_csv_files()
        csv_files = get_csv_files()

    # 展開なしで実行したときに、次に何をすればよいかを明確に表示する
    if not csv_files:
        raise FileNotFoundError(
            f"CSV が見つかりません: {CSV_DIRECTORY}\n"
            "最初の一回だけ、次のコマンドを実行してください。\n"
            "python 04_read_baseball_csv.py --extract"
        )

    print(f"読み込む CSV ファイル数: {len(csv_files)}")
    print(f"CSV の場所: {CSV_DIRECTORY}")

    # Spark をローカル PC 上で起動する
    # local[2] は、この PC で最大 2 個のタスクを同時に実行する設定
    # これは「同時に働ける作業員の数」であり、パーティション数そのものではない
    spark = (
        configure_event_logging(SparkSession.builder)
        .appName("ReadBaseballCsv")
        .master("local[2]")
        # groupBy() 後に結果を集め直す処理（Shuffle）の分割数を 4 とする学習用設定
        # Spark の最適化により、実際の分割数がこの値と完全に一致しない場合もある
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    try:
        # 実行ログを減らし、ハンズオンの結果を読みやすくする
        spark.sparkContext.setLogLevel("ERROR")

        # 50 個の CSV をワイルドカードで一括して DataFrame として読み込む
        # Spark の Driver がファイルの数・サイズなどから「読み込みの仕事」を自動で分ける
        # パーティション数はコードで固定しておらず、入力データや設定により毎回変わり得る
        # まずは全列を文字列として読み込み、読み込み処理を安定させる
        csv_pattern = str(CSV_DIRECTORY / "games_wide-*.csv")
        raw_df = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "false")
            .option("mode", "PERMISSIVE")
            .csv(csv_pattern)
        )

        # Driver が作った読み込み計画を表示する
        # 今回の実行結果は 50 CSV / 17 パーティションだった
        # 17 個の仕事は local[2] により、最大 2 個ずつ順番に実行される
        print(f"Spark が認識した入力ファイル数: {len(raw_df.inputFiles())}")
        print(f"読み込み時のパーティション数: {raw_df.rdd.getNumPartitions()}")
        print(f"列数: {len(raw_df.columns)}")

        # この集計に必要な列が欠けていないか確認する
        required_columns = {"year", "seasonType", "gameId"}
        missing_columns = required_columns - set(raw_df.columns)
        if missing_columns:
            raise ValueError(f"必要な列が見つかりません: {sorted(missing_columns)}")

        # 1行は投球・打席などのイベント単位で、同じ gameId が複数行現れる
        # そのため、イベント行数と gameId の重複を除いた試合数を分けて集計する
        # groupBy() は、各パーティションの途中結果を同じ year・seasonType ごとに集め直す
        # この「分けて数え、同じキーごとに集める」処理が Shuffle（シャッフル）である
        summary_df = (
            raw_df
            .where(F.col("gameId").isNotNull())
            .groupBy("year", "seasonType")
            .agg(
                F.count("*").alias("event_row_count"),
                F.countDistinct("gameId").alias("game_count"),
            )
            .orderBy("year", "seasonType")
            # 小さな集計結果をキャッシュし、表示と保存で元データを読み直さない
            .cache()
        )

        # collect() が Spark の実際の読み込み・分散集計を開始する（Action）
        # 読み込みの17個の仕事は、この時点で最大2個ずつ実行される
        # Python 側へ戻すのは元の76万行ではなく、小さな年別集計結果だけである
        summary_rows = summary_df.collect()
        total_event_rows = sum(row["event_row_count"] for row in summary_rows)
        total_game_count = sum(row["game_count"] for row in summary_rows)

        print(f"イベント行数の合計: {total_event_rows:,}")
        print(f"年別に集計した試合数の合計: {total_game_count:,}")
        print("年別・シーズン種別の集計結果:")
        summary_df.show(100, truncate=False)

        # Spark の集計結果を Ubuntu 側へ Parquet として保存する
        # overwrite は同じ出力先がある場合に、その集計結果を上書きする設定
        summary_df.write.mode("overwrite").parquet(str(OUTPUT_DIRECTORY))
        print(f"Parquet output: {OUTPUT_DIRECTORY}")
    finally:
        # Spark を終了し、使用したメモリや Java プロセスを解放する
        spark.stop()


if __name__ == "__main__":
    # このファイルを直接実行したときだけ main() を動かす
    main()
