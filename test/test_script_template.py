"""Тесты для Layers/Executor/script_template.py::build_script."""
import pytest

from Layers.Executor.script_template import build_script, DEFAULT_MARKER


def test_positive_marker_replaced():
    template = f"{DEFAULT_MARKER}\nprint(TUR55_PAYLOAD['x'])\n"
    payload = {"x": 1}
    result = build_script(template, payload)
    assert "TUR55_PAYLOAD = " in result
    assert DEFAULT_MARKER not in result


def test_payload_is_valid_json():
    import json
    template = f"{DEFAULT_MARKER}\n"
    payload = {"a": 1, "b": "text"}
    result = build_script(template, payload)
    line = [l for l in result.splitlines() if l.startswith("TUR55_PAYLOAD = ")][0]
    parsed = json.loads(line[len("TUR55_PAYLOAD = "):])
    assert parsed == payload


def test_no_marker_raises():
    with pytest.raises(ValueError, match="не найден"):
        build_script("x = 1\n", {"a": 1})


def test_two_markers_raises():
    template = f"{DEFAULT_MARKER}\n{DEFAULT_MARKER}\n"
    with pytest.raises(ValueError, match="встречается 2 раз"):
        build_script(template, {"a": 1})


def test_invalid_python_raises():
    template = "if True:\n" + DEFAULT_MARKER + "\n"
    with pytest.raises(ValueError, match="не является валидным"):
        build_script(template, {"a": 1})