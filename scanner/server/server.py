import logging
import asyncio

import websockets
from websockets import WebSocketServerProtocol


logger = logging.getLogger('scanner.server')
logger_handler = logging.StreamHandler()
logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s > %(message)s'))
logger.setLevel(logging.INFO)
logger.addHandler(logger_handler)


class Server:
    def __init__(self, port: int, host: str = 'localhost'):
        """
        Сервер использует подключение по протоколу WS.

        Для инициализации требуется хост и номер порта, по которым будут подключаться клиенты.
        :param port:
        :param host:
        """
        self.port: int = port
        self.host: str = host
        self._connections: list = []
        self._messages: list = []

    async def _connect(self, websocket: WebSocketServerProtocol) -> None:
        if websocket not in self._connections:
            self._connections.append(websocket)
            logger.info(f'Подключён клиент {websocket.remote_address[0]}:{websocket.remote_address[1]}.')

    async def _disconnect(self, websocket: WebSocketServerProtocol) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)
            logger.info(f'Отключён клиент {websocket.remote_address[0]}:{websocket.remote_address[1]}.')

    async def _server_handler(self, websocket: WebSocketServerProtocol, path: str) -> None:
        # Добавление сокета при каждом подключении нового клиента.
        await self._connect(websocket)

        while True:
            # Регулярно проверяем, жив ли сокет.
            # Если нет, то удаляем подключение из списка _connections.
            if websocket.closed:
                await self._disconnect(websocket)
            await asyncio.sleep(.1)

    async def run_server(self) -> None:
        """
        Запуск сервера с использование хандлера _server_handler.
        :return:
        """
        await websockets.serve(self._server_handler, self.host, self.port)

    async def send_message(self, message: str) -> None:
        """
        Метод для отправки сообщений всем клиентам сразу.
        :param message:
        :return:
        """
        if self._connections:
            await asyncio.wait([client.send(message) for client in self._connections])
            logger.info(f'Было разослано сообщение "{message}".')
