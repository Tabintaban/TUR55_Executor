# HANDOFF — TUR55_Executor

**Дата:** 2026-10-21 (сессия приёмки MVP, обновлено после приёмки ESP32)
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
4. **Собирает** пакет: `execution.setup` / `execution.loop_logic` + данные события
5. **Шифрует**: сессионный ключ → RSA-OAEP (публичный ключ ESP32); JSON → AES-256-GCM
6. **Подписывает**: ECDSA secp256k1 (`embit`, не `coincurve` — см. ошибка 16 в ESP32)
7. **Собирает** пакет TUR55 (раздел 3.4)
8. **Отправляет** через **Delivery Layer** (MVP: MQTT + file; далее BLE / LoRaWAN / QR / NFC / SD / USB)

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
│   ├── __init__.py
│   ├── Event/
│   │   ├── __init__.py
│   │   ├── ethereum.py         ← слушатель Ethereum (мок + каркас web3.py)
│   │   ├── solana.py           ← описание (позже)
│   │   └── tron.py             ← описание (позже)
│   ├── Delivery/
│   │   ├── __init__.py
│   │   ├── FILE.py             ← транспорт file (save)
│   │   ├── MQTT.py             ← транспорт MQTT (publish)
│   │   ├── HTTP_HTTPS.py       ← описание
│   │   ├── Bluetooth_BLE.py    ← описание
│   │   ├── LoraWAN.py          ← описание
│   │   ├── QR-code_NFC.py      ← описание
│   │   └── SD_USB.py           ← описание
│   └── Executor/
│       ├── __init__.py
│       ├── tur55_packet.py           ← формат пакета TUR55 (parse)
│       ├── build_packet_cpython.py   ← сборка пакета (build)
│       ├── packet_builder.py         ← сборка из события + программы
│       ├── delivery.py               ← диспетчер доставки
│       └── script_template.py        ← встраивание payload в шаблон (не используется)
├── configs/
│   ├── README.md
│   └── ethereum.example.json   ← шаблон (ethereum.json — в .gitignore)
├── inputfiles/
│   ├── README.md
│   └── example_led.json        ← программа для ESP32 (setup/loop_logic/custom_data)
├── outputfiles/
│   ├── README.md
│   └── program.enc             ← результат `py main.py build`
├── keys/                       ← .gitignore (3 файла: esp32_public_key.pem, executor_private_key.bin, executor_pubkey.bin)
├── logs/                       ← .gitignore
├── scripts/
│   ├── export_esp32_pubkey.py
│   └── generate_executor_key.py
├── test/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_event_mock.py
│   ├── test_packet_roundtrip.py
│   ├── test_script_template.py
│   └── test_delivery_file.py
├── .gitignore
├── main.py                     ← CLI (build / send / listen)
├── README.md
└── README_RU.md
```

### Что работает (MVP принят 21.10.2026)

| Команда | Что делает | Статус |
|---|---|---|
| `py main.py listen` | Слушает Ethereum (мок) → JSONL | ✅ |
| `py main.py build` | Событие + программа → пакет TUR55 → `outputfiles/program.enc` | ✅ |
| `py main.py send` | (TODO) Доставка через Delivery | ⏳ |

**End-to-end (приёмка пройдена 21.10.2026):**
- Executor собрал пакет (988 байт) → ESP32 получил → расшифровал → проверил подпись → исполнил.
- **Результат:** `max_iterations=240` (из `custom_data.duration_sec: 120`), `loop iterations: 240`, **лампочка мигала ~4 минуты и выключилась**.

**Реализовано:**
- `Layers/Event/ethereum.py` — `listen()` (мок + каркас web3.py)
- `Layers/Executor/script_template.py` — `build_script()` (для модели B, не используется)
- `Layers/Executor/packet_builder.py` — `PacketBuilder.build_from_event()`, **`max_iterations` из `custom_data.duration_sec`**
- `Layers/Delivery/FILE.py` — `save()` (сохранение в файл)
- `Layers/Delivery/MQTT.py` — `publish()` (MQTT)
- `Layers/Executor/delivery.py` — `send()` (диспетчер по `transport`)
- `scripts/generate_executor_key.py` — генерация secp256k1 ключей
- `scripts/export_esp32_pubkey.py` — извлечение RSA public из ESP32 private

**Тесты:** 17 passed (`py -m pytest test/ -v`):
- `test_event_mock.py` (3)
- `test_packet_roundtrip.py` (5)
- `test_script_template.py` (5)
- `test_delivery_file.py` (4)

### Коммиты (15, все запушены в `origin/main`)

```
0293aa7 packet_builder: max_iterations из custom_data.duration_sec
0768c5c docs: HANDOFF (этапы 1–8), README (статус), DECISIONS_LOG (+4), inputfiles (JSON)
93f9fdb test: 17 тестов (event mock, packet, script template, delivery file)
3373fd8 Delivery: FILE.py + MQTT.py + delivery.py; main.py: cmd_build -> delivery.send; configs: transport=file
fc1bbd3 main.py: cmd_build -> PacketBuilder (пакет в outputfiles/program.enc); configs: inputfiles.template -> example_led.json
248129a Layers/Executor: packet_builder.py + inputfiles/example_led.json + test/test_packet.py
48441c1 scripts: ключи (export ESP32 pub, generate Executor key) + keys/ в .gitignore
481c1ca docs: DECISIONS_LOG.md — 8 зафиксированных решений
d3f0156 README: статус (listen/build работают, send — шаг 7) + быстрый старт
04a51b5 docs: HANDOFF.md — состояние на 20.10.2026, архитектура, решения, уроки, открытый вопрос шага 6
44fc44d main.py: cmd_build -> event + script_template + печать; configs: inputfiles.template -> example_led.py
5acfeaa Layers/Executor: script_template.py (build_script); inputfiles/example_led.py (тестовый шаблон)
46f0433 event: добавить custom_data в мок-событие + секция event.mock в ethereum.example.json
d584010 main.py: cmd_listen -> Layers.Event.ethereum + JSONL
9c2529f Layers: __init__; Layers/Event/ethereum.py: мок + каркас web3.py
```

---

## Что осталось до MVP (на 2026-10-21)

### 1. Шаг 10 — приёмка (end-to-end)

`py main.py build` → пакет TUR55 (байты) → `outputfiles/program.enc`.

**Варианты доставки:**
- **FILE:** скопировать `outputfiles/program.enc` на ESP32 (MicroPico / mpremote).
- **MQTT:** `transport: "mqtt"` (или `"both"`) → пакет публикуется в `broker.hivemq.com` → ESP32 подписан на топик.

ESP32: `parse_packet` → JSON → `exec(setup)` + `exec(loop_logic)` → **лампочка мигает 2 минуты**.

**Критерий MVP:** ESP32 мигает 2 минуты и выключается после события контракта.

**Проверить:**
- `keys/executor_pubkey.bin` на ESP32 **совпадает** с нашим.
- `esp32_private_key.json` на ESP32 **совпадает** с тем, из которого извлечён `esp32_public_key.pem`.

### 2. Документация (обновляется в сессии 21.10.2026)

- ✅ `HANDOFF.md` — этот файл.
- ⏳ `README.md` — обновить «Статус» (Delivery работает, 17 тестов).
- ⏳ `DECISIONS_LOG.md` — добавить решения 9–12.
- ⏳ `inputfiles/README.md` — переписать: «JSON, не `.py`».

---

## Архитектура (обновлено 21.10.2026)

```
Блокчейн (Ethereum / Sepolia)
    │  событие ExecutorTriggered
    ▼
