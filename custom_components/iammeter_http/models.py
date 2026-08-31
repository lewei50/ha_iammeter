"""IAMMETER local monitor data models and parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

MODEL_3080 = "WEM3080"
MODEL_3080T = "WEM3080T"
MODEL_3046T = "WEM3046T"
MODEL_3050T = "WEM3050T"
MODEL_2067 = "WEM2067"
MODEL_3063T = "WEM3063T"
MODEL_3162 = "WEM3162"

METHOD_MODEL_MAP = {
    1: MODEL_3080,
    2: MODEL_3080T,
    3: MODEL_3046T,
    4: MODEL_3050T,
    5: MODEL_2067,
    6: MODEL_3063T,
}

PHASE_COUNT = {
    MODEL_3080: 1,
    MODEL_3080T: 3,
    MODEL_3046T: 3,
    MODEL_3050T: 3,
    MODEL_2067: 2,
    MODEL_3063T: 3,
}

_METHOD_PATTERN = re.compile(r"^([1-6])-.+$")
_PHASE_NAMES = ("A", "B", "C")


class IammeterDataError(ValueError):
    """Raised when a monitor payload is malformed."""


@dataclass(slots=True)
class IammeterReading:
    """Parsed IAMMETER monitor data."""

    model: str
    measurement: dict[str, float]
    serial_number: str | None = None
    mac: str | None = None
    firmware_version: str | None = None


def _metadata(payload: dict[str, Any]) -> dict[str, str | None]:
    """Return normalized device metadata."""
    return {
        "serial_number": payload.get("SN") or payload.get("sn"),
        "mac": payload.get("mac") or payload.get("MAC"),
        "firmware_version": payload.get("version"),
    }


def _validate_row(row: Any, minimum_length: int, label: str) -> list[Any]:
    """Validate one measurement row."""
    if not isinstance(row, list) or len(row) < minimum_length:
        raise IammeterDataError(
            f"{label} must contain at least {minimum_length} values"
        )
    return row


def _parse_single_phase(payload: dict[str, Any], key: str) -> IammeterReading:
    """Parse a legacy single-phase payload."""
    row = _validate_row(payload[key], 5, key)
    measurement = {
        "Voltage": row[0],
        "Current": row[1],
        "Power": row[2],
        "ImportEnergy": row[3],
        "ExportGrid": row[4],
    }
    measurement.update(_parse_reactive(payload, 1))
    model = MODEL_3162 if key == "data" else MODEL_3080
    return IammeterReading(model=model, measurement=measurement, **_metadata(payload))


def _model_from_method(method: Any) -> str:
    """Resolve a current-format method, falling back for legacy payloads."""
    if isinstance(method, str) and (match := _METHOD_PATTERN.fullmatch(method)):
        return METHOD_MODEL_MAP[int(match.group(1))]
    return MODEL_3080T


def _parse_phase(row: list[Any], phase: str) -> dict[str, float]:
    """Parse one multi-channel phase row."""
    return {
        f"Voltage_{phase}": row[0],
        f"Current_{phase}": row[1],
        f"Power_{phase}": row[2],
        f"ImportEnergy_{phase}": row[3],
        f"ExportGrid_{phase}": row[4],
        f"Frequency_{phase}": row[5],
        f"PF_{phase}": row[6],
    }


def _parse_net(row: list[Any]) -> dict[str, float]:
    """Parse an optional Net Metering summary row."""
    return {
        "Voltage_Net": row[0],
        "Power_Net": row[2],
        "ImportEnergy_Net": row[3],
        "ExportGrid_Net": row[4],
        "Frequency_Net": row[5],
        "PF_Net": row[6],
    }


def _parse_reactive(payload: dict[str, Any], phase_count: int) -> dict[str, float]:
    """Parse optional per-phase reactive measurements."""
    ea = payload.get("EA")
    if not isinstance(ea, dict) or "Reactive" not in ea:
        return {}
    rows = ea["Reactive"]
    if not isinstance(rows, list):
        raise IammeterDataError("EA.Reactive must be a list")

    measurement: dict[str, float] = {}
    for index, row in enumerate(rows[:phase_count]):
        row = _validate_row(row, 3, f"EA.Reactive[{index}]")
        phase = _PHASE_NAMES[index]
        measurement.update(
            {
                f"ReactivePower_{phase}": row[0],
                f"InductiveReactiveEnergy_{phase}": row[1],
                f"CapacitiveReactiveEnergy_{phase}": row[2],
            }
        )
    return measurement


def parse_monitor_payload(payload: Any) -> IammeterReading:
    """Parse `/monitorjson` or `/api/monitorjson` response data."""
    if not isinstance(payload, dict):
        raise IammeterDataError("Monitor response must be a JSON object")

    if "Data" in payload:
        return _parse_single_phase(payload, "Data")
    if "data" in payload:
        return _parse_single_phase(payload, "data")
    if "Datas" not in payload:
        raise IammeterDataError("Monitor response contains neither Data nor Datas")

    rows = payload["Datas"]
    if not isinstance(rows, list):
        raise IammeterDataError("Datas must be a list")

    model = _model_from_method(payload.get("method"))
    phase_count = PHASE_COUNT[model]
    if len(rows) < phase_count:
        raise IammeterDataError(
            f"{model} requires {phase_count} phase rows, received {len(rows)}"
        )

    measurement: dict[str, float] = {}
    for index in range(phase_count):
        row = _validate_row(rows[index], 7, f"Datas[{index}]")
        measurement.update(_parse_phase(row, _PHASE_NAMES[index]))

    # The row immediately after the model's physical phases is the optional
    # Net Metering summary. For WEM2067 this is Datas[2], never a C phase.
    if phase_count > 1 and len(rows) > phase_count:
        net_row = _validate_row(rows[phase_count], 7, f"Datas[{phase_count}]")
        measurement.update(_parse_net(net_row))

    measurement.update(_parse_reactive(payload, phase_count))
    return IammeterReading(model=model, measurement=measurement, **_metadata(payload))
