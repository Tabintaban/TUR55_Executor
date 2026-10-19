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
    """Слушатель Ethereum через web3.py (каркас — реализация позже).

    TODO (следующий подшаг):
      1. Загрузить ABI контракта TUR55 (config["event"]["abi_path"], пока нет в конфиге).
      2. from web3 import Web3
         web3 = Web3(Web3.HTTPProvider(config["event"]["rpc_url"]))
         contract = web3.eth.contract(
             address=config["event"]["contract_address"], abi=abi
         )
      3. event_filter = contract.events.ExecutorTriggered.create_filter(from_block="latest")
      4. В цикле:
             for entry in event_filter.get_new_entries():
                 yield {
                     "user_wallet": entry["args"]["user_wallet"],
                     "amount":      entry["args"]["amount"],
                     "expires":     entry["args"]["expires"],
                     "device_id":   entry["args"]["device_id"],
                     "metadata":    entry["args"]["metadata"],
                 }
             time.sleep(config["event"]["poll_interval_sec"])
    """
    try:
        import web3  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "web3.py не установлен. Установите: py -m pip install web3"
        ) from e

    raise NotImplementedError(
        "web3.py: реализация — следующий подшаг "
        "(ABI, контракт, event_filter; см. TODO в docstring)"
    )