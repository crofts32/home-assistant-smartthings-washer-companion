"""Pure parsing helpers for SmartThings washer data."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .const import CYCLE_NAMES


def key_value(key: object) -> str:
    """Return a stable string for SmartThings enum or string keys."""
    value = getattr(key, "value", key)
    return str(value)


def mapping_get(mapping: Mapping[Any, Any] | None, wanted: str) -> Any:
    """Read a mapping whose keys can be strings or string enums."""
    if not mapping:
        return None
    for key, value in mapping.items():
        if key_value(key) == wanted:
            return value
    return None


def status_value(status: Any) -> Any:
    """Extract a pysmartthings Status value, while accepting raw test data."""
    return getattr(status, "value", status)


def attribute_value(capability: Mapping[Any, Any] | None, attribute: str) -> Any:
    """Read an attribute value from a capability status mapping."""
    return status_value(mapping_get(capability, attribute))


def normalise_table_id(value: Any) -> str:
    """Normalise SmartThings referenceTable values to table_XX."""
    if isinstance(value, Mapping):
        value = value.get("id")
    if not value:
        return ""
    return str(value).strip().lower()


def normalise_cycle_code(value: Any) -> str | None:
    """Return a canonical Samsung Course_XX code."""
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip().split("_")[-2:] if value.startswith("Table_") else value
    if isinstance(value, list):
        value = "_".join(value)
    if value.lower().startswith("course_"):
        suffix = value.split("_", 1)[1].upper()
        return f"Course_{suffix}"
    return value


def extract_supported_cycles(value: Any) -> list[str]:
    """Extract cycle codes from SmartThings supportedCycles payloads."""
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        raw = item.get("cycle") if isinstance(item, Mapping) else item
        code = normalise_cycle_code(raw)
        if code and code not in result:
            result.append(code)
    return result


def cycle_label(code: str, table_id: str) -> str:
    """Return a safe friendly name, falling back to the raw device code."""
    return CYCLE_NAMES.get(table_id, {}).get(code, code)


def build_labels(codes: list[str], table_id: str) -> tuple[list[str], dict[str, str]]:
    """Build unique display labels and a display-to-code lookup."""
    labels: list[str] = []
    by_label: dict[str, str] = {}
    names = [cycle_label(code, table_id) for code in codes]
    duplicate_names = {name for name in names if names.count(name) > 1}
    for code, name in zip(codes, names, strict=True):
        label = f"{name} ({code})" if name in duplicate_names else name
        labels.append(label)
        by_label[label] = code
    return labels, by_label


def is_enabled(value: Any) -> bool:
    """Interpret SmartThings booleans consistently."""
    return value is True or str(value).lower() in {"true", "on", "enabled"}


@dataclass(frozen=True, slots=True)
class WasherCycleData:
    """Parsed washer cycle state."""

    current_code: str | None
    current_label: str | None
    labels: list[str]
    code_by_label: dict[str, str]
    table_id: str
    remote_control_enabled: bool
    machine_state: str | None
