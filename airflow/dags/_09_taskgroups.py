from datetime import datetime

from airflow.decorators import dag, task, task_group


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["taskgroup"])
def taskgroups_demo():
    """TaskGroupを確認するDAG。関連するタスクをUIでグループ化して可視化する。

    ETLパイプラインをTaskGroupで構造化する例。
    UIのGraph Viewでグループが折りたたみ表示される。
    """

    @task_group
    def extract():
        @task
        def from_db() -> str:
            print("DBからデータ取得")
            return "db_records"

        @task
        def from_api() -> str:
            print("APIからデータ取得")
            return "api_records"

        # グループ内で並列実行
        from_db()
        from_api()

    @task_group
    def transform():
        @task
        def clean() -> str:
            print("欠損値・重複を除去")
            return "cleaned"

        @task
        def normalize(data: str) -> str:
            print(f"正規化: {data}")
            return "normalized"

        # グループ内で直列実行
        normalize(clean())

    @task
    def load() -> None:
        print("データウェアハウスへ書き込み完了")

    # グループ間の依存関係
    extract() >> transform() >> load()


taskgroups_demo()
