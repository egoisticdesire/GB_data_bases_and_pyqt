from tabulate import tabulate
from task_2 import host_range_ping


def host_range_ping_tab():
    print(tabulate([host_range_ping(True)], headers='keys', tablefmt='fancy_grid', stralign='center'))


if __name__ == '__main__':
    host_range_ping_tab()
