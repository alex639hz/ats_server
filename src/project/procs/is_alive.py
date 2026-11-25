"""Heartbeat procedure: logs an 'alive' message at a fixed interval while the engine runs."""

import logging
from pathlib import Path

from ats_engine.constants import DEF_DB_COL_RUNTIME
from ats_engine.procedure import Procedure
from ats_engine.procedure_builder import ProcedureBuilder
from ats_engine.types import StepInterface
from ats_engine.utils import Utils
from ats_engine.db import database

PROCEDURE_LABEL = "is_alive"
HEARTBEAT_SECONDS = 1.0
STATION_CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "station.json"
STATION_ID = Utils.read_json(STATION_CONFIG_PATH)["station_id"]


def runtime_heartbeat(step_interface: StepInterface):
    procedure, _ = Utils.extract_step_interface(step_interface)
    count = procedure.context.attribute_get("alive_count", 0) + 1
    procedure.context.attribute_set("alive_count", count)

    start_time = procedure.framework.context.attribute_get("start_time")
    ping_time = procedure.framework.get_time_datetime()
    try:
        database.update_one(
            DEF_DB_COL_RUNTIME,
            {"start_time": start_time},
            {"last_ping": ping_time, "station_id": STATION_ID},
        )
    except Exception as err:
        procedure.log_err(f"is_alive: last_ping not saved: {err}")

    # repeat this step forever, once per HEARTBEAT_SECONDS
    procedure.nextstate_sleep_and_repeat(HEARTBEAT_SECONDS)
    return f"alive: {ping_time.isoformat()} (count={count})"


def ensure_runtime_index():
    """Index the 'runtime' collection by station_id (no-op if the index already exists)."""
    try:
        database.create_index(DEF_DB_COL_RUNTIME, "station_id")
    except Exception as err:
        logging.getLogger("[framework]").error(f"runtime index not created: {err}")


def build_is_alive_procedure() -> Procedure:
    ensure_runtime_index()
    builder = ProcedureBuilder(PROCEDURE_LABEL)
    builder.step_call(runtime_heartbeat, label="heartbeat")
    return builder.generate_procedure()
