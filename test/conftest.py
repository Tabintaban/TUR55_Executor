"""Общие фикстуры для тестов TUR55_Executor."""
import sys
from pathlib import Path

import pytest

# Чтобы `from Layers...` работало при запуске из test/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
KEYS_DIR = REPO_ROOT / "keys"
PROGRAM_LED = REPO_ROOT / "inputfiles" / "example_led.json"


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def keys_dir() -> Path:
    return KEYS_DIR


@pytest.fixture
def program_led() -> Path:
    return PROGRAM_LED


@pytest.fixture
def sample_event() -> dict:
    return {
        "user_wallet": "0xabc",
        "amount": 50,
        "expires": 1792407556,
        "device_id": "esp32_001",
        "custom_data": {"duration_sec": 120},
    }


@pytest.fixture
def mock_config() -> dict:
    return {
        "executor": {"name": "TUR55_Executor", "version": "0.1.0", "device_id": "esp32_001"},
        "event": {
            "blockchain": "ethereum",
            "use_mock": True,
            "mock": {"max_events": 3, "interval_sec": 0.0, "seed": 0, "custom_data": {"duration_sec": 120}},
        },
        "delivery": {
            "transport": "file",
            "file": {"output_dir": "outputfiles/", "filename": "program.enc"},
        },
        "inputfiles": {"template": "inputfiles/example_led.json"},
    }