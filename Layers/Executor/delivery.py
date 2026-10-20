"""Диспетчер доставки — выбор транспорта по config["delivery"]["transport"].

Значения:
    "file"  — только Layers/Delivery/FILE.py
    "mqtt"  — только Layers/Delivery/MQTT.py
    "both"  — оба
"""

from __future__ import annotations

from typing import Any


def send(packet_bytes: bytes, config: dict[str, Any]) -> list[str]:
    """Отправить пакет через транспорт(ы), выбранные в config.

    Args:
        packet_bytes: bytes — пакет TUR55.
        config: dict — полный конфиг.

    Returns:
        list[str] — список успешно выполненных транспортов (["file"], ["mqtt"], ["file", "mqtt"]).
    """
    transport = config["delivery"].get("transport", "file")
    done: list[str] = []

    if transport in ("file", "both"):
        from Layers.Delivery.FILE import save
        path = save(packet_bytes, config)
        print(f"[delivery:file] saved {len(packet_bytes)} bytes → {path}")
        done.append("file")

    if transport in ("mqtt", "both"):
        from Layers.Delivery.MQTT import publish
        publish(packet_bytes, config)
        print(f"[delivery:mqtt] published {len(packet_bytes)} bytes")
        done.append("mqtt")

    if not done:
        raise ValueError(f"Unknown transport: {transport!r} (expected: file / mqtt / both)")

    return done