from datetime import datetime

from airflow.decorators import dag, task


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["dynamic"])
def dynamic_tasks_demo():
    """Dynamic Task Mappingを確認するDAG。

    .expand() を使うとリストの要素数だけタスクを動的に生成できる。
    処理対象が実行時まで決まらない場合に有効。
    """

    @task
    def get_items() -> list[str]:
        items = ["apple", "banana", "cherry", "date", "elderberry"]
        print(f"{len(items)}件のアイテムを処理します")
        return items

    @task
    def process_item(item: str) -> str:
        result = item.upper()
        print(f"{item} → {result}")
        return result

    @task
    def summarize(results: list[str]) -> None:
        print(f"全{len(results)}件の処理が完了しました")
        for r in results:
            print(f"  - {r}")

    items = get_items()
    # .expand() で items の要素数分だけ process_item タスクが生成される
    # UIのGraph Viewで "process_item[0]", "process_item[1]"... と表示される
    processed = process_item.expand(item=items)
    summarize(processed)


dynamic_tasks_demo()
