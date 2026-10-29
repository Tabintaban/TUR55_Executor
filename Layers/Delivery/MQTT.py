"""Транспорт MQTT — публикация пакета TUR55 в MQTT-брокер.

Читает config["delivery"]["mqtt"]:
    broker, port, topic, qos, retain
"""

from __future__ import annotations

from typing import Any

import paho.mqtt.client as mqtt


def publish(packet_bytes: bytes, config: dict[str, Any]) -> None:
    """Опубликовать пакет в MQTT.

    Args:
        packet_bytes: bytes — пакет TUR55.
        config: dict — полный конфиг (нужна секция delivery.mqtt).
    """
    mqtt_cfg = config["delivery"]["mqtt"]
    broker = mqtt_cfg["broker"]
    port = mqtt_cfg["port"]
    topic = mqtt_cfg["topic"]
    qos = mqtt_cfg.get("qos", 1)
    retain = mqtt_cfg.get("retain", False)

    client = mqtt.Client()
    client.connect(broker, port, keepalive=60)
    client.loop_start()  # Запускаем фоновый цикл для обработки сети
    info = client.publish(topic, packet_bytes, qos=qos, retain=retain)
    info.wait_for_publish()  # ЖДЕМ, пока пакет реально уйдет в брокер
    client.loop_stop()
    client.disconnect()