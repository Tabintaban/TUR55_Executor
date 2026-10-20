# HANDOFF — TUR55_Executor

**Дата:** 2026-10-20 (обновлено после сессии 19.10.2026)
**Цель:** передать контекст новому диалогу/ассистенту для продолжения работы.

---

## Что такое TUR55_Executor

**TUR55_Executor** — реализация **Layer 2 (Executor Layer)** стандарта **TUR55**.

**Стандарт:** https://github.com/Tabintaban/Protocol_TUR55
**Автор стандарта:** NOMOS-H, зафиксирован 2026-04-10.

**Репозиторий:** https://github.com/Tabintaban/TUR55_Executor
**Локально:** `C:\Users\user\Documents\Projects\TUR55_Executor`

### Задача Executor

Executor — **сервер** (Python 3.14, CPython, запуск `py`), который:

1. **Слушает** блокчейн (MVP: Ethereum / Sepolia; позже — Solana / Tron)
2. **Извлекает** событие `ExecutorTriggered(user_wallet, amount, expires, device_id, metadata, custom_data)`
3. **Формирует** JSON-конверт TUR55 (раздел 3.2)
4. **Встраивает** данные в Python-скрипт (раздел 3.3) — маркер `# @@TUR55_PAYLOAD@@`
5. **Шифрует** (TODO): сессионный ключ → RSA-OAEP (публичный ключ ESP32); скрипт → AES-256-GCM
6. **Подписывает** (TODO): ECDSA secp256k1 (`embit`, не `coincurve` — см. ошибка 16 в ESP32)
7. **Собирает** пакет TUR55 (раздел 3.4)
8. **Отправляет** через **Delivery Layer** (MVP: MQTT + file; далее — BLE / LoRaWAN / QR / NFC / SD / USB)

### Связанный проект

**ESP32_Python_FUEL** — реализация **Layer 4 (Execution Layer)**.
- Репозиторий: https://github.com/Tabintaban/ESP32_Python_FUEL
- **Статус:** ~95% TUR55/Bronze, Bronze закрыт.
- **eFuse, Secure boot** — Gold уровень.

**Документы ESP32 (для контекста):**
- `PROJECT_HISTORY.md` — 12 сессий
- `TUR55_COMPLIANCE.md` — ~95% Bronze закрыт
- `TODO.md` — план
- `DECISIONS_LOG.md` — 26 решений
- `ERRORS_AND_SOLUTIONS.md` — 28 ошибок
- `CHANGELOG.md` — v3.3.0

---

## Что уже сделано в TUR55_Executor

### Структура (git)
```
TUR55_Executor/
├── Layers/
│ ├── __init__.py
│ ├── Event/
│ │ ├── __init__.py
│ │ ├── ethereum.py ← слушатель Ethereum (мок + каркас web3.py)
│ │ ├── solana.py ← описание (позже)
│ │ └── tron.py ← описание (позже)
│ ├── Delivery/
│ │ ├── __init__.py
│ │ ├── MQTT.py ← описание
│ │ ├── HTTP_HTTPS.py ← описание
│ │ ├── Bluetooth_BLE.py ← описание
│ │ ├── LoraWAN.py ← описание
│ │ ├── QR-code_NFC.py ← описание
│ │ └── SD_USB.py ← описание
│ └── Executor/
│ ├── __init__.py
│ ├── tur55_packet.py ← формат пакета TUR55 (из ESP32)
│ ├── build_packet_cpython.py ← сборка пакета (из ESP32)
│ └── script_template.py ← встраивание payload в шаблон
├── configs/
│ ├── README.md
│ └── ethereum.example.json ← шаблон (ethereum.json — в .gitignore)
├── inputfiles/
│ ├── README.md
│ └── example_led.py ← тестовый шаблон (мигающая лампочка)
├── outputfiles/
│ └── README.md
├── test/
│ └── README.md ← все тесты только здесь
├── .gitignore
├── main.py ← CLI (build / send / listen)
├── README.md
└── README_RU.md
```


### Что работает

| Команда | Что делает | Статус |
|---|---|---|
| `py main.py listen` | Слушает Ethereum (мок) → JSONL-события | ✅ |
| `py main.py build` | Одно событие + шаблон → готовый Python-скрипт с `TUR55_PAYLOAD` | ✅ |
| `py main.py send` | Доставка через Delivery | ❌ (каркас, NotImplementedError) |

**Что уже реализовано:**
- **`Layers/Event/ethereum.py`** — `listen(config, verbose)`:
  - `_listen_mock` — детерминированный мок (seed, max_events, interval_sec), поля события: `user_wallet`, `amount`, `expires`, `device_id`, `metadata` (служебное), `custom_data` (прикладное)
  - `_listen_web3` — каркас для реального Ethereum (TODO: ABI, контракт, event_filter)
