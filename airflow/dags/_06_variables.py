from datetime import datetime

from airflow.decorators import dag, task
from airflow.models import Variable


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["variables"])
def variables_demo():
    """Airflow Variablesを確認するDAG。

    Variables は UI の Admin > Variables で管理できる設定値。
    コードを変えずに実行時の挙動を変えられる。
    """

    @task
    def setup_variables() -> None:
        # プログラムからも設定できる（通常はUIやCLIで管理する）
        Variable.set("greeting", "こんにちは、Airflow！")
        Variable.set("threshold", "80")
        Variable.set("app_config", '{"env": "dev", "debug": true}', serialize_json=False)
        print("Variablesを設定しました")

    @task
    def read_variables() -> None:
        # 存在しない場合のデフォルト値を指定できる
        greeting = Variable.get("greeting", default_var="（未設定）")
        threshold = Variable.get("threshold", default_var="0")

        # deserialize_json=True でJSONを自動でdictに変換
        config = Variable.get("app_config", default_var="{}", deserialize_json=True)

        print(f"greeting : {greeting}")
        print(f"threshold: {threshold}")
        print(f"config   : {config}")
        print(f"env      : {config.get('env')}")

    setup_variables() >> read_variables()


variables_demo()
