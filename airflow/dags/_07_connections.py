from datetime import datetime

from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["connections"])
def connections_demo():
    """Airflow Connectionsを確認するDAG。

    Connections は DB接続情報・APIキー・ホスト名などの接続設定を
    コードから切り離して UI の Admin > Connections で管理する仕組み。

    事前準備（CLIで接続を作成）:
      docker compose exec webserver airflow connections add demo_db \\
        --conn-type postgres \\
        --conn-host postgres \\
        --conn-login airflow \\
        --conn-password airflow \\
        --conn-schema airflow \\
        --conn-port 5432
    """

    @task
    def show_connection_info() -> None:
        conn_id = "demo_db"
        try:
            conn = BaseHook.get_connection(conn_id)
            print(f"conn_id  : {conn.conn_id}")
            print(f"conn_type: {conn.conn_type}")
            print(f"host     : {conn.host}")
            print(f"schema   : {conn.schema}")
            print(f"port     : {conn.port}")
            print(f"login    : {conn.login}")
            # パスワードは ****** でマスクして表示
            print(f"password : {'*' * len(conn.password or '')}")
        except Exception as e:
            print(f"接続が見つかりません: {e}")
            print("上記の事前準備コマンドを実行してください")

    @task
    def list_all_connections() -> None:
        # 登録済みのすべての接続を確認
        from airflow.models import Connection
        from airflow.utils.session import create_session

        with create_session() as session:
            connections = session.query(Connection).all()
            print(f"登録済み接続数: {len(connections)}")
            for c in connections:
                print(f"  - {c.conn_id} ({c.conn_type})")

    show_connection_info() >> list_all_connections()


connections_demo()
