
# TUR55_Executor

Реализация **Layer 2 (Executor Layer)** стандарта [TUR55](https://github.com/Tabintaban/Protocol_TUR55).

Executor — сервер (CPython), который слушает блокчейн, извлекает событие `ExecutorTriggered(user_wallet, amount, expires, device_id, metadata)`, собирает JSON-конверт TUR55, шифрует скрипт (RSA-OAEP + AES-256-GCM), подписывает пакет (ECDSA secp256k1) и доставляет его на устройство Layer 4 через Delivery Layer.

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
4. **Формирует** полезную нагрузку исполняемого скрипта.
5. **Шифрует**: сессионный ключ → RSA-OAEP (публичный ключ ESP32); скрипт → AES-256-GCM.
6. **Подписывает** пакет → ECDSA secp256k1.
7. **Собирает** пакет TUR55 (раздел 3.4).
8. **Доставляет** через Delivery Layer (MQTT / HTTP / BLE / LoRaWAN / QR / NFC / SD / USB).

---

## Структура репозитория

```
TUR55_Executor/
├── Layers/
│   ├── Event/
│   │   ├── ethereum.py          ← слушатель Ethereum (web3.py)
│   │   ├── solana.py            ← описание
│   │   └── tron.py              ← описание
│   ├── Delivery/
│   │   ├── FILE.py              ← save(packet, config) → outputfiles/program.enc
│   │   ├── MQTT.py              ← publish(packet, config) → broker
│   │   ├── HTTP_HTTPS.py        ← описание
│   │   ├── Bluetooth_BLE.py     ← описание
│   │   ├── LoraWAN.py           ← описание
│   │   ├── QR-code_NFC.py       ← описание
│   │   └── SD_USB.py            ← описание
│   └── Executor/
│       ├── tur55_packet.py      ← формат пакета TUR55 (parse)
│       ├── build_packet_cpython.py  ← build_packet (RSA-OAEP + AES-GCM + ECDSA)
│       ├── packet_builder.py    ← PacketBuilder.build_from_event() (max_iterations)
│       ├── delivery.py          ← send(packet, config) — диспетчер
│       └── script_template.py   ← build_script (не используется)
├── configs/
│   ├── README.md
│   └── ethereum.example.json    ← шаблон (ethereum.json — в .gitignore)
├── inputfiles/
│   ├── README.md
│   └── example_led.json         ← программа для ESP32 (setup/loop_logic/custom_data)
├── outputfiles/                 ← program.enc (физическая доставка)
├── test/
│   ├── conftest.py
│   ├── test_event_mock.py
│   ├── test_packet_roundtrip.py
│   ├── test_script_template.py
│   └── test_delivery_file.py
├── main.py                      ← CLI: build / send / listen
├── README.md                    ← этот файл (EN)
└── README_RU.md                 ← этот файл (RU)
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
| `web3` | слушатель Ethereum | **используется** |
| `paho-mqtt` | транспорт MQTT | **используется** (MQTT) |
| `embit` | ECDSA secp256k1 | **выбран** (не `coincurve` — см. `ERRORS_AND_SOLUTIONS.md` #16) |
| `cryptography` | RSA-OAEP + AES-256-GCM | **используется** (`build_packet_cpython.py`) |

---

## Быстрый старт

```powershell
# 1. Настройки
copy configs\ethereum.example.json configs\ethereum.json
# отредактировать ethereum.json: rpc_url, contract_address, device_id, пути к ключам

# 2. Сборка пакета TUR55
py main.py build

# 3. Отправка через Delivery Layer (MQTT / file / both)
py main.py send

# 4. Слушатель блокчейна (мок / реальный)
py main.py listen
```

> `listen` и `build` работают: `build` собирает пакет TUR55 и сохраняет в `outputfiles/program.enc`.
> `send` — CLI-команда (сейчас через `build` → `delivery.send`).
> `transport: "file"` / `"mqtt"` / `"both"` в `configs/ethereum.json`.

---

### 🚀 Сквозной сценарий (Sepolia → ESP32)

Для проверки полной цепочки (от события в блокчейне до исполнения на устройстве) используется команда **`build`**, а не `listen`.

1. **Убедитесь, что ESP32 подключена** к тому же брокеру MQTT (или используйте локальный Mosquitto).
2. **Запустите Executor:**
   ```bash
   py main.py build
   ```
   *(Он будет ждать одно новое событие из блокчейна).*
3. **Отправьте транзакцию** в смарт-контракт (например, через ваш скрипт `send_test.py` или Remix).
4. **Executor поймает событие**, соберёт пакет TUR55, зашифрует, подпишет и отправит на ESP32 через MQTT (или сохранит в `outputfiles/`).
5. **ESP32 получит пакет** и исполнит его (светодиод замигает).

> **Важно:** Команда `py main.py listen` только **показывает** события в консоли (JSONL) и **не отправляет** их на устройство. Она полезна для отладки.

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
  - ✅ `listen` — слушатель Ethereum (мок / реальный через web3.py) → JSONL
  - ✅ `build` — пакет TUR55 → `outputfiles/program.enc` (RSA-OAEP + AES-256-GCM + ECDSA secp256k1)
  - ✅ Delivery — FILE + MQTT (диспетчер по `transport`)
  - ✅ Тесты — 17 passed (`py -m pytest test/ -v`)
  - ✅ **End-to-end Sepolia → ESP32 (27.10.2026)** — реальное событие из блокчейна, пакет собран и доставлен по MQTT, ESP32 исполнила скрипт (светодиод замигал).
  - ⏳ `send` — CLI-команда (сейчас через `build`)
  - ⏳ Поддержка Solana / Tron — в планах.

---

## Лицензия

См. TUR55 Standard (ссылка выше).
.