- **`Layers/Executor/script_template.py`** — `build_script(template_text, payload, marker)`:
  - проверка: маркер **ровно один**
  - замена на `TUR55_PAYLOAD = {...}` (компактный JSON)
  - проверка: результат — **валидный Python** (`compile`)
- **`main.py`** — `cmd_listen` (JSONL) и `cmd_build` (event + template + `build_script` + печать)
- **`configs/ethereum.example.json`** — единый конфиг маршрута Ethereum
- **`.gitignore`** — `keys/`, `logs/`, `configs/ethereum.json`, `*.pem`, `*.key`, `outputfiles/*.enc`, `inputfiles/*.enc`

### Коммиты (9, все запушены в `origin/main`)
44fc44d main.py: cmd_build -> event + script_template + печать; configs: inputfiles.template -> example_led.py
5acfeaa Layers/Executor: script_template.py (build_script); inputfiles/example_led.py (тестовый шаблон)
46f0433 event: добавить custom_data в мок-событие + секция event.mock в ethereum.example.json
d584010 main.py: cmd_listen -> Layers.Event.ethereum + JSONL
9c2529f Layers: init; Layers/Event/ethereum.py: мок + каркас web3.py
79ad226 gitignore: configs/settings.json -> configs/ethereum.json; main.py: DEFAULT_CONFIG и EXAMPLE_CONFIG -> ethereum.*
526528a configs: settings.* -> ethereum.*; main.py: проверка имени файла и event.blockchain
4b48227 main.py: CLI-каркас (build / send / listen)
6dbb954 README: описание проекта, схема слоёв, быстрый старт, ссылки


**История до 20.10.2026:** структура проекта + перенос `tur55_packet.py` / `build_packet_cpython.py` из ESP32 + `configs/` + `README.md`.

---

## Что осталось до MVP (на 2026-10-20)

### 1. Шаг 6 — сборка пакета TUR55 (шифрование + подпись)

**Не начато.** Открытый вопрос: **что шифруется в пакете TUR55 (3.4)?**

- **(а)** JSON-конверт (3.2), а готовый скрипт — отдельно.
- **(б)** Готовый Python-скрипт (с payload) — ESP32 расшифровывает и **исполняет**.
- **(в)** Оба в одном пакете (JSON + скрипт).

**По HANDOFF 3.3 — (б).** Но `build_packet_cpython.py::build_packet(json_data, ...)` сейчас реализует **(а)**.

**Что нужно, чтобы решить:**
- Полный `build_packet` (тело) — что именно шифрует (json_data? скрипт?).
- `main()` в `build_packet_cpython.py` — пример использования.
- `tur55_packet.py` — интерфейс `parse_packet` (что распаковывает).
- `parse_packet` на ESP32 — что делает после расшифровки.

**После ответа:**
- Подключить `build_packet` в `cmd_build` (после `build_script`).
- Проверить, что `parse_packet` из `tur55_packet.py` принимает результат.
- Ключи: `keys/esp32_public_key.pem` (RSA pub) + `keys/executor_private_key.pem` (ECDSA priv). Локально должны быть — проверить.

### 2. Шаг 7 — Delivery Layer (MQTT + file)

**Не начато.** В `configs/ethereum.json` уже есть:
```json
"delivery": {
  "transport": "both",
  "mqtt": { "broker": "broker.hivemq.com", "port": 1883, "topic": "tur55/device/esp32_001", "qos": 1, "retain": false },
  "file": { "output_dir": "outputfiles/", "filename": "program.enc" }
}
```
### Что нужно

`Layers/Delivery/MQTT.py — publish(packet_bytes, config)` → через `paho-mqtt`

`Layers/Delivery/file.py — save(packet_bytes, config)` → в `outputfiles/program.enc`

`Layers/Executor/delivery.py` — единый интерфейс: `send(packet, config)` → выбирает транспорт по `delivery.transport (mqtt / file / both)`

В `main.py` `cmd_send` — вызвать `send`

Зависимость: `py -m pip install paho-mqtt`

### 3. Шаг 8 — тесты (test/)
Не начато. Правило: все тесты только в `test/`.

Минимум:

`test_packet_roundtrip.py` — `build_packet` → `parse_packet` → все поля совпадают.

`test_script_template.py` — позитив (маркер заменён) + негатив (нет маркера / два маркера / невалидный Python).

`test_event_mock.py` — детерминизм `_listen_mock` (`user_wallet, amount, metadata, custom_data` — стабильны).

`test_delivery_file.py` — пакет сохраняется в `outputfiles/.`

Запуск: `py -m pytest test/`.

### 4. Шаг 9 — документация
В работе (сессия 20.10.2026).

✅ HANDOFF.md — обновляется.

✅ README.md — обновляется (build уже работает).

