# DECISIONS_LOG — TUR55_Executor

Журнал зафиксированных решений. Аналог `DECISIONS_LOG.md` в ESP32_Python_FUEL.

**Дата создания:** 2026-10-20
**Всего решений:** 12

---

## 1. Python 3.14.2, запуск через `py`

**Дата:** 2026-10-20
**Решение:** Целевая версия — **Python 3.14.2** (Windows, CPython). Все команды — через **`py`**, не `python`.

**Обоснование:**
- Совпадает с эталоном ESP32_Python_FUEL (там тоже 3.14.2).
- `coincurve` не собирается на 3.14 (ошибка 16 в `ERRORS_AND_SOLUTIONS.md` ESP32) → используем `embit`.
- `py` — Windows launcher, не зависит от PATH.

**Следствия:**
- `py main.py build`, `py -m pip install ...`, `py -m py_compile`, `py -m pytest`.
- README и HANDOFF фиксируют 3.14.2.

---

## 2. `embit` вместо `coincurve` для ECDSA secp256k1

**Дата:** 2026-10-20
**Решение:** Для ECDSA secp256k1 использовать **`embit`** (чистый Python), не `coincurve` (C-обёртка).

**Обоснование:**
- `coincurve` не ставится на Python 3.14 (ESP32 `ERRORS_AND_SOLUTIONS.md` #16).
- `embit` — чистый Python, работает на 3.14.
- Уже используется в `build_packet_cpython.py` (`from embit import ec, hashes`).

**Следствия:**
- Зависимость: `py -m pip install embit`.
- Никаких C-компиляторов для ECDSA.

---

## 3. Ethereum (Sepolia) первым

**Дата:** 2026-10-20
**Решение:** MVP — **Ethereum (Sepolia testnet)**. Solana / Tron — позже.

**Обоснование:**
- `web3.py` — зрелый Python-клиент Ethereum.
- Sepolia — тестнет без затрат.
- `build_packet_cpython.py` / `tur55_packet.py` уже ориентированы на Ethereum (`secp256k1`).
- Solana / Tron — другие криптографические примитивы (Ed25519 / secp256k1), отдельная работа.

**Следствия:**
- `Layers/Event/ethereum.py` — первый слушатель.
- `solana.py` / `tron.py` — заглушки (описания).
- Конфиг `configs/ethereum.json` — единый на маршрут Ethereum.

---

## 4. Транспорт: MQTT + file (оба)

**Дата:** 2026-10-20
**Решение:** Delivery Layer поддерживает **оба** транспорта: **MQTT** и **file**. Выбор — через `delivery.transport` (`mqtt` / `file` / `both`).

**Обоснование:**
- MQTT — сетевая доставка (ESP32 онлайн).
- File (`outputfiles/program.enc`) — физическая доставка (SD/USB/QR).
- ESP32 `mqtt_publisher.py` уже есть — MQTT совместим.
- `delivery.transport: "both"` по умолчанию — обе работают.

**Следствия:**
- `Layers/Delivery/MQTT.py` — `publish(packet_bytes, config)`.
- `Layers/Delivery/FILE.py` — `save(packet_bytes, config)`.
- `Layers/Executor/delivery.py` — единый `send(packet, config)`.

---

## 5. Маркер `# @@TUR55_PAYLOAD@@`

**Дата:** 2026-10-20
**Решение:** В шаблонах `inputfiles/*.py` использовать маркер **`# @@TUR55_PAYLOAD@@`** — на его место Executor встраивает `TUR55_PAYLOAD = {...}`.

**Обоснование:**
- `#` — комментарий в Python → шаблон остаётся **валидным** даже без Executor.
- `@@...@@` — уникальный паттерн, вряд ли встретится в обычном коде.
- `TUR55_PAYLOAD` — имя переменной в готовом скрипте (совпадает с HANDOFF).
- Маркер настраивается через `config["inputfiles"]["payload_marker"]`.

**Следствия:**
- `Layers/Executor/script_template.py::build_script` — проверка «маркер ровно один».
- `inputfiles/example_led.py` — тестовый шаблон с маркером.
- Реальные `led_control.py` / `unlock.py` / `sensor_read.py` — позже.

---

## 6. `metadata` ≠ `custom_data`

**Дата:** 2026-10-20
**Решение:** В событии `ExecutorTriggered` — **два разных поля**:
- **`metadata`** — служебное (nonce, source, event_index).
- **`custom_data`** — прикладное (duration_sec и т.п.).

**Обоснование:**
- `metadata` — «паспорт события» (для логов Executor).
- `custom_data` — данные для скрипта ESP32 (сколько мигать, что открывать).
- Смешивание в одно поле — каша.

**Следствия:**
- `Layers/Event/ethereum.py::_listen_mock` — генерирует оба поля.
- `configs/ethereum.example.json::event.mock.custom_data` — `{"duration_sec": 120}`.
- `inputfiles/README.md` — перечисляет `custom_data` в списке встраиваемых данных.

---

## 7. `device_id` в `executor`, не в `delivery`

**Дата:** 2026-10-20
**Решение:** `device_id` (например, `esp32_001`) хранится в **`executor.device_id`**, не в `delivery`.

**Обоснование:**
- `device_id` используется **и в Event** (поле события `device_id`), **и в Delivery** (адресат, топик MQTT).
- Один источник — `executor.device_id` — читается обоими слоями.
- `delivery.mqtt.topic` на MVP — **явный** `tur55/device/esp32_001` (без плейсхолдера). Когда понадобится шаблон `{device_id}` — научим `MQTT.py` подставлять `executor.device_id`.

**Следствия:**
- `configs/ethereum.example.json::executor.device_id` — `"esp32_001"`.
- `configs/ethereum.example.json::delivery.mqtt.topic` — `"tur55/device/esp32_001"` (явно).
- Никакого дублирования `device_id` в двух местах.

---

## 8. `configs/ethereum.json` — один конфиг на маршрут

**Дата:** 2026-10-20
**Решение:** Один конфиг **`configs/ethereum.json`** настраивает **весь маршрут** (Event → Executor → Delivery) для Ethereum. Имя файла конфига **должно совпадать** с `event.blockchain`.

**Обоснование:**
- «Шампур»: `main.py` читает конфиг, вызывает нужные слои.
- `delivery.transport` — переключение MQTT / file / both.
- `inputfiles.template` — какой шаблон использовать.
- Если файл `ethereum.json`, а `event.blockchain: "solana"` — ошибка (защита от опечаток). Аналогично для `solana.json`.
- Замена `settings.json` → `ethereum.json` (коммит `526528a`).

**Следствия:**
- `configs/ethereum.example.json` — шаблон.
- `configs/ethereum.json` — локальный, в `.gitignore`.
- `main.py::load_config` — проверка `path.name.split(".")[0] == config["event"]["blockchain"]`.
- `.gitignore` — `configs/ethereum.json` (заменено с `configs/settings.json`).

---

## 9. Ключи в `keys/` (не в git)

**Дата:** 2026-10-21
**Решение:** Ключи хранятся в `keys/` (в `.gitignore`):
- `keys/esp32_public_key.pem` — публичный RSA ESP32 (для шифрования).
- `keys/executor_private_key.bin` — приватный secp256k1 Executor (для подписи, raw 32 байта).
- `keys/executor_pubkey.bin` — публичный secp256k1 Executor (raw 33 байта).

**Обоснование:**
- Секреты **не** в git.
- Формат: RSA — PEM (стандарт), secp256k1 — raw (embit).
- Скрипты в `scripts/`: `export_esp32_pubkey.py` (извлечение из `esp32_private_key.json`), `generate_executor_key.py` (генерация).

**Следствия:**
- `PacketBuilder` читает ключи из `keys/`.
- При смене ключей — перегенерировать.

---

## 10. `inputfiles/` = JSON (не `.py`)

**Дата:** 2026-10-21
**Решение:** `inputfiles/*.json` — программы для ESP32 в формате TUR55 3.2:
```json
{
  "setup": ["led = machine.Pin(2, machine.Pin.OUT)"],
  "loop_logic": ["led.value(1)", "time.sleep(0.5)"],
  "custom_data": {"duration_sec": 120}
}
```

**Обоснование:**
- ESP32 (`execution_engine`) исполняет `setup`/`loop_logic` — списки строк.
- `.py`-файлы **не** принимаются ESP32.
- `example_led.py` — оставлен как **пример** (человекочитаемый), но **не используется**.

**Следствия:**
- `configs/ethereum.json::inputfiles.template` = `inputfiles/example_led.json`.
- `.py` → `.json` конвертер — **позже** (сложно, хрупко).

---

## 11. Delivery — единый интерфейс (`delivery.py`)

**Дата:** 2026-10-21
**Решение:** Транспорты (`FILE.py`, `MQTT.py`) — отдельные модули. `Layers/Executor/delivery.py::send(packet, config)` — диспетчер по `config["delivery"]["transport"]`:
- `"file"` → только `FILE.py`.
- `"mqtt"` → только `MQTT.py`.
- `"both"` → оба.

**Обоснование:**
- `main.py::cmd_build` не знает деталей транспорта.
- Единый интерфейс для `cmd_build` и `cmd_send`.
- Легко добавить `BLE` / `QR` / `NFC`.

**Следствия:**
- `Layers/Delivery/FILE.py::save()` — `outputfiles/program.enc`.
- `Layers/Delivery/MQTT.py::publish()` — `paho-mqtt`.
- `cmd_build` → `send(packet, config)`.

---

## 12. Тесты (`test/`) — 17 passed

**Дата:** 2026-10-21
**Решение:** Все тесты — в `test/`. 17 тестов:
- `test_event_mock.py` (3) — детерминизм, поля.
- `test_packet_roundtrip.py` (5) — magic, версия, ключ, размер.
- `test_script_template.py` (5) — позитив/негатив.
- `test_delivery_file.py` (4) — сохранение в файл.

**Обоснование:**
- Регрессионный барьер перед приёмкой.
- `pytest` — стандарт.

**Следствия:**
- `py -m pytest test/ -v` — 17 passed.
- `test/conftest.py` — фикстуры (`keys_dir`, `program_led`, `sample_event`, `mock_config`).

---

## 13. `max_iterations` в пакете (`execution.max_iterations`)

**Дата:** 2026-10-21
**Решение:** `PacketBuilder` добавляет `max_iterations` в `execution.max_iterations` пакета. Вычисляется из `custom_data.duration_sec` (× 2, т.к. `loop_logic` в `example_led.json` = 1 сек/итерацию).

**Обоснование:**
- ESP32 `main.main()` жёстко передаёт `max_iterations=5` (до приёмки).
- Без `max_iterations` в пакете — **лампочка мигает 5 сек** (не 120).
- С `max_iterations` (из пакета) — ESP32 читает `execution.max_iterations` → 240 итераций → **~240 сек**.

**Следствия:**
- `Layers/Executor/packet_builder.py` — добавлено поле.
- `ESP32_Python_FUEL/main.py` — читает `execution.max_iterations` (правка `8f2639a`).
- **Приёмка 21.10.2026:** `max_iterations=240`, `loop iterations: 240`, **лампочка мигала ~4 минуты и выключилась**.

---

## Ссылки

- **TUR55 Standard:** https://github.com/Tabintaban/Protocol_TUR55
- **ESP32_Python_FUEL** (Layer 4, `DECISIONS_LOG.md` — 26 решений): https://github.com/Tabintaban/ESP32_Python_FUEL
- **TUR55_Executor:** https://github.com/Tabintaban/TUR55_Executor

