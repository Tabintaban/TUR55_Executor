"""Пример шаблона: мигающая лампочка на ESP32.

Executor заменит строку-маркер (см. ниже) на `TUR55_PAYLOAD = {...}`.
Скрипт мигает `duration_sec` секунд (из `TUR55_PAYLOAD["custom_data"]`),
затем выключает LED.

Это ШАБЛОН — на реальный ESP32 он уедет только после того, как Executor
встроит данные и зашифрует пакет.
"""

# @@TUR55_PAYLOAD@@

import machine
import time


LED_PIN = 2         # GPIO2 — встроенный LED на большинстве ESP32
BLINK_PERIOD = 0.5  # секунд


def main() -> None:
    led = machine.Pin(LED_PIN, machine.Pin.OUT)

    duration = TUR55_PAYLOAD["custom_data"]["duration_sec"]
    user = TUR55_PAYLOAD["user_wallet"]
    print(f"[example_led] user={user} duration={duration}s")

    end_time = time.time() + duration
    while time.time() < end_time:
        led.value(not led.value())
        time.sleep(BLINK_PERIOD)

    led.value(0)
    print("[example_led] done")


if __name__ == "__main__":
    main()