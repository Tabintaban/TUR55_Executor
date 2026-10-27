#!/usr/bin/env python3
"""TUR55_Executor — CLI skeleton (Layer 2, Executor).

Subcommands:
    build  — build a TUR55 packet from an event
    send   — deliver the packet via Delivery Layer
    listen — listen to the blockchain (mock / web3.py)

Usage (Windows):
    py main.py build
    py main.py send
    py main.py listen
    py main.py --help

Config: configs/ethereum.json (default).
Template: configs/ethereum.example.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Пути и константы
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = REPO_ROOT / "configs" / "ethereum.json"
EXAMPLE_CONFIG = REPO_ROOT / "configs" / "ethereum.example.json"

REQUIRED_SECTIONS = ("executor", "event", "delivery", "keys")


# ---------------------------------------------------------------------------
# Загрузка и валидация конфига
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict[str, Any]:
    """Load config. Behavior (a): if missing — clear error + exit 1."""
    if not path.exists():
        print(f"[ERROR] Config not found: {path}", file=sys.stderr)
        print("[HINT]  Copy the template:", file=sys.stderr)
        print(f"        copy {EXAMPLE_CONFIG.relative_to(REPO_ROOT)} {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        print(f"        then edit {path.relative_to(REPO_ROOT)} (rpc_url, contract_address, device_id, key paths).", file=sys.stderr)
        sys.exit(1)

    try:
        with path.open("r", encoding="utf-8-sig") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    missing = [s for s in REQUIRED_SECTIONS if s not in config]
    if missing:
        print(f"[ERROR] Missing required sections in {path}: {missing}", file=sys.stderr)
        sys.exit(1)

    # MVP: filename must match event.blockchain.
    expected_blockchain = path.name.split(".")[0]
    actual_blockchain = config.get("event", {}).get("blockchain")
    if actual_blockchain != expected_blockchain:
        print(
            f"[ERROR] Config {path.name}: event.blockchain={actual_blockchain!r}, "
            f"expected {expected_blockchain!r} (based on filename).",
            file=sys.stderr,
        )
        sys.exit(1)

    return config

# ---------------------------------------------------------------------------
# Подкоманды (каркас; реализация — шаг 4)
# ---------------------------------------------------------------------------

def cmd_build(config: dict[str, Any], verbose: bool) -> int:
    """build — собрать пакет TUR55 и доставить через Delivery."""
    from Layers.Event.ethereum import listen
    from Layers.Executor.packet_builder import PacketBuilder
    from Layers.Executor.delivery import send

    executor = config["executor"]
    if verbose:
        print(f"[build] config: executor={executor.get('name')} version={executor.get('version')}", file=sys.stderr)

    # 1. Одно событие
    event = next(iter(listen(config, verbose=verbose)))
    if verbose:
        print(f"[build] event: user={event['user_wallet'][:10]}... amount={event['amount']}", file=sys.stderr)

    # 2. Программа для ESP32
    program_rel = config["inputfiles"]["template"]
    program_path = REPO_ROOT / program_rel
    if not program_path.exists():
        print(f"[ERROR] Program not found: {program_path}", file=sys.stderr)
        return 1

    # 3. Собрать пакет
    builder = PacketBuilder(keys_dir=REPO_ROOT / "keys")
    packet = builder.build_from_event(event, program_path)

    # 4. Доставить через Delivery
    try:
        done = send(packet, config)
    except Exception as e:
        print(f"[ERROR] Delivery: {e}", file=sys.stderr)
        return 1

    print(f"[OK] Packet: {len(packet)} bytes -> transport: {done}")
    return 0

def cmd_send(config: dict[str, Any], verbose: bool) -> int:
    """send — доставить пакет через Delivery Layer.

    TODO (шаг 4):
      delivery.py — транспорт из config['delivery']['transport'] (mqtt / file / both).
    """
    transport = config["delivery"].get("transport", "?")
    if verbose:
        print(f"[send] transport: {transport}", file=sys.stderr)
    raise NotImplementedError("send: implementation — step 4 (Layers/Executor/delivery.py)")


def cmd_listen(config: dict[str, Any], verbose: bool) -> int:
    """listen — слушать Ethereum (мок / web3.py).

    Печатает события ExecutorTriggered в формате JSONL (одно событие = одна строка).
    Мок-режим ограничен config["event"]["mock"]["max_events"] (по умолчанию 3).
    """
    from Layers.Event.ethereum import listen

    event = config["event"]
    mock = event.get("use_mock", True)
    if verbose:
        print(f"[listen] blockchain={event.get('blockchain')} use_mock={mock}", file=sys.stderr)

    for ev in listen(config, verbose=verbose):
        print(json.dumps(ev, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="TUR55_Executor — CLI (Layer 2, Executor).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"path to config (default: {DEFAULT_CONFIG.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="verbose output (to stderr)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # Общие флаги подкоманд: --verbose принимается и после подкоманды
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=argparse.SUPPRESS,   # не перетирать значение от родителя
        help="verbose output (to stderr)",
    )

    sub.add_parser("build",  parents=[common], help="build a TUR55 packet from an event")
    sub.add_parser("send",   parents=[common], help="deliver the packet via Delivery Layer")
    sub.add_parser("listen", parents=[common], help="listen to the blockchain (mock / web3.py)")

    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config(args.config)

    handlers = {
        "build": cmd_build,
        "send": cmd_send,
        "listen": cmd_listen,
    }
    handler = handlers[args.command]

    try:
        return handler(config, args.verbose)
    except NotImplementedError as e:
        print(f"[NOT IMPLEMENTED] {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())