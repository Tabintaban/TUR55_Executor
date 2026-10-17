# HANDOFF — TUR55_Executor

**Дата:** 2026-10-17
**Цель:** передать контекст новому диалогу/ассистенту для продолжения работы.

---

## Что такое TUR55_Executor

**TUR55_Executor** — реализация **Layer 2 (Executor Layer)** стандарта **TUR55**.

**Стандарт:** https://github.com/Tabintaban/Protocol_TUR55
**Автор стандарта:** NOMOS-H, зафиксирован 2026-04-10.

**Репозиторий:** https://github.com/Tabintaban/TUR55_Executor
**Локально:** `C:\Users\user\Documents\Projects\TUR55_Executor`

### Задача Executor

Executor — **сервер** (Python, CPython), который:

1. **Слушает** блокчейн (Ethereum / Solana / Tron)
2. **Извлекает** событие `ExecutorTriggered(user_wallet, amount, expires, device_id, metadata)`
3. **Формирует** JSON-конверт TUR55 (раздел 3.2)
4. **Встраивает** данные в Python-скрипт (раздел 3.3)
5. **Шифрует**:
   - сессионный ключ → RSA-OAEP (публичный ключ ESP32)
   - скрипт → AES-256-GCM
6. **Подписывает** → ECDSA secp256k1
7. **Собирает** пакет TUR55 (раздел 3.4)
8. **Отправляет** через **Delivery Layer** (MQTT / HTTP / BLE / LoRaWAN / QR / NFC / SD / USB)

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
│ ├── Event/
│ │ ├── ethereum.py ← описание (не код)
│ │ ├── solana.py ← описание
│ │ └── tron.py ← описание
│ ├── Delivery/
│ │ ├── MQTT.py ← описание
│ │ ├── HTTP_HTTPS.py ← описание
│ │ ├── Bluetooth_BLE.py ← описание
│ │ ├── LoraWAN.py ← описание
│ │ ├── QR-code_NFC.py ← описание
│ │ └── SD_USB.py ← описание
│ └── Executor/
│ ├── tur55_packet.py ← готовый код (из ESP32)
│ └── build_packet_cpython.py ← готовый код (из ESP32)
├── configs/
│ ├── README.md
│ └── settings.json ← в .gitignore (секрет)
├── inputfiles/
│ └── README.md ← шаблоны скриптов для ESP32
├── outputfiles/
│ └── README.md ← program.enc (physical delivery)
├── test/
│ └── README.md ← все тесты только здесь
├── .gitignore
├── main.py ← пустой
├── README.md ← пустой
└── README_RU.md ← пустой
```

### Что перенесено из ESP32

- **`tur55_packet.py`** — формат пакета TUR55 (build + parse), ~9.5 KB
- **`build_packet_cpython.py`** — сборка пакета (CPython), ~6 KB

### Коммиты

b030657 README для inputfiles, outputfiles, test, configs
19d16f6 структура проекта (Layers/Event, Layers/Delivery, Layers/Executor)


**Оба запушены** в `origin/main`.

---

## Что нужно (MVP)

### 1. `configs/settings.example.json` — шаблон настроек

**Не принято:** структура (моя версия или своя).

**Моя версия:**

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
    "contract_address": "0x...",
    "event_name": "ExecutorTriggered",
    "poll_interval_sec": 5
  },
  "delivery": {
    "transport": "mqtt",
    "mqtt": {
      "broker": "broker.hivemq.com",
      "port": 1883,
      "topic": "tur55/device/esp32_001"
    },
    "file": {
      "output_dir": "outputfiles/"
    }
  },
  "keys": {
    "esp32_public_key": "esp32_public_key.pem",
    "executor_private_key": "executor_private_key.pem"
  }
}
```
2. `README.md` — описание проекта
Не начато. Краткое: что, зачем, как (`build`, `send`, `listen`).

3. `main.py` — CLI-каркас
Не начато. Планируется argparse:

`build` — сформировать пакет

`send` — отправить по транспорту

`listen` — слушать блокчейн (мок)

4. `Layers/Executor/` — основной код
Не начато. Планируется:

`event_listener.py` — слушатель блокчейна (мок + опционально web3.py)

`script_template.py` — встраивание данных в скрипт

`packet_builder.py` — обёртка tur55_packet + build_packet

`delivery.py` — единый интерфейс (MQTT / файл)

5. `test/ — тесты`
Не начато. Правило: все тесты — только в `test/`.

## Открытые вопросы (не приняты) ##
### Блокчейн первым:###

(а) Ethereum (`ethereum.py` — заглушка)

(б) Solana (`solana.py` — заглушка)

(в) Tron (`tron.py` — заглушка)

### Транспорт по умолчанию:###

(а) MQTT (уже есть mqtt_publisher.py в ESP32)

(б) Файл (outputfiles/program.enc)

(в) Оба (выбор через settings.json)

`inputfiles/` — какие шаблоны скриптов:

`led_control.py`, `unlock.py`, `sensor_read.py`?

Другие?

## Правила работы (для нового ассистента) ##
### Стиль ###
Пошагово — не забегать вперёд.

Всегда показывай что найти и что заменить (для правок).

Всегда — `git status` перед `git add`.

Всегда — `py_compile` перед запуском.

Не сокращай структуру и комментарии.

Не гадай — если не знаешь, спроси или скинь документ.

### Среда ###
`Windows PowerShell: C:\Users\user\Documents\Projects\`

`WSL:` сборка прошивки ESP32 (не для Executor).

`ESP32: MicroPico / miniterm` (для тестов Layer 4).

`Git`
Перед коммитом: `git status` → `git add -A` → `git status` → `git commit`.

Сообщения: на русском, кратко, по делу.

`Push:` после каждого коммита.

### Документация ###
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

Следующий шаг (после нового диалога)
Ответить на 3 вопроса:

Блокчейн первым: `Ethereum / Solana / Tron?`

Транспорт по умолчанию: `MQTT / файл / оба?`

Шаблоны в `inputfiles/`: какие?

Потом — создать:

`configs/settings.example.json`

`README.md`

`main.py` (CLI-каркас)

`Layers/Executor/event_listener.py` (мок)

Ссылки
`TUR55 Standard: https://github.com/Tabintaban/Protocol_TUR55`

`ESP32_Python_FUEL: https://github.com/Tabintaban/ESP32_Python_FUEL`

`TUR55_Executor: https://github.com/Tabintaban/TUR55_Executor`

`NIST SP 800-38D: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf`

`embit (CPython ECDSA): https://github.com/diybitcoinhardware/embit`

`paho-mqtt: https://github.com/eclipse-paho/paho.mqtt.python`

