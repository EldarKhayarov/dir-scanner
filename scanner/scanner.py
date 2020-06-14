import sys
import os
import time


class TCPSender:
    def send(self, message):
        # TODO: реализовать отправку по TCP
        # print - временное решения для дебага
        print(message)


class Scanner:
    def __init__(self, path):
        self.path = path
        self.tcp_handler = TCPSender()

    def _send_message(self, message):
        self.tcp_handler.send(message)

    @staticmethod
    def _get_files_dict(path):
        result = {
            root + os.sep + file: os.stat(root + os.sep + file).st_mtime
            for root, dirs, files in os.walk(path)
            for file in files
        }
        return result

    def run(self):
        self._send_message(
            'Запущен процесс сканирования директории ' + self.path
        )
        old_dict = self._get_files_dict(self.path)
        while True:
            new_dict = self._get_files_dict(self.path)

            for file in new_dict:
                if old_dict.get(file) is None:
                    # Если в старом словаре файл найден не был,
                    # значит этот файл был только что создан.
                    self._send_message('Был создан файл: ' + file)
                elif old_dict[file] != new_dict[file]:
                    # Проверка времени последнего изменения.
                    # Если значения не идентичны, значит произошла модификация.
                    self._send_message('Был модифицирован файл: ' + file)

            # Отдельно производится проверка на удаление файлов.
            for file in old_dict:
                if file not in new_dict:
                    self._send_message('Был удалён файл: ' + file)

            # Переопределение переменной старго словаря.
            old_dict = new_dict
            time.sleep(0.01)


def direct_run():
    try:
        # Для успешной работы необходимо добавить в качестве единственного
        # аргумента путь целевой директории.
        path = sys.argv[1]
    except IndexError:
        print('Необходимо добаить путь до сканируемой папки вторым аргументом.')
    else:
        scanner = Scanner(path)
        scanner.run()


if __name__ == '__main__':
    direct_run()
