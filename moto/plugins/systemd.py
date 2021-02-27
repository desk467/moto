'''
systemd.py

Plugin responsável por verificar em um servidor
se um serviço está ativo.

'''

import locale
from datetime import datetime
from datetime import timedelta

from moto.logging import get_logger

logger = get_logger('systemd')

__author__ = 'Ricardo Gomes'


def parse_systemctl_show(info):
    info_per_service = {}

    for line in info:
        if len(line.strip('\n')) == 0:
            yield info_per_service
            info_per_service = {}
        else:
            key, val = line.strip('\n').split('=', 1)
            info_per_service[key] = val
    else:
        yield info_per_service


def generate_extradata(services_info, host):
    for service in services_info:
        yield {
            'name': service.get('Names'),
            'is_active': service.get('ActiveState') == 'active',
            'started_since': datetime.strptime(service.get('ActiveEnterTimestamp') + '00', '%a %Y-%m-%d %H:%M:%S %z'),
            'host': host
        }


def systemd(service_name, ssh_connections):
    logger.debug(f'Checking if "{service_name}" is up')

    extradata = []

    for host, connection in ssh_connections:
        stdin, stdout, stderr = connection.exec_command(
            f'systemctl show {service_name}')

        services_info = parse_systemctl_show(stdout)

        extradata = extradata + list(generate_extradata(services_info, host))

    for data in extradata:
        if not data.get('is_active'):
            return False, None

    return True, extradata
