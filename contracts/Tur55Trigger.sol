// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * Tur55Trigger — контракт-триггер для стандарта TUR55 v1.0 (раздел 3.1).
 *
 * Соответствует событию ExecutorTriggered строго по стандарту:
 *   address indexed userWallet
 *   uint256         amount
 *   uint256         expires
 *   bytes32         deviceId
 *   bytes           metadata
 *
 * Поле custom_data в событии ОТСУТСТВУЕТ (стандарт его не определяет).
 * Прикладные данные (duration_sec и т.п.) берутся из программы
 * inputfiles/example_led.json на стороне Executor (PacketBuilder).
 *
 * Контракт stateless: единственная задача — принять оплату (msg.value)
 * и сгенерировать событие ExecutorTriggered.
 */
contract Tur55Trigger {

    event ExecutorTriggered(
        address indexed userWallet,
        uint256 amount,
        uint256 expires,
        bytes32 deviceId,
        bytes   metadata
    );

    /**
     * @notice Сгенерировать событие TUR55 для исполнения на устройстве.
     * @param expires   Unix timestamp, после которого пакет невалиден
     * @param deviceId  Идентификатор устройства, ровно 32 байта (например "esp32_001")
     * @param metadata  JSON-строка в bytes (например '{"nonce":1,"source":"evm"}')
     *
     * amount    = msg.value   — оплата (в wei)
     * userWallet = msg.sender — инициатор
     */
    function trigger(
        uint256 expires,
        bytes32 deviceId,
        bytes calldata metadata
    ) external payable {
        emit ExecutorTriggered(
            msg.sender,
            msg.value,
            expires,
            deviceId,
            metadata
        );
    }
}