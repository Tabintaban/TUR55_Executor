"""Встраивание JSON-конверта TUR55 в Python-скрипт для ESP32.

Маркер по умолчанию: `# @@TUR55_PAYLOAD@@`.
После вставки в скрипте появляется переменная `TUR55_PAYLOAD` — dict
с данными события `ExecutorTriggered`:

    user_wallet : str
    amount      : int
    expires     : int
    device_id   : str
    metadata    : dict   — служебное (nonce, source, event_index)
    custom_data : dict   — прикладное (например, duration_sec)

Публичный API:
    build_script(template_text, payload, marker=DEFAULT_MARKER) -> str

Исключения:
    ValueError — маркер не найден, встречается больше одного раза,
                 или результат не является валидным Python-кодом.
"""

from __future__ import annotations

import json
from typing import Any


DEFAULT_MARKER = "# @@TUR55_PAYLOAD@@"
PAYLOAD_VAR = "TUR55_PAYLOAD"


def build_script(
    template_text: str,
    payload: dict[str, Any],
    marker: str = DEFAULT_MARKER,
) -> str:
    """Встроить payload в template_text вместо маркера.

    Возвращает готовый Python-скрипт (str).
    """
    count = template_text.count(marker)
    if count == 0:
        raise ValueError(
            f"Маркер {marker!r} не найден в шаблоне. "
            f"Добавьте его в скрипт в место, куда нужно встроить данные."
        )
    if count > 1:
        raise ValueError(
            f"Маркер {marker!r} встречается {count} раз — должно быть ровно один. "
            f"Уберите лишние вхождения."
        )

    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    assignment = f"{PAYLOAD_VAR} = {payload_json}"

    script = template_text.replace(marker, assignment)

    # Проверка, что получился валидный Python.
    try:
        compile(script, "<generated>", "exec")
    except SyntaxError as e:
        raise ValueError(
            f"После вставки payload скрипт не является валидным Python: {e}. "
            f"Скорее всего, маркер {marker!r} стоит внутри строки или комментария. "
            f"Перенесите маркер в отдельную строку."
        ) from e

    return script