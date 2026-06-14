from pathlib import Path
from dagster import Definitions
from dagster_dbt import DbtCliResource

# dbtプロジェクトの絶対パスを指定します
DBT_PROJECT_DIR = Path(r"C:\test_github\machida\test_dbt_pj")

# dbtリソースの定義
dbt_resource = DbtCliResource(project_dir=DBT_PROJECT_DIR)

# Definitionsにリソースを登録します
# （アセットは defs/ フォルダ内のファイルから自動検出されるため、ここではリソースのみ渡します）
defs = Definitions(
    resources={
        "dbt": dbt_resource,
    },
)