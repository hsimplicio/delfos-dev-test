from dagster import (
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_package_module,
)

from . import assets

etl_job = define_asset_job(name="etl_job")

daily_refresh_schedule = ScheduleDefinition(
    job=etl_job, cron_schedule="0 0 * * *"
)

defs = Definitions(
    assets=load_assets_from_package_module(assets),
    jobs=[etl_job],
    schedules=[daily_refresh_schedule]
)
