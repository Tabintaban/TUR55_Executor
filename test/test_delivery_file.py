"""Тесты для Layers/Delivery/FILE.py::save."""
import pytest

from Layers.Delivery.FILE import save


@pytest.fixture
def delivery_config(tmp_path):
    """Конфиг с временной папкой для output."""
    return {
        "delivery": {
            "transport": "file",
            "file": {
                "output_dir": str(tmp_path),
                "filename": "test_program.enc",
            },
        }
    }


def test_save_creates_file(delivery_config):
    packet = b"TUR5" + b"\x00" * 100
    path = save(packet, delivery_config)
    assert path.exists()
    assert path.name == "test_program.enc"


def test_save_writes_correct_bytes(delivery_config):
    packet = b"TUR5TESTDATA" + bytes(range(256))
    path = save(packet, delivery_config)
    assert path.read_bytes() == packet


def test_save_creates_output_dir(tmp_path):
    """Если папки нет — создаётся."""
    cfg = {
        "delivery": {
            "file": {
                "output_dir": str(tmp_path / "nested" / "deep"),
                "filename": "x.enc",
            }
        }
    }
    path = save(b"TUR5", cfg)
    assert path.exists()
    assert path.parent.is_dir()


def test_save_overwrites(delivery_config):
    """Повторное сохранение перезаписывает файл."""
    save(b"first", delivery_config)
    path = save(b"second", delivery_config)
    assert path.read_bytes() == b"second"