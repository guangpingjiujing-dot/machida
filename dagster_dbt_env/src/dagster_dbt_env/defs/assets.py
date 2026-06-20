import os
from pathlib import Path

import pandas as pd
import dagster as dg

_app_dir = Path(os.getenv("DAGSTER_APP_DIR", "/opt/dagster/app"))
sample_data_file = _app_dir / "sample.csv"
processed_data_file = _app_dir / "sample_out.csv"


@dg.asset
def processed_data():
    df = pd.read_csv(sample_data_file)
    df["age_group"] = pd.cut(
        df["age"], bins=[0, 30, 40, 100], labels=["Young", "Middle", "Senior"]
    )
    df.to_csv(processed_data_file, index=False)
    return "Data loaded successfully"
