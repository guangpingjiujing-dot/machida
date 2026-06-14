from pathlib import Path
from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets, DagsterDbtTranslator

# ★ コンテナ内のパスに変更します
DBT_PROJECT_DIR = Path("/opt/dbt/dbt_project")

class MyDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, record):
        key = super().get_asset_key(record)
        
        # 辞書型（dict）としてキーにアクセスするように修正します
        if record.get("resource_type") == "source":
            return key.with_prefix(["test_dbt_pj", "sources"])
        
        return key.with_prefix(["test_dbt_pj", "models"])

@dbt_assets(
    manifest=DBT_PROJECT_DIR.joinpath("target", "manifest.json"),
    dagster_dbt_translator=MyDbtTranslator(),
)
def my_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()