Layers/Event/ethereum.py                ← слушатель
    │  dict: user_wallet, amount, expires, device_id, metadata, custom_data
    ▼
Layers/Executor/packet_builder.py       ← PacketBuilder
    │  + inputfiles/example_led.json (setup/loop_logic)
    ▼
Layers/Executor/build_packet_cpython.py ← build_packet (RSA-OAEP + AES-GCM + ECDSA)
    │  пакет TUR55 (байты)
    ▼
Layers/Executor/delivery.py             ← send (диспетчер)
    │
    ├── Layers/Delivery/FILE.py         ← save → outputfiles/program.enc
    └── Layers/Delivery/MQTT.py         ← publish → broker.hivemq.com
    ▼
ESP32 (Layer 4)
    parse_packet → JSON → exec(setup) + exec(loop_logic)
```

**Ключевое:**
- Один конфиг — `configs/ethereum.json` — настраивает **весь маршрут** (Event → Executor → Delivery).
- Имя файла конфига **должно совпадать** с `event.blockchain`.
- `main.py` — «шампур»: читает конфиг, вызывает нужные слои.
- **MVP:** Ethereum + мок; Solana / Tron — позже.
- **Delivery:** MQTT + FILE (оба, выбор через `delivery.transport`).

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
    "transport": "file",
    "mqtt": { "broker": "broker.hivemq.com", "port": 1883, "topic": "tur55/device/esp32_001", "qos": 1, "retain": false },
    "file": { "output_dir": "outputfiles/", "filename": "program.enc" }
  },
  "keys": {
    "esp32_public_key": "keys/esp32_public_key.pem",
    "executor_private_key": "keys/executor_private_key.pem"
  },
  "inputfiles": {
    "template": "inputfiles/example_led.json"
  },
  "logging": { "level": "INFO", "file": "logs/executor.log" }
}
```

