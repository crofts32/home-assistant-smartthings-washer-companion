"""Tests for washer cycle parsing."""

from datetime import UTC, datetime

from custom_components.smartthings_washer_companion.logic import (
    build_labels,
    cycle_label,
    delay_minutes_for_finish,
    extract_supported_cycles,
    infer_table_id,
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


def test_infers_unambiguous_table_from_supported_cycles() -> None:
    assert infer_table_id(["Course_1C", "Course_21", "Course_96"]) == "table_02"


def test_does_not_infer_ambiguous_table() -> None:
    assert infer_table_id(["Course_1B"]) == ""


def test_unknown_cycle_is_never_guessed() -> None:
    assert cycle_label("Course_FE", "table_02") == "Course_FE"


def test_normalises_prefixed_status_value() -> None:
    assert normalise_cycle_code("Table_02_Course_21") == "Course_21"


def test_normalises_bare_hex_cycle_code() -> None:
    assert normalise_cycle_code("21") == "Course_21"
    assert normalise_cycle_code("1c") == "Course_1C"


def test_duplicate_labels_include_raw_code() -> None:
    labels, lookup = build_labels(["Course_1A", "Course_32"], "table_02")
    assert labels == ["Shirts (Course_1A)", "Shirts (Course_32)"]
    assert lookup["Shirts (Course_1A)"] == "Course_1A"


def test_delay_minutes_rounds_down_to_five_minutes() -> None:
    now = datetime(2026, 9, 20, 22, 2, 31, tzinfo=UTC)
    finish = datetime(2026, 9, 21, 5, 55, 0, tzinfo=UTC)
    assert delay_minutes_for_finish(now, finish) == 470


def test_delay_minutes_rejects_past_time() -> None:
    now = datetime(2026, 9, 20, 22, 0, tzinfo=UTC)
    try:
        delay_minutes_for_finish(now, now)
    except ValueError as err:
        assert str(err) == "Finish time must be in the future"
    else:
        raise AssertionError("Expected ValueError")
