from pathlib import Path
from dagster_dbt import DbtCliResource

# ★ Dockerコンテナ内のdbtプロジェクトパスに変更します
DBT_PROJECT_DIR = Path("/opt/dbt/dbt_project")

# dbtリソースの定義
dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROJECT_DIR,  # ★ profiles_dir を追加（プロジェクトディレクトリと同じ /opt/dbt/dbt_project を指定）
)
