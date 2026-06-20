from pathlib import Path
from dagster_dbt import DbtCliResource

DBT_PROJECT_DIR = Path("/opt/dbt/dbt_project")

dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROJECT_DIR,
)
