import sys
import os
import asyncio
import logging

from server.server import Server


class Scanner:
    def __init__(self, path: str, port: int):
        self.path = path
        self.server = Server(port)

    async def _send_message(self, message: str) -> None:
        await self.server.send_message(message)

    @staticmethod
    def _get_files_dict(path: str) -> dict:
        # Получаем словарь по схеме "путь":"последнее время изменения"
        result = {
            root + os.sep + file: os.stat(root + os.sep + file).st_mtime
            for root, dirs, files in os.walk(path)
            for file in files
        }
        return result

    async def _run_scanning(self) -> None:
        await self._send_message(
            'Запущен процесс сканирования директории ' + self.path
        )
        old_dict = self._get_files_dict(self.path)
        while True:
            new_dict = self._get_files_dict(self.path)

            for file in new_dict:
                if old_dict.get(file) is None:
                    # Если в старом словаре файл найден не был,
                    # значит этот файл был только что создан.
                    await self._send_message('Был создан файл ' + file)
                elif old_dict[file] != new_dict[file]:
                    # Проверка времени последнего изменения.
                    # Если значения не идентичны, значит произошла модификация.
                    await self._send_message('Был модифицирован файл ' + file)

            # Отдельно производится проверка на удаление файлов.
            for file in old_dict:
                if file not in new_dict:
                    await self._send_message('Был удалён файл ' + file)

            # Переопределение переменной старго словаря.
            old_dict = new_dict
            await asyncio.sleep(.1)

    async def _run(self) -> None:
        # Одновременно запусаем и сервер, и сканнер.
        await asyncio.gather(self._run_scanning(), self.server.run_server())

    def run(self) -> None:
        print('Старт сканирования.')
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            print('Сканирование прервано.')


def direct_run() -> None:
    try:
        # Для успешной работы необходимо добавить в качестве единственного
        # аргумента путь целевой директории.
        path = sys.argv[1]
        port = int(sys.argv[2])
    except IndexError:
        print('Необходимо добаить путь до сканируемой папки первым аргументом'
              'и порт - вторым.')
    else:
        scanner = Scanner(path, port)
        scanner.run()


if __name__ == '__main__':
    direct_run()
