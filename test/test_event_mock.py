"""Тесты для Layers/Event/ethereum.py::_listen_mock."""
from Layers.Event.ethereum import listen


def test_mock_returns_three_events(mock_config):
    events = list(listen(mock_config))
    assert len(events) == 3


def test_mock_event_fields(mock_config):
    events = list(listen(mock_config))
    ev = events[0]
    for key in ("user_wallet", "amount", "expires", "device_id", "metadata", "custom_data"):
        assert key in ev, f"missing field: {key}"
    assert ev["device_id"] == "esp32_001"
    assert ev["custom_data"] == {"duration_sec": 120}
    assert ev["user_wallet"].startswith("0x")
    assert len(ev["user_wallet"]) == 42


def test_mock_deterministic(mock_config):
    a = list(listen(mock_config))
    b = list(listen(mock_config))
    for ea, eb in zip(a, b):
        assert ea["user_wallet"] == eb["user_wallet"]
        assert ea["amount"] == eb["amount"]
        assert ea["metadata"] == eb["metadata"]
        assert ea["custom_data"] == eb["custom_data"]