"""Сгенерировать secp256k1 ключи Executor → raw 32/33 байта."""
from __future__ import annotations
import os
from pathlib import Path
from embit.ec import PrivateKey


def main() -> int:
    secret = os.urandom(32)
    sk = PrivateKey(secret)
    pubkey = sk.get_public_key().sec()
    out = Path("keys")
    out.mkdir(parents=True, exist_ok=True)
    (out / "executor_private_key.bin").write_bytes(secret)
    (out / "executor_pubkey.bin").write_bytes(pubkey)
    print("Saved: keys/executor_private_key.bin")
    print("Saved: keys/executor_pubkey.bin")
    print(f"Pubkey: {pubkey.hex()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())