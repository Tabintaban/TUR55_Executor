"""Сборка пакета TUR55 из события + программы (JSON).

Читает inputfiles/*.json (setup/loop_logic), добавляет данные события
(user_wallet, amount, expires), вызывает build_packet → байты.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization


class PacketBuilder:
    """Обёртка над build_packet: событие + программа → пакет TUR55."""

    def __init__(self, keys_dir: Path | str = "keys"):
        self.keys_dir = Path(keys_dir)
        self._load_keys()

    def _load_keys(self) -> None:
        with open(self.keys_dir / "esp32_public_key.pem", "rb") as f:
            self.esp32_public_key = serialization.load_pem_public_key(f.read())

        with open(self.keys_dir / "executor_private_key.bin", "rb") as f:
            self.executor_secret = f.read()

        with open(self.keys_dir / "executor_pubkey.bin", "rb") as f:
            self.executor_pubkey = f.read()

    def build_from_event(
        self,
        event: dict[str, Any],
        program_path: Path | str,
    ) -> bytes:
        """Собрать пакет TUR55 из события и программы."""
        with open(program_path, "r", encoding="utf-8") as f:
            program = json.load(f)

        setup_lines = program.get("setup", [])
        loop_lines = program.get("loop_logic", [])
        functions = program.get("functions", [])
        program_custom_data = program.get("custom_data", {})

        custom_data = {**program_custom_data, **(event.get("custom_data") or {})}

        # Вычисляем max_iterations из duration_sec (2 итерации = 1 сек)
        duration_sec = int(custom_data.get("duration_sec") or 120)
        max_iterations = duration_sec * 2  # 0.5 сек × 2 = 1 сек за итерацию

        json_data = {
            "tur55_version": "1.0",
            "command_id": event.get("command_id", "0xauto"),
            "device_id": event.get("device_id", "esp32_001"),
            "source": {
                "smart_contract": event.get("smart_contract", "0x0"),
                "transaction_hash": event.get("transaction_hash", "0x0"),
                "block_number": event.get("block_number", 0),
            },
             "execution": {
                "user_wallet": event.get("user_wallet", "0x0"),
                "amount": event.get("amount", 0),
                "expires": event.get("expires", 0),
                "max_iterations": max_iterations,
                "runtime_limit_ms": 5000,
                "memory_limit_kb": 25,
                "permissions": ["gpio", "time"],
                "functions": functions,
                "setup": setup_lines,
                "loop_logic": loop_lines,
            },
            "custom_data": custom_data,
        }

        from Layers.Executor.build_packet_cpython import build_packet
        from embit.ec import PrivateKey

        # Превращаем байты (32) в объект embit PrivateKey
        executor_sk = PrivateKey(self.executor_secret)

        return build_packet(
            json_data,
            self.esp32_public_key,
            executor_sk,
            self.executor_pubkey,
        )
    