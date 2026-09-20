"""Tests for washer cycle parsing."""

from custom_components.smartthings_washer_companion.logic import (
    build_labels,
    cycle_label,
    extract_supported_cycles,
    normalise_cycle_code,
    normalise_table_id,
)


def test_extracts_supported_cycle_objects() -> None:
    assert extract_supported_cycles(
        [
            {"cycle": "Course_21", "supportedOptions": {}},
            {"cycle": "Course_1B"},
            {"cycle": "Course_21"},
        ]
    ) == ["Course_21", "Course_1B"]


def test_table_and_colours_translation() -> None:
    assert normalise_table_id({"id": "Table_02"}) == "table_02"
    assert cycle_label("Course_21", "table_02") == "Colours"


def test_unknown_cycle_is_never_guessed() -> None:
    assert cycle_label("Course_FE", "table_02") == "Course_FE"


def test_normalises_prefixed_status_value() -> None:
    assert normalise_cycle_code("Table_02_Course_21") == "Course_21"


def test_duplicate_labels_include_raw_code() -> None:
    labels, lookup = build_labels(["Course_1A", "Course_32"], "table_02")
    assert labels == ["Shirts (Course_1A)", "Shirts (Course_32)"]
    assert lookup["Shirts (Course_1A)"] == "Course_1A"
