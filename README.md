
# TUR55_Executor

Implementation of **Layer 2 (Executor Layer)** of the [TUR55 standard](https://github.com/Tabintaban/Protocol_TUR55).

The Executor is a server (CPython) that listens to the blockchain, extracts the `ExecutorTriggered(user_wallet, amount, expires, device_id, metadata)` event, builds the TUR55 JSON envelope, encrypts the script (RSA-OAEP + AES-256-GCM), signs the packet (ECDSA secp256k1), and delivers it to the Layer 4 device via the Delivery Layer.

**Related project:** [ESP32_Python_FUEL](https://github.com/Tabintaban/ESP32_Python_FUEL) — Layer 4 (Execution Layer), ~95% TUR55/Bronze, Bronze closed.

---

## Layer Architecture

```
  Blockchain (Ethereum / Solana / Tron)
        │  ExecutorTriggered event
        ▼
  ┌──────────────────────────┐
  │  Layer 2: TUR55_Executor │  ← this repository
  │  (CPython, server)       │
  └──────────────────────────┘
        │  TUR55 packet (section 3.4)
        ▼
  Delivery Layer (MQTT / HTTP / BLE / LoRaWAN / QR / NFC / SD / USB)
        │
        ▼
  Layer 4: ESP32_Python_FUEL (MicroPython, device)
```

---

## What the Executor does (8 steps)

1. **Listens** to the blockchain (Ethereum / Solana / Tron).
2. **Extracts** the `ExecutorTriggered(user_wallet, amount, expires, device_id, metadata)` event.
3. **Builds** the TUR55 JSON envelope (section 3.2).
4. **Forms** the executable script payload.
5. **Encrypts**: session key → RSA-OAEP (ESP32 public key); script → AES-256-GCM.
6. **Signs** the packet → ECDSA secp256k1.
7. **Assembles** the TUR55 packet (section 3.4).
8. **Delivers** via the Delivery Layer (MQTT / HTTP / BLE / LoRaWAN / QR / NFC / SD / USB).

---

## Repository Structure

```
TUR55_Executor/
├── Layers/
│   ├── Event/
│   │   ├── ethereum.py          ← Ethereum listener (web3.py)
│   │   ├── solana.py            ← description
│   │   └── tron.py              ← description
│   ├── Delivery/
│   │   ├── FILE.py              ← save(packet, config) → outputfiles/program.enc
│   │   ├── MQTT.py              ← publish(packet, config) → broker
│   │   ├── HTTP_HTTPS.py        ← description
│   │   ├── Bluetooth_BLE.py     ← description
│   │   ├── LoraWAN.py           ← description
│   │   ├── QR-code_NFC.py       ← description
│   │   └── SD_USB.py            ← description
│   └── Executor/
│       ├── tur55_packet.py      ← TUR55 packet format (parse)
│       ├── build_packet_cpython.py  ← build_packet (RSA-OAEP + AES-GCM + ECDSA)
│       ├── packet_builder.py    ← PacketBuilder.build_from_event() (max_iterations)
│       ├── delivery.py          ← send(packet, config) — dispatcher
│       └── script_template.py   ← build_script (unused)
├── configs/
│   ├── README.md
│   └── ethereum.example.json    ← template (ethereum.json — in .gitignore)
├── inputfiles/
│   ├── README.md
│   └── example_led.json         ← ESP32 program (setup/loop_logic/custom_data)
├── outputfiles/                 ← program.enc (physical delivery)
├── test/
│   ├── conftest.py
│   ├── test_event_mock.py
│   ├── test_packet_roundtrip.py
│   ├── test_script_template.py
│   └── test_delivery_file.py
├── main.py                      ← CLI: build / send / listen
├── README.md                    ← this file
└── README_RU.md
```

---

## Requirements

- **Python 3.14** (Windows, CPython) — reference environment. See `ESP32_Python_FUEL/ERRORS_AND_SOLUTIONS.md` (error 16: `coincurve` does not install on 3.14 → use `embit`).
- **`py`** instead of `python` (Windows launcher): `py main.py`, `py -m pip install ...`, `py -m py_compile`, `py -m pytest`.
- Windows PowerShell (Executor development) / WSL Ubuntu 22.04 + Python 3.10.12 (ESP-IDF firmware build — **not for Executor**).
- Git.

**Dependencies (candidates, refined as implementation progresses):**

| Package | Purpose | Status |
|---------|---------|--------|
| `web3` | Ethereum listener | **used** |
| `paho-mqtt` | MQTT transport | **used** (MQTT) |
| `embit` | ECDSA secp256k1 | **selected** (not `coincurve` — see `ERRORS_AND_SOLUTIONS.md` #16) |
| `cryptography` | RSA-OAEP + AES-256-GCM | **used** (`build_packet_cpython.py`) |

---

## Quick Start

```powershell
# 1. Configuration
copy configs\ethereum.example.json configs\ethereum.json
# edit ethereum.json: rpc_url, contract_address, device_id, key paths

# 2. Build the TUR55 packet
py main.py build

# 3. Deliver via Delivery Layer (MQTT / file / both)
py main.py send

# 4. Blockchain listener (mock / real)
py main.py listen
```

> `listen` and `build` work: `build` assembles the TUR55 packet and saves it to `outputfiles/program.enc`.
> `send` — CLI command (currently via `build` → `delivery.send`).
> `transport: "file"` / `"mqtt"` / `"both"` in `configs/ethereum.json`.

---

### 🚀 End-to-End Scenario (Sepolia → ESP32)

To test the full pipeline (from a blockchain event to device execution), use the **`build`** command, not `listen`.

1. **Ensure ESP32 is connected** to the same MQTT broker (or use a local Mosquitto).
2. **Start the Executor:**
   ```bash
   py main.py build
   ```
   *(It will wait for one new event from the blockchain).*
3. **Send a transaction** to the smart contract (e.g., via your `send_test.py` script or Remix).
4. **The Executor catches the event**, assembles the TUR55 packet, encrypts, signs, and sends it to ESP32 via MQTT (or saves it to `outputfiles/`).
5. **ESP32 receives the packet** and executes it (the LED blinks).

> **Important:** The `py main.py listen` command only **prints** events to the console (JSONL) and **does not send** them to the device. It is useful for debugging.

---

## Documentation

- **TUR55 Standard** — https://github.com/Tabintaban/Protocol_TUR55
- **ESP32_Python_FUEL** (Layer 4) — https://github.com/Tabintaban/ESP32_Python_FUEL
- **NIST SP 800-38D** (GCM) — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf
- **embit** (CPython ECDSA) — https://github.com/diybitcoinhardware/embit
- **paho-mqtt** — https://github.com/eclipse-paho/paho.mqtt.python

---

## Status

- **MVP in development.**
- Layer 4 (ESP32_Python_FUEL): ~95% TUR55/Bronze, Bronze closed. eFuse, Secure boot — Gold level.
- Layer 2 (this repository):
  - ✅ `listen` — Ethereum listener (mock / real via web3.py) → JSONL
  - ✅ `build` — TUR55 packet → `outputfiles/program.enc` (RSA-OAEP + AES-256-GCM + ECDSA secp256k1)
  - ✅ Delivery — FILE + MQTT (dispatcher based on `transport`)
  - ✅ Tests — 17 passed (`py -m pytest test/ -v`)
  - ✅ **End-to-end Sepolia → ESP32 (27.10.2026)** — real event from the blockchain, packet assembled and delivered via MQTT, ESP32 executed the script (LED blinked).
  - ⏳ `send` — CLI command (currently via `build`)
  - ⏳ Solana / Tron support — planned.

---

## License

See TUR55 Standard (link above).
