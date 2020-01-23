'''

network.py

Plugin responsável por verificar se uma interface está ativa.

'''

import re
from datetime import timedelta


def parse_ping(info):
    text = info.read().decode()

    parsed_data = []
    for line in reversed(text.split('\n')):
        if 'statistics' in line:
            break
        if line:
            parsed_data.append(line)

    if len(parsed_data) == 2:
        min, avg, max, mdev = re.compile("\d+.\d+").findall(parsed_data.pop(0))
    else:
        min, avg, max, mdev = 0, 0, 0, 0

    transmitted, received, loss, time = re.compile(
        "\d+").findall(parsed_data.pop(0))

    return {
        "min": float(min),
        "avg": float(avg),
        "max": float(max),
        "mdev": float(mdev),
        "packets": {
            "transmitted": int(transmitted),
            "received": int(received),
            "loss": int(loss)/100,
            "time": timedelta(milliseconds=int(time))
        }
    }


def parse_flags(info):
    flags, _ = info.split('  ')

    translation = flags.maketrans({'<': ' ', '>': ' '})
    flags = flags.translate(translation)
    _, flags = re.compile('=\d+').split(flags)

    return flags.strip().split(',')


def parse_mtu(info):
    _, mtu = info.split('  ')
    _, mtu = mtu.split(' ')

    return int(mtu)


def parse_ifconfig_iface(info):
    first_line = True

    parsed_data = {}
    for line in info:
        if first_line:
            first_line = False

            iface, rest = line.strip('\n').split(': ')

            parsed_data['iface'] = iface
            parsed_data['flags'] = parse_flags(rest)
            parsed_data['mtu'] = parse_mtu(rest)
        else:
            line_infos = line.strip('\n').split('  ')

            for line_info in line_infos:
                if line_info and '(' not in line_info:
                    key, val = line_info.split(' ', 1)
                    parsed_data[key] = val

    return parsed_data


def network(interface, logger, ssh_connections, ping=False, ping_to=None, num_of_tries=1, packet_loss_threshold=0.0):
    all_hosts_passed = []
    extradata = []

    for host, connection in ssh_connections:
        is_test_passed = False

        stdin, stdout, stderr = connection.exec_command(
            f'ifconfig {interface}')

        ifconfig_data = parse_ifconfig_iface(stdout)

        ifconfig_test_passed = 'UP' in ifconfig_data.get('flags', [])

        stdin, stdout, stderr = connection.exec_command(
            f'ping -c{num_of_tries} {ping_to}')

        ping_data = parse_ping(stdout) if ping else {}

        ping_test_passed = ping_data.get("packets", {}).get("loss") == packet_loss_threshold

        extradata.append({
            'host': host,
            'is_test_passed': ifconfig_test_passed and ping_test_passed,
            'ifconfig': ifconfig_data,
            'ping': ping_data if ping else None,
        })

    return all(data.get('is_test_passed') for data in extradata), extradata
