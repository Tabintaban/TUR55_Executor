# TUR55_Executor

Реализация **Layer 2 (Executor Layer)** стандарта [TUR55](https://github.com/Tabintaban/Protocol_TUR55).

Executor — сервер (CPython), который слушает блокчейн, извлекает событие `ExecutorTriggered(user_wallet, amount, expires, device_id, metadata)`, собирает JSON-конверт TUR55, встраивает его в Python-скрипт, шифрует (RSA-OAEP + AES-256-GCM), подписывает (ECDSA secp256k1) и доставляет пакет на устройство Layer 4 через Delivery Layer.

**Связанный проект:** [ESP32_Python_FUEL](https://github.com/Tabintaban/ESP32_Python_FUEL) — Layer 4 (Execution Layer), ~95% TUR55/Bronze, Bronze закрыт.

---

## Схема слоёв

```
  Блокчейн (Ethereum / Solana / Tron)
        │  событие ExecutorTriggered
        ▼
  ┌──────────────────────────┐
  │  Layer 2: TUR55_Executor │  ← этот репозиторий
  │  (CPython, сервер)       │
  └──────────────────────────┘
        │  пакет TUR55 (раздел 3.4)
        ▼
  Delivery Layer (MQTT / HTTP / BLE / LoRaWAN / QR / NFC / SD / USB)
        │
        ▼
  Layer 4: ESP32_Python_FUEL (MicroPython, устройство)
```

---

## Что делает Executor (8 шагов)

1. **Слушает** блокчейн (Ethereum / Solana / Tron).
2. **Извлекает** событие `ExecutorTriggered(user_wallet, amount, expires, device_id, metadata)`.
3. **Формирует** JSON-конверт TUR55 (раздел 3.2).
4. **Встраивает** конверт в Python-скрипт (раздел 3.3).
5. **Шифрует**: сессионный ключ → RSA-OAEP (публичный ключ ESP32); скрипт → AES-256-GCM.
6. **Подписывает** пакет → ECDSA secp256k1.
7. **Собирает** пакет TUR55 (раздел 3.4).
8. **Отправляет** через Delivery Layer (MQTT / HTTP / BLE / LoRaWAN / QR / NFC / SD / USB).

---

## Структура репозитория

```
TUR55_Executor/
├── Layers/
│   ├── Event/
│   │   ├── ethereum.py          ← слушатель Ethereum (заглушка → web3.py)
│   │   ├── solana.py            ← описание
│   │   └── tron.py              ← описание
│   ├── Delivery/
│   │   ├── MQTT.py              ← описание
│   │   ├── HTTP_HTTPS.py        ← описание
│   │   ├── Bluetooth_BLE.py     ← описание
│   │   ├── LoraWAN.py           ← описание
│   │   ├── QR-code_NFC.py       ← описание
│   │   └── SD_USB.py            ← описание
│   └── Executor/
│       ├── tur55_packet.py      ← формат пакета TUR55 (build + parse)
│       └── build_packet_cpython.py  ← сборка пакета (CPython)
├── configs/
│   ├── README.md
│   └── settings.example.json    ← шаблон (settings.json — в .gitignore)
├── inputfiles/                  ← шаблоны скриптов для ESP32
├── outputfiles/                 ← program.enc (физическая доставка)
├── test/                        ← все тесты только здесь
├── main.py                      ← CLI: build / send / listen
├── README.md                    ← этот файл
└── README_RU.md
```

---

## Требования

- **Python 3.14** (Windows, CPython) — эталон проекта. См. `ESP32_Python_FUEL/ERRORS_AND_SOLUTIONS.md` (ошибка 16: `coincurve` не ставится на 3.14 → используем `embit`).
- **`py`** вместо `python` (Windows launcher): `py main.py`, `py -m pip install ...`, `py -m py_compile`, `py -m pytest`.
- Windows PowerShell (разработка Executor) / WSL Ubuntu 22.04 + Python 3.10.12 (сборка прошивки ESP-IDF — **не для Executor**).
- Git.

**Зависимости (кандидаты, уточняются по мере реализации):**

| Пакет | Назначение | Статус |
|-------|------------|--------|
| `web3` | слушатель Ethereum | планируется (шаг 4) |
| `paho-mqtt` | транспорт MQTT | планируется (шаг 4) |
| `embit` | ECDSA secp256k1 | **выбран** (не `coincurve` — см. `ERRORS_AND_SOLUTIONS.md` #16) |
| `cryptography` | RSA-OAEP + AES-256-GCM | планируется |

---

## Быстрый старт

```powershell
# 1. Настройки
copy configs\settings.example.json configs\settings.json
# отредактировать settings.json: rpc_url, contract_address, device_id, пути к ключам

# 2. Сборка пакета TUR55
py main.py build

# 3. Отправка через Delivery Layer (MQTT / file / both)
py main.py send

# 4. Слушатель блокчейна (мок / реальный)
py main.py listen
```

> `listen` и `build` работают (мок Ethereum → готовый скрипт с `TUR55_PAYLOAD`).
> `send` — пока `NotImplementedError` (Delivery — шаг 7).

---

## Документация

- **TUR55 Standard** — https://github.com/Tabintaban/Protocol_TUR55
- **ESP32_Python_FUEL** (Layer 4) — https://github.com/Tabintaban/ESP32_Python_FUEL
- **NIST SP 800-38D** (GCM) — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf
- **embit** (CPython ECDSA) — https://github.com/diybitcoinhardware/embit
- **paho-mqtt** — https://github.com/eclipse-paho/paho.mqtt.python

---

## Статус

- **MVP в разработке.**
- Layer 4 (ESP32_Python_FUEL): ~95% TUR55/Bronze, Bronze закрыт. eFuse, Secure boot — Gold уровень.
- Layer 2 (этот репозиторий):
  - ✅ `listen` — слушатель Ethereum (мок) → JSONL
  - ✅ `build` — встраивание payload в шаблон → готовый Python-скрипт
  - ⏳ `send` — Delivery (MQTT + file) — шаг 7
  - ⏳ шифрование + сборка пакета TUR55 — шаг 6 (открытый вопрос: JSON / скрипт / оба)
  - ⏳ тесты (`test/`) — шаг 8

---

## Лицензия

См. TUR55 Standard (ссылка выше).

