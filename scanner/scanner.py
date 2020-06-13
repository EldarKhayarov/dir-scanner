import sys


IPS_FILE_FLAG = '-f'
IPS_LIST_FLAG = '-ips'


def get_ips_from_file(path: str):
    # TODO: Реализовать функцию чтения айпишников из файла
    pass


def get_ips_from_args():
    if IPS_FILE_FLAG in sys.argv:
        try:
            get_ips_from_file(sys.argv[sys.argv.index(IPS_FILE_FLAG) + 1])
        except IndexError:
            print('Отсутствует путь до файла с IP-адресами.')

    elif IPS_LIST_FLAG in sys.argv:
        return list([ip for ip in sys.argv[sys.argv.index(IPS_LIST_FLAG):]])
    else:
        raise KeyError('Не найдено специальных параметоров для списка ip.')


class Scanner:
    ips: list

    def __init__(self, ips, *args):
        self.ips = ips


def direct_run():
    scanner = Scanner(get_ips_from_args())


if __name__ == '__main__':
    direct_run()
