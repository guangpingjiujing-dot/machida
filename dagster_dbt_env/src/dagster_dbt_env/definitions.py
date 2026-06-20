from dagster import Definitions

from .defs.assets import processed_data
from .defs.dbt_assets import my_dbt_assets
from .defs.resources import dbt_resource

defs = Definitions(
    assets=[
        processed_data,
        my_dbt_assets,
    ],
    resources={
        "dbt": dbt_resource,
    },
)
