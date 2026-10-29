"""Слушатель Ethereum — события ExecutorTriggered.

Единая точка входа:
    listen(config, verbose=False) -> Iterator[dict]

Две реализации:
    _listen_mock(config, verbose)   — мок-генератор (use_mock=True)
    _listen_web3(config, verbose)   — каркас web3.py (use_mock=False)

Мок детерминирован при одинаковом seed. Каждое событие — dict с полями:
    user_wallet : str  — "0x" + 40 hex
    amount      : int  — 1..100
    expires     : int  — unix ts, now + 3600
    device_id   : str  — config["executor"]["device_id"]
    metadata    : dict — {"nonce": int, "source": "mock", "event_index": int}

Параметры мока (config["event"]["mock"], все опциональны):
    max_events   : int | None — по умолчанию 3; None = бесконечно
    interval_sec : float      — по умолчанию 0.0
    seed         : int        — по умолчанию 0
"""

from __future__ import annotations

import random
import sys
import time
from typing import Any, Iterator


# ---------------------------------------------------------------------------
# Публичный интерфейс
# ---------------------------------------------------------------------------

def listen(config: dict[str, Any], verbose: bool = False) -> Iterator[dict[str, Any]]:
    """Итератор событий ExecutorTriggered (Ethereum).

    Если config["event"]["use_mock"] == True — мок.
    Иначе — web3.py по rpc_url + contract_address.
    """
    event_cfg = config.get("event", {})
    use_mock = event_cfg.get("use_mock", True)

    if use_mock:
        return _listen_mock(config, verbose)
    return _listen_web3(config, verbose)


# ---------------------------------------------------------------------------
# Мок-генератор (use_mock=True)
# ---------------------------------------------------------------------------

def _listen_mock(config: dict[str, Any], verbose: bool) -> Iterator[dict[str, Any]]:
    """Детерминированный мок событий ExecutorTriggered для Ethereum."""
    event_cfg = config.get("event", {})
    mock_cfg = event_cfg.get("mock", {})

    max_events = mock_cfg.get("max_events", 3)
    interval_sec = float(mock_cfg.get("interval_sec", 0.0))
    seed = int(mock_cfg.get("seed", 0))

    device_id = config.get("executor", {}).get("device_id", "esp32_001")

    rng = random.Random(seed)
    now = int(time.time())
    expires = now + 3600  # +1 час

    index = 0
    while max_events is None or index < max_events:
        wallet_hex = "".join(rng.choice("0123456789abcdef") for _ in range(40))
        custom_data = mock_cfg.get("custom_data", {"duration_sec": 120})
        event = {
            "user_wallet": "0x" + wallet_hex,
            "amount": rng.randint(1, 100),
            "expires": expires,
            "device_id": device_id,
            "metadata": {
                "nonce": index,
                "source": "mock",
                "event_index": index,
            },
            "custom_data": custom_data,
        }

        if verbose:
            print(
                f"[ethereum:mock] event #{index} "
                f"user={event['user_wallet'][:10]}... "
                f"amount={event['amount']} expires={expires}",
                file=sys.stderr,
            )

        yield event
        index += 1

        if interval_sec > 0 and (max_events is None or index < max_events):
            time.sleep(interval_sec)


# ---------------------------------------------------------------------------
# Каркас web3.py (use_mock=False)
# ---------------------------------------------------------------------------

def _listen_web3(config: dict[str, Any], verbose: bool) -> Iterator[dict[str, Any]]:
    """Слушатель Ethereum через web3.py (TUR55 v1.0, раздел 3.1).

    Маппинг полей события:
        userWallet (address)  -> user_wallet (str)
        amount     (uint256)  -> amount      (int)
        expires    (uint256)  -> expires     (int)
        deviceId   (bytes32)  -> device_id   (str, decode + rstrip)
        metadata   (bytes)    -> metadata    (dict, json.loads)

    custom_data из события НЕ читается — PacketBuilder берёт его
    из inputfiles/example_led.json (решение №18, DECISIONS_LOG.md).
    """
    import json
    import time

    try:
        from web3 import Web3
    except ImportError:
        raise RuntimeError(
            "web3.py не установлен. Установите: py -m pip install web3"
        )

    ev_cfg = config["event"]
    rpc_url = ev_cfg["rpc_url"]
    contract_address = ev_cfg["contract_address"]
    abi_path = ev_cfg["abi_path"]
    poll_interval = ev_cfg.get("poll_interval_sec", 5)

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"web3.py: не удалось подключиться к {rpc_url}")

    with open(abi_path, "r", encoding="utf-8") as f:
        abi = json.load(f)

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=abi,
    )

    # Запоминаем блок, с которого начинаем (строго после текущего)
    # Это ключевой момент: мы хотим слушать только НОВЫЕ блоки.
    # Вместо ручного отслеживания start_block используем фильтр новых блоков
    block_filter = w3.eth.filter('latest')

    if verbose:
        print(f"[web3] connected: {rpc_url}")
        print(f"[web3] contract:  {contract_address}")
        print(f"[web3] waiting for new blocks...")

    while True:
        try:
            # Получаем хэши только что появившихся блоков
            new_block_hashes = block_filter.get_new_entries()
            
            for block_hash in new_block_hashes:
                # --- ГЛАВНЫЙ ФИКС: Запрашиваем логи по ХЭШУ, а не по номеру ---
                # Это гарантирует, что узел не ответит ошибкой "block range extends beyond".
                logs = []
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        logs = contract.events.ExecutorTriggered.get_logs(
                            block_hash=block_hash
                        )
                        break  # Успех, выходим из цикла попыток
                    except Exception as e:
                        if "block range" in str(e) or "invalid" in str(e):
                            if verbose:
                                print(f"[web3] block {block_hash.hex()} not ready yet (attempt {attempt+1}/{max_retries}), waiting...")
                            time.sleep(2)
                        else:
                            raise e
                else:
                    # Если все 5 попыток провалились, пропускаем блок
                    if verbose:
                        print(f"[web3] failed to get logs for block {block_hash.hex()}")
                    continue
                # -----------------------------------------------------------------
                
                for entry in logs:
                    args = entry["args"]
                    # ... (дальше ваш код обработки userWallet, deviceId и т.д. остается без изменений) ...
                
                for entry in logs:
                    args = entry["args"]
                    raw_device_id = args["deviceId"]
                    raw_metadata = args["metadata"]

                    # bytes32 -> str (rstrip нулей паддинга)
                    device_id = raw_device_id.decode("utf-8").rstrip("\x00")

                    # bytes -> dict (JSON)
                    try:
                        metadata = json.loads(raw_metadata.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as e:
                        if verbose:
                            print(f"[web3] skip event: metadata not JSON ({e})")
                        continue

                    event = {
                        "user_wallet": args["userWallet"],
                        "amount":      args["amount"],
                        "expires":     args["expires"],
                        "device_id":   device_id,
                        "metadata":    metadata,
                    }

                    if verbose:
                        print(
                            f"[web3] event: user={event['user_wallet'][:10]}... "
                            f"amount={event['amount']} expires={event['expires']} "
                            f"device={event['device_id']}"
                        )
                    yield event

        except Exception as e:
            if verbose:
                print(f"[web3] error while processing new block: {e}")

        time.sleep(poll_interval)