#!/usr/bin/env python3
"""TUR55_Executor — CLI-каркас (Layer 2, Executor).

Подкоманды:
    build  — собрать пакет TUR55 из события (шаг 4)
    send   — доставить пакет через Delivery Layer (шаг 4)
    listen — слушать блокчейн (мок / web3.py) (шаг 4)

Запуск (Windows):
    py main.py build
    py main.py send
    py main.py listen
    py main.py --help

Настройки: configs/settings.json (по умолчанию).
Шаблон: configs/settings.example.json.
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
DEFAULT_CONFIG = REPO_ROOT / "configs" / "settings.json"
EXAMPLE_CONFIG = REPO_ROOT / "configs" / "settings.example.json"

REQUIRED_SECTIONS = ("executor", "event", "delivery", "keys")


# ---------------------------------------------------------------------------
# Загрузка и валидация конфига
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict[str, Any]:
    """Загрузить settings.json. Поведение (а): при отсутствии — понятная ошибка + exit 1."""
    if not path.exists():
        print(f"[ERROR] Конфиг не найден: {path}", file=sys.stderr)
        print("[HINT]  Скопируйте шаблон:", file=sys.stderr)
        print(f"        copy {EXAMPLE_CONFIG.relative_to(REPO_ROOT)} {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        print(f"        затем отредактируйте {path.relative_to(REPO_ROOT)} (rpc_url, contract_address, device_id, пути к ключам).", file=sys.stderr)
        sys.exit(1)

    try:
        with path.open("r", encoding="utf-8-sig") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Некорректный JSON в {path}: {e}", file=sys.stderr)
        sys.exit(1)

    missing = [s for s in REQUIRED_SECTIONS if s not in config]
    if missing:
        print(f"[ERROR] В {path} отсутствуют обязательные секции: {missing}", file=sys.stderr)
        sys.exit(1)

    return config


# ---------------------------------------------------------------------------
# Подкоманды (каркас; реализация — шаг 4)
# ---------------------------------------------------------------------------

def cmd_build(config: dict[str, Any], verbose: bool) -> int:
    """build — собрать пакет TUR55 из события.

    TODO (шаг 4):
      1. event_listener.py  — получить событие ExecutorTriggered
      2. script_template.py — встроить JSON-конверт (3.2) в скрипт (3.3)
      3. packet_builder.py  — собрать пакет TUR55 (3.4) через Layers/Executor/tur55_packet.py
    """
    if verbose:
        executor = config["executor"]
        print(f"[build] config: executor={executor.get('name')} version={executor.get('version')}", file=sys.stderr)
    raise NotImplementedError("build: реализация — шаг 4 (Layers/Executor/*)")


def cmd_send(config: dict[str, Any], verbose: bool) -> int:
    """send — доставить пакет через Delivery Layer.

    TODO (шаг 4):
      delivery.py — транспорт из config['delivery']['transport'] (mqtt / file / both).
    """
    transport = config["delivery"].get("transport", "?")
    if verbose:
        print(f"[send] transport: {transport}", file=sys.stderr)
    raise NotImplementedError("send: реализация — шаг 4 (Layers/Executor/delivery.py)")


def cmd_listen(config: dict[str, Any], verbose: bool) -> int:
    """listen — слушать блокчейн (мок / web3.py).

    TODO (шаг 4):
      event_listener.py — мок при config['event']['use_mock']=true,
                          иначе web3.py по config['event']['rpc_url'] + contract_address.
    """
    event = config["event"]
    mock = event.get("use_mock", True)
    if verbose:
        print(f"[listen] blockchain={event.get('blockchain')} use_mock={mock}", file=sys.stderr)
    raise NotImplementedError("listen: реализация — шаг 4 (Layers/Executor/event_listener.py)")


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
        help=f"путь к settings.json (по умолчанию: {DEFAULT_CONFIG.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="подробный вывод (в stderr)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # Общие флаги подкоманд: --verbose принимается и после подкоманды
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=argparse.SUPPRESS,   # не перетирать значение от родителя
        help="подробный вывод (в stderr)",
    )

    sub.add_parser("build",  parents=[common], help="собрать пакет TUR55 из события (шаг 4)")
    sub.add_parser("send",   parents=[common], help="доставить пакет через Delivery Layer (шаг 4)")
    sub.add_parser("listen", parents=[common], help="слушать блокчейн (мок / web3.py) (шаг 4)")

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