**Примечание:** `keys` секция — legacy, `PacketBuilder` читает ключи напрямую из `keys/`. Не критично.

## Зафиксированные решения (8)

| # | Решение | Обоснование |
|---|---|---|
| 1 | **Python 3.14.2**, запуск через **`py`** | Совпадает с ESP32; `coincurve` не ставится на 3.14 (ошибка 16 в ESP32) |
| 2 | **`embit`** вместо `coincurve` | Чистый Python, работает на 3.14 |
| 3 | **Ethereum (Sepolia)** первым | Зрелый `web3.py`, тестнет без затрат; Solana / Tron — позже |
| 4 | **Транспорт: MQTT + file** (`delivery.transport`) | Оба нужны: MQTT для сети, file для физической доставки (SD/USB/QR) |
| 5 | Маркер **`# @@TUR55_PAYLOAD@@`** | Уникальный, шаблон остаётся валидным Python даже без Executor |
| 6 | **`metadata` ≠ `custom_data`** | `metadata` — служебное; `custom_data` — прикладное |
| 7 | **`device_id`** в `executor` (не `delivery`) | Используется и Event (поле события), и Delivery (адресат) |
| 8 | **`configs/ethereum.json`** — один конфиг на маршрут | Единая настройка Event → Delivery; имя файла = `event.blockchain` |

---

## Уроки среды (7)

| # | Урок |
|---|---|
| 1 | **`git add` с несуществующим путём** — падает целиком. Проверять `N files changed`. |
| 2 | **`py main.py build > file.py`** в PowerShell ненадёжно (UTF-16 LE → null bytes). Использовать `Set-Content -Encoding UTF8` или Python `Path.write_text(encoding="utf-8")`. |
| 3 | **`py -c "..."`** в PowerShell не передаёт двойные кавычки. Использовать двойные снаружи + одинарные Python внутри. |
| 4 | **`.Split("# ...")`** в PowerShell — по символам. Для подстроки — `-split [regex]::Escape("...")`. |
| 5 | **Heredoc `@'...'@`** через копипаст ломается. Надёжнее — VS Code или массив строк. |
| 6 | **`git diff`** открывает `less` — использовать `git --no-pager diff`. |
| 7 | **`Measure-Object -Line`** считает непустые строки; `(Get-Content file).Count` — все. |

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
`Push:` после каждого коммита (SSH, порт 22).

### Документация
Стиль: Markdown, таблицы, разделы.
Комментарии — не сокращать.
Структура — полная (все файлы, вложенные папки).

---

## Следующий шаг (после 21.10.2026)

**Приёмка MVP (шаг 10):**
1. Убедиться, что `keys/executor_pubkey.bin` на ESP32 совпадает с нашим.
2. `py main.py build` → `outputfiles/program.enc` (FILE).
3. Скопировать на ESP32 (mpremote) **или** переключить `transport: "mqtt"` → ESP32 подписан на топик.
4. ESP32: `parse_packet` → JSON → `exec(setup) + exec(loop_logic)` → мигает 2 минуты.
5. Если формат/ключи не совпадают — отладка (сверить `executor_pubkey`, `esp32_private_key`).

**Документация (этап 9):**
- `README.md` — статус.
- `DECISIONS_LOG.md` — 4 новых решения.
- `inputfiles/README.md` — JSON, не `.py`.

---

## Ссылки

- **TUR55 Standard** — https://github.com/Tabintaban/Protocol_TUR55
- **ESP32_Python_FUEL** — https://github.com/Tabintaban/ESP32_Python_FUEL
- **TUR55_Executor** — https://github.com/Tabintaban/TUR55_Executor
- **NIST SP 800-38D** — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf
- **embit** — https://github.com/diybitcoinhardware/embit
- **paho-mqtt** — https://github.com/eclipse-paho/paho.mqtt.python

