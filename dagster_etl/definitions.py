from dagster import (
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_package_module,
    DailyPartitionsDefinition,
)

from . import assets, resources

daily_partitions_def = DailyPartitionsDefinition(start_date="2024-05-20", end_date="2024-05-30")

etl_job = define_asset_job(
    name="etl_job",
    partitions_def=daily_partitions_def
)

daily_refresh_schedule = ScheduleDefinition(
    job=etl_job, cron_schedule="0 0 * * *"
)

defs = Definitions(
    assets=load_assets_from_package_module(assets),
    jobs=[etl_job],
    schedules=[daily_refresh_schedule],
    resources={
        "fonte_conn": resources.FonteAPIResource(),
        "alvo_conn": resources.AlvoDBResource()
    },
)
