"""Извлечь публичный RSA-ключ ESP32 из esp32_private_key.json → PEM."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def _hex_or_int(v):
    return int(v, 16) if isinstance(v, str) else int(v)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    with open(args.input, "r", encoding="utf-8") as f:
        key = json.load(f)
    n = _hex_or_int(key["n"])
    e = _hex_or_int(key["e"])
    pub = rsa.RSAPublicNumbers(e, n).public_key()
    pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pem)
    print(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())