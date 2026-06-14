from pathlib import Path
from dagster import Definitions
from dagster_dbt import DbtCliResource

# ★ Dockerコンテナ内のdbtプロジェクトパスに変更します
DBT_PROJECT_DIR = Path("/opt/dbt/dbt_project")

# dbtリソースの定義
dbt_resource = DbtCliResource(project_dir=DBT_PROJECT_DIR)

# Definitionsにリソースを登録します
defs = Definitions(
    resources={
        "dbt": dbt_resource,
    },
)