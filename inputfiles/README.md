# inputfiles/

Программы для ESP32 (формат TUR55, раздел 3.2).

## Формат

**JSON**, а не `.py`. Структура:

```json
{
  "setup": [
    "led = machine.Pin(2, machine.Pin.OUT)",
    "led.value(0)"
  ],
  "loop_logic": [
    "led.value(1)",
    "time.sleep(0.5)",
    "led.value(0)",
    "time.sleep(0.5)"
  ],
  "custom_data": {
    "duration_sec": 120
  }
}
```

| Поле | Что | Тип |
|------|-----|-----|
| `setup` | код инициализации (выполняется один раз) | `list[str]` |
| `loop_logic` | код цикла (выполняется многократно) | `list[str]` |
| `custom_data` | параметры (перекрываются данными из события) | `dict` |

## Почему JSON, а не `.py`

ESP32 (`execution_engine`) **не исполняет `.py`-файл**. ESP32 склеивает `setup` + `loop_logic` в строку и выполняет через `exec()` **в песочнице**.

`.py` — **не принимается** ESP32. `example_led.py` — оставлен как **пример** (для чтения), но **не используется**.

## Примеры

- `example_led.json` — мигающая лампочка на 120 секунд (рабочий).
- `example_led.py` — тот же код в виде `.py` (человекочитаемый, не используется).

## Как добавить новую программу

1. Создать `inputfiles/<имя>.json`.
2. Заполнить `setup`, `loop_logic`, `custom_data`.
3. В `configs/ethereum.json` → `"inputfiles": {"template": "inputfiles/<имя>.json"}`.
4. `py main.py build` → пакет → ESP32.

## Будущее

Конвертер `.py` → `.json` — позже (сложно, хрупко). Пока — **вручную**.

