"""Тесты для Layers/Executor/packet_builder.py — структура пакета TUR55."""
from Layers.Executor.packet_builder import PacketBuilder


def test_build_returns_bytes(keys_dir, program_led, sample_event):
    b = PacketBuilder(keys_dir=keys_dir)
    pkt = b.build_from_event(sample_event, program_led)
    assert isinstance(pkt, bytes)
    assert len(pkt) > 100


def test_packet_magic(keys_dir, program_led, sample_event):
    b = PacketBuilder(keys_dir=keys_dir)
    pkt = b.build_from_event(sample_event, program_led)
    assert pkt[:4] == b"TUR5"


def test_packet_version(keys_dir, program_led, sample_event):
    b = PacketBuilder(keys_dir=keys_dir)
    pkt = b.build_from_event(sample_event, program_led)
    version = int.from_bytes(pkt[4:6], "big")
    assert version == 1


def test_packet_pubkey_matches(keys_dir, program_led, sample_event):
    b = PacketBuilder(keys_dir=keys_dir)
    pkt = b.build_from_event(sample_event, program_led)
    assert pkt[8] == 33                       # длина
    assert pkt[9:42] == b.executor_pubkey     # ключ


def test_packet_deterministic_size(keys_dir, program_led, sample_event):
    """Размер пакета стабилен ±1 байт (RSA-OAEP длина фиксирована, expires меняется)."""
    b = PacketBuilder(keys_dir=keys_dir)
    p1 = b.build_from_event(sample_event, program_led)
    p2 = b.build_from_event(sample_event, program_led)
    assert abs(len(p1) - len(p2)) <= 1