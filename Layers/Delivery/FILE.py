"""Транспорт FILE — сохранение пакета TUR55 в файл.

Используется в Delivery Layer.
Читает config["delivery"]["file"]:
    output_dir — папка (например, "outputfiles/")
    filename   — имя файла (например, "program.enc")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def save(packet_bytes: bytes, config: dict[str, Any]) -> Path:
    """Сохранить пакет в файл.

    Args:
        packet_bytes: bytes — пакет TUR55.
        config: dict — полный конфиг (нужна секция delivery.file).

    Returns:
        Path — путь к сохранённому файлу.
    """
    file_cfg = config["delivery"]["file"]
    output_dir = Path(file_cfg["output_dir"])
    filename = file_cfg["filename"]

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    output_path.write_bytes(packet_bytes)

    return output_path