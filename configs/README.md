# configs/

Тонкие настройки Executor.

## Файлы

- `settings.example.json` — **шаблон** (в git)
- `settings.json` — **реальные** настройки (в `.gitignore`, секретные)

## Что настраивается

| Секция | Что |
|---|---|
| `executor` | Имя, версия, `device_id` |
| `event` | Блокчейн, RPC, контракт, событие |
| `delivery` | Транспорт (MQTT / файл), брокер, топик |
| `keys` | Пути к ключам (ESP32 public, executor private) |

## Пример

См. `settings.example.json`.