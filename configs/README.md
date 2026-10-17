# configs/

Настройки TUR55_Executor.

## Файлы

| Файл | Назначение | В git |
|------|------------|-------|
| `settings.example.json` | Шаблон настроек (без секретов) | да |
| `settings.json` | Рабочие настройки (с секретами) | **нет** (`.gitignore`) |

## Как использовать

```powershell
copy configs\settings.example.json configs\settings.json
# отредактировать settings.json: rpc_url, contract_address, device_id, пути к ключам
```

## Ключевые поля

| Поле | Значения | Описание |
|------|----------|----------|
| `event.blockchain` | `ethereum` / `solana` / `tron` | Какой слушатель использовать |
| `event.use_mock` | `true` / `false` | `true` — мок-события без сети |
| `delivery.transport` | `mqtt` / `file` / `both` | Куда доставлять пакет |
| `inputfiles.template` | путь | Шаблон Python-скрипта для ESP32 |
| `inputfiles.payload_marker` | строка | Маркер, куда встраивается конверт |

## Безопасность

- `settings.json` **никогда** не коммитится (см. `.gitignore`).
- Ключи (`keys/*.pem`) — тоже вне git.
- `settings.example.json` содержит только плейсхолдеры (`YOUR_KEY`, `0x0000...`).
