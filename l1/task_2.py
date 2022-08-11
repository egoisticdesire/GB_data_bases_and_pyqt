from task_1 import check_ip, host_ping


def host_range_ping(get_list=False):
    while True:
        ip = input('Enter IP-address: ')
        try:
            ip_start = check_ip(ip)
            last_oct = int(ip.split('.')[3])
            break
        except Exception as e:
            print(e)

    while True:
        ip_count = input('How many IP-addresses to check: ')
        if not ip_count.isnumeric():
            print('Enter a number, please!')
        else:
            if (last_oct + int(ip_count)) > 256:
                print(f'Only the last octet can be changed.\n'
                      f'{256 - last_oct} is a maximum number of hosts\n')
            else:
                break

    host_list = []
    [host_list.append(str(ip_start + ip)) for ip in range(int(ip_count))]
    if not get_list:
        host_ping(host_list)
    else:
        return host_ping(host_list, True)


if __name__ == '__main__':
    host_range_ping()
