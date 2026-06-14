from pathlib import Path
from dagster import Definitions
from dagster_dbt import DbtCliResource

from .defs.assets import processed_data
from .defs.dbt_assets import my_dbt_assets

DBT_PROJECT_DIR = Path("/opt/dbt/dbt_project")

defs = Definitions(
    assets=[
        processed_data,
        my_dbt_assets,
    ],
    resources={
        # ★ profiles_dir を追加（プロジェクトディレクトリと同じ /opt/dbt/dbt_project を指定）
        "dbt": DbtCliResource(
            project_dir=DBT_PROJECT_DIR, 
            profiles_dir=DBT_PROJECT_DIR
        ),
    },
)