"""Тест сборки пакета TUR55 (без parse_packet)."""
import sys
from pathlib import Path

# Чтобы `from Layers.Executor...` работало при запуске из test/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Layers.Executor.packet_builder import PacketBuilder


def main() -> int:
    b = PacketBuilder("keys")
    ev = {
        "user_wallet": "0xabc",
        "amount": 50,
        "expires": 1792407556,
        "device_id": "esp32_001",
        "custom_data": {"duration_sec": 120},
    }
    pkt = b.build_from_event(ev, "inputfiles/example_led.json")

    print(f"Packet: {len(pkt)} bytes")
    print(f"Magic: {pkt[:4]}")
    print(f"Version: {int.from_bytes(pkt[4:6], 'big')}")
    print(f"Pubkey len: {pkt[8]}")
    print(f"Pubkey: {pkt[9:42].hex()}")
    print(f"Executor pubkey: {b.executor_pubkey.hex()}")
    print(f"Match: {pkt[9:42] == b.executor_pubkey}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())