⏳ DECISIONS_LOG.md — создать (8–9 решений).

### 5. Шаг 10 — приёмка (end-to-end)
Не начато.

`py main.py build` → пакет `TUR55` (байты).

`py main.py send` → доставка (`MQTT / file`).

ESP32 принимает пакет, расшифровывает, запускает скрипт «мигающая лампочка на 120 секунд».

Критерий MVP: ESP32 мигает 2 минуты и выключается после события контракта.

## Архитектура (обновлено 20.10.2026)
```
Блокчейн (Ethereum / Sepolia)
│ событие ExecutorTriggered
▼
Layers/Event/ethereum.py ← слушатель
│ dict: user_wallet, amount, expires, device_id, metadata, custom_data
▼
Layers/Executor/script_template.py ← встраивает payload в шаблон
│ готовый Python-скрипт (TUR55_PAYLOAD + логика ESP32)
▼
Layers/Executor/build_packet_cpython.py ← шифрование + подпись (TODO, шаг 6)
│ пакет TUR55 (раздел 3.4)
▼
Layers/Executor/delivery.py ← единый интерфейс доставки (TODO, шаг 7)
│
├── Layers/Delivery/MQTT.py (TODO)
└── Layers/Delivery/file.py (TODO)
▼
ESP32 (Layer 4, ESP32_Python_FUEL
```

**Ключевое:**
- Один конфиг — `configs/ethereum.json` — настраивает **весь маршрут** (Event → Executor → Delivery).
- Имя файла конфига **должно совпадать** с `event.blockchain` (`ethereum.json` ↔ `blockchain: "ethereum"`).
- `main.py` — «шампур»: читает конфиг, вызывает нужные слои.
- **MVP:** Ethereum + мок; Solana / Tron — позже.
- **Delivery:** MQTT + file (оба, выбор через `delivery.transport`).

---

## Схема `configs/ethereum.example.json`

```json
{
  "executor": {
    "name": "TUR55_Executor",
    "version": "0.1.0",
    "device_id": "esp32_001"
  },
  "event": {
    "blockchain": "ethereum",
    "rpc_url": "https://sepolia.infura.io/v3/YOUR_KEY",
    "contract_address": "0x0000000000000000000000000000000000000000",
    "event_name": "ExecutorTriggered",
    "poll_interval_sec": 5,
    "use_mock": true,
    "mock": {
      "max_events": 3,
      "interval_sec": 0.0,
      "seed": 0,
      "custom_data": { "duration_sec": 120 }
    }
  },
  "delivery": {
    "transport": "both",
    "mqtt": { "broker": "broker.hivemq.com", "port": 1883, "topic": "tur55/device/esp32_001", "qos": 1, "retain": false },
    "file": { "output_dir": "outputfiles/", "filename": "program.enc" }
  },
  "keys": {
    "esp32_public_key": "keys/esp32_public_key.pem",
    "executor_private_key": "keys/executor_private_key.pem"
  },
  "inputfiles": {
    "template": "inputfiles/example_led.py",
    "payload_marker": "# @@TUR55_PAYLOAD@@"
  },
  "logging": { "level": "INFO", "file": "logs/executor.log" }
}
```

## Зафиксированные решения (8)

| # | Решение | Обоснование |
|---|---|---|
| 1 | **Python 3.14.2**, запуск через **`py`** | Совпадает с ESP32; `coincurve` не ставится на 3.14 (ошибка 16 в ESP32) |
| 2 | **`embit`** вместо `coincurve` | Чистый Python, работает на 3.14 |
| 3 | **Ethereum (Sepolia)** первым | Зрелый `web3.py`, тестнет без затрат; Solana / Tron — позже |
| 4 | **Транспорт: MQTT + file** (`delivery.transport`) | Оба нужны: MQTT для сети, file для физической доставки (SD/USB/QR) |
| 5 | Маркер **`# @@TUR55_PAYLOAD@@`** | Уникальный, шаблон остаётся валидным Python даже без Executor |
| 6 | **`metadata` ≠ `custom_data`** | `metadata` — служебное (nonce, source, event_index); `custom_data` — прикладное (duration_sec) |
| 7 | **`device_id`** в `executor` (не `delivery`) | Используется и Event (поле события), и Delivery (адресат) |
| 8 | **`configs/ethereum.json`** — один конфиг на маршрут | Единая настройка Event → Delivery; имя файла = `event.blockchain` |

---

## Уроки среды (7)

