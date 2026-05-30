from datetime import datetime
from pathlib import Path
import pendulum
from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import GoogleCloudServiceAccountDictProfileMapping

DBT_PROJECT_PATH = Path("/opt/airflow/test_dbt_pj")
local_tz = pendulum.timezone("Asia/Tokyo")

cosmos_dag = DbtDag(
    dag_id="dbt_after_cosmos",
    start_date=datetime(2026, 5, 23, tzinfo=local_tz),
    schedule_interval="0 7 * * *",
    catchup=False,
    
    project_config=ProjectConfig(
        dbt_project_path=DBT_PROJECT_PATH,
    ),
    profile_config=ProfileConfig(
        profile_name="test_dbt_pj", 
        target_name="dev",
        profile_mapping=GoogleCloudServiceAccountDictProfileMapping(
            conn_id="my_gcp_connection", 
            profile_args={"dataset": "my_practice_ds"},
        ),
    ),
    execution_config=ExecutionConfig(
        dbt_executable_path="dbt", 
    ),
)