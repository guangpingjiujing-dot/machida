import pandas as pd

import dagster as dg

# マウント先のコンテナ内パス（/opt/dagster/app）を指定します
sample_data_file = "/opt/dagster/app/sample.csv"
processed_data_file = "/opt/dagster/app/sample_out.csv"


@dg.asset
def processed_data():
    ## Read data from the CSV
    df = pd.read_csv(sample_data_file)

    ## Add an age_group column based on the value of age
    df["age_group"] = pd.cut(
        df["age"], bins=[0, 30, 40, 100], labels=["Young", "Middle", "Senior"]
    )

    ## Save processed data
    df.to_csv(processed_data_file, index=False)
    return "Data loaded successfully"