| # | Урок |
|---|---|
| 1 | **`git add` с несуществующим путём** — падает целиком. Проверять `N files changed` в коммите. |
| 2 | **`py main.py build > file.py`** в PowerShell ненадёжно (UTF-16 LE → null bytes). Использовать `Set-Content -Encoding UTF8` или Python `Path.write_text(encoding='utf-8')`. |
| 3 | **`py -c '...'`** в PowerShell не передаёт двойные кавычки. Использовать двойные снаружи + одинарные Python внутри. |
| 4 | **`.Split('# ...')`** в PowerShell — по символам. Для подстроки — `-split [regex]::Escape('...')`. |
| 5 | **Heredoc `@'...'@`** через копипаст ломается. Надёжнее — VS Code или массив строк. |
| 6 | **`git diff`** открывает `less` — использовать `git --no-pager diff`. |
| 7 | **`Measure-Object -Line`** считает непустые строки; `(Get-Content file).Count` — все. Для сравнения использовать `.Count`. |

---


## Открытый вопрос (один, блокирует шаг 6)

**Что шифруется в пакете TUR55 (раздел 3.4)?**

- **(а)** JSON-конверт (3.2), а готовый скрипт — отдельно (или уже на ESP32).
- **(б)** Готовый Python-скрипт (с payload) — ESP32 расшифровывает и **исполняет**.
- **(в)** Оба в одном пакете (JSON + скрипт в разных полях).

**По HANDOFF 3.3 — (б).** Но `build_packet_cpython.py::build_packet(json_data, ...)` сейчас реализует **(а)**.

**Что нужно, чтобы решить:**
1. Полный `build_packet` (тело, что именно шифрует: `json_data`? скрипт? оба?).
2. `main()` в `build_packet_cpython.py` — пример использования.
3. `tur55_packet.py` — интерфейс `parse_packet` (что распаковывает).
4. `parse_packet` на ESP32 — что делает после расшифровки (исполняет скрипт? читает JSON?).

**Все ранее открытые вопросы закрыты:**
- Блокчейн первым: **Ethereum (Sepolia)**.
- Транспорт по умолчанию: **оба** (`mqtt` + `file`, выбор через `delivery.transport`).
- Шаблоны в `inputfiles/`: **`led_control.py`, `unlock.py`, `sensor_read.py`** (реальные — позже) + **`example_led.py`** (тестовый, уже есть).

---

## Правила работы (для нового ассистента)
### Стиль
Пошагово — не забегать вперёд.

Всегда показывай что найти и что заменить (для правок).

Всегда — `git status` перед `git add`.

Всегда — `py_compile` перед запуском.

Не сокращай структуру и комментарии.

Не гадай — если не знаешь, спроси или скинь документ.

### Среда
`Windows PowerShell: C:\Users\user\Documents\Projects\`

`WSL:` сборка прошивки ESP32 (не для Executor).

`ESP32: MicroPico / miniterm` (для тестов Layer 4).

`Git`
Перед коммитом: `git status` → `git add -A` → `git status` → `git commit`.

Сообщения: на русском, кратко, по делу.

`Push:` после каждого коммита.

### Документация
Стиль: Markdown, таблицы, разделы.

Комментарии — не сокращать.

Структура — полная (все файлы, вложенные папки).

Ключевые документы ESP32 (для контекста)
Если нужен контекст по TUR55 / криптографии / ESP32:

`PROJECT_HISTORY.md` — 12 сессий (полная хронология)

`TUR55_COMPLIANCE.md` — таблица соответствия (~95%)

`DECISIONS_LOG.md` — 26 решений (почему так)

`ERRORS_AND_SOLUTIONS.md` — 28 ошибок (как решали)

`BUILD_GCM_FIRMWARE.md` — сборка прошивки

`FIRMWARE_WITH_UCRYPTOGRAPHY.md` — модули прошивки

`Ссылка: https://github.com/Tabintaban/ESP32_Python_FUEL`

## Следующий шаг (после 20.10.2026)

**Закрыть документацию** (эта сессия):
- `HANDOFF.md` — обновляется (в работе)
- `README.md` — обновить раздел «Статус» и «Быстрый старт» (build уже работает)
- `DECISIONS_LOG.md` — создать (8–9 решений)

**Затем — шаг 6 (сборка пакета TUR55):**
1. Ответить на **открытый вопрос**: JSON / скрипт / оба.
2. Прислать полный `build_packet`, `main()`, `tur55_packet.py::parse_packet`.
3. Подключить `build_packet` в `cmd_build`.
4. Проверить `parse_packet` на результат.
5. Коммит.

**После — шаги 7–10:** Delivery (MQTT + file), тесты, приёмка.

---

## Ссылки

`TUR55 Standard: https://github.com/Tabintaban/Protocol_TUR55`

`ESP32_Python_FUEL: https://github.com/Tabintaban/ESP32_Python_FUEL`

`TUR55_Executor: https://github.com/Tabintaban/TUR55_Executor`

`NIST SP 800-38D: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf`

`embit (CPython ECDSA): https://github.com/diybitcoinhardware/embit`

`paho-mqtt: https://github.com/eclipse-paho/paho.mqtt.python`

