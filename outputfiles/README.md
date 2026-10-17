# outputfiles/
Зашифрованные пакеты TUR55 (`program.enc`).
Используются для \*\*физической доставки\*\* (флешка / USB) на ESP32,
если нет сети (MQTT/HTTP).

## Формат
`program\_<command\_id>.enc` — бинарный пакет TUR55.

## Не коммитить
`outputfiles/\*.enc` — в `.gitignore` (пакеты секретные).

