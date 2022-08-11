import platform
import subprocess
import threading
from ipaddress import ip_address

result = {
        'Reachable': '',
        'Unreachable': '',
}


def check_ip(val):
    try:
        ip = ip_address(val)
    except ValueError:
        raise Exception('Incorrect IP-address')
    return ip


def ping(ip, processed_ip, get_list):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, '1', '-w', '1', str(ip)]
    response = subprocess.Popen(args, stdout=subprocess.PIPE)

    if response.wait() == 0:
        processed_ip['Reachable'] += f'{ip}\n'
        res_str = f'{ip} is reachable node'

        if not get_list:
            print(res_str)

        return res_str

    else:
        processed_ip['Unreachable'] += f'{ip}\n'
        res_str = f'{ip} is unreachable node'

        if not get_list:
            print(res_str)

        return res_str


def host_ping(nodes, get_list=False):
    threads = []
    for node in nodes:
        try:
            ip = check_ip(node)
        except Exception as e:
            print(f'{node}: {e} is perceived as a domain name')
            ip = node

        thread = threading.Thread(target=ping, args=(ip, result, get_list), daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if get_list:
        return result


if __name__ == '__main__':
    hosts = ['1.1.1.1', '8.8.8.8', '192.168.1.1', '127.0.0.1', 'gb.ru', 'bad.address']
    host_ping(hosts)
