import sys
import asyncio
import socket
import logging

import websockets


IPS_FILE_FLAG = '-f'
IPS_LIST_FLAG = '-ips'

WS_PROTOCOL_PREFIX = 'ws://'


logger = logging.getLogger('client.client')
logger_handler = logging.StreamHandler()
logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s > %(message)s'))
logger.addHandler(logger_handler)
logger.setLevel(logging.INFO)


def validate_ip(string: str) -> None:
    """
    Функция проверки валидности ip.
    :param string:
    :return:
    """
    try:
        socket.inet_aton(string)
    except socket.error:
        raise ValueError('IP невалиден.')


def validate_ips(ips: list) -> None:
    """
    Функция проверки валидности списка ip.
    :param ips:
    :return:
    """
    for ip in ips:
        validate_ip(ip)


def get_ips_from_file(path: str) -> list:
    """
    Получение списка ip из файла.

    Каждый адрес разделён переносом строки.
    :param path:
    :return:
    """
    with open(path) as f:
        return list([ip for ip in f.read().split('\n')])


def get_scanner_ips() -> list:
    if IPS_FILE_FLAG in sys.argv:
        try:
            return get_ips_from_file(sys.argv[sys.argv.index(IPS_FILE_FLAG) + 1])
        except IndexError:
            print('Отсутствует путь до файла с IP-адресами.')

    elif IPS_LIST_FLAG in sys.argv:
        return list([ip for ip in sys.argv[sys.argv.index(IPS_LIST_FLAG) + 1:]])
    else:
        raise KeyError('Не найдено специальных параметоров для списка ip.')


class Client:
    def __init__(self, ips: list):
        """
        Клиент осуществляет подключение ко всем сканнерам и выводит входящие сообщения в лог.
        :param ips:
        """
        self.ips = ips

    @staticmethod
    async def _connect_to_server(ip: str) -> None:
        logger.info('Подключение к %s', ip)
        try:
            async with websockets.connect(WS_PROTOCOL_PREFIX + ip) as connection:
                # После подключения регулярно проверяем буфер
                # на наличие новых сообщений.
                while True:
                    logger.info(await connection.recv())
                    await asyncio.sleep(.1)

        except ConnectionRefusedError:
            logger.info(f'Соединение не было установлено с %s.', ip)
        except websockets.ConnectionClosedOK:
            logger.info(f'Соединение с %s было прервано.', ip)
        except websockets.ConnectionClosedError:
            logger.warning(f'Соединение с %s было прервано с ошибкой.', ip)

    async def _run(self) -> None:
        # Одновременно подключаемся ко всем сканнерам.
        await asyncio.gather(*[self._connect_to_server(ip) for ip in self.ips])

    def run(self) -> None:
        logger.info('Запуск прослушивания адресов: %s', ', '.join(self.ips))
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            print('Прервано вручную.')


def direct_run() -> None:
    try:
        ips = get_scanner_ips()
        validate_ips(ips)

        client = Client(get_scanner_ips())
    except (KeyError, ValueError) as ex:
        # Секция, срабатывающая при отлавливании исключения, вызванного во
        # время валидации адреса сервера(ов).
        print(str(ex).strip("'"))
    else:
        client.run()


if __name__ == '__main__':
    direct_run()
