'''
webservice.py

Plugin responsável por enviar requisições para um webservice
e informar se o retorno dele é positivo ou não

'''

__author__ = 'Ricardo Gomes'


import requests
import jinja2
import json

from moto.logging import get_logger

logger = get_logger('webservice')


def parse_curl_response(http_response):
    dict_response = {}

    first_line = True
    for line in reversed(http_response):
        if first_line:
            first_line = False
            dict_response['data'] = json.loads(line)
        elif 'HTTP' in line:
            dict_response['status'] = int(line.split(' ')[1])
        elif len(line):
            key, val = line.split(':', 1)
            dict_response[key] = val

    return dict_response


def generate_port_range(port_pattern):
    for i in range(10):
        port = port_pattern.replace('x', str(i), 1)

        if 'x' in port:
            for another_port in generate_port_range(port):
                yield another_port
        else:
            yield port


def get_active_ports(host, port_pattern, connection):
    for port in generate_port_range(port_pattern):
        session = connection.get_transport().open_session()
        session.exec_command(f'nc -w 5 -z {host} {port}')
        exit_status = session.recv_exit_status()

        if exit_status == 0:
            yield port
        else:
            break


def create_do_local_request(connection):
    def do_local_request(url):
        stdin, stdout, stderr = connection.exec_command(f'curl -i {url}')

        raw_response = stdout.read().decode().split('\n')
        raw_response = [line.strip('\r') for line in raw_response]
        dict_response = parse_curl_response(raw_response)

        return {
            'is_response_ok': dict_response.get('status', 500) >= 200 and dict_response.get('status') < 300,
            'http_code': dict_response.get('status', 500),
            'data': dict_response.get('data', {})
        }

    return do_local_request


def create_do_remote_request():
    def do_remote_request(url):
        call_method = getattr(requests, routes.get('method', 'get').lower())

        response = call_method(url)

        return {
            'is_response_ok': response.ok,
            'http_code': response.status_code,
            'data': response.json(),
        }

    return do_remote_request


def webservice(routes, request_from_server, ssh_connections):
    port_pattern = routes.get('port')
    host = routes.get('host')
    url = routes.get('route')
    template = jinja2.Template(url)

    for _, connection in ssh_connections:
        if request_from_server:
            do_request = create_do_local_request(connection)
        else:
            do_request = create_do_remote_request()

        for port in get_active_ports(host, port_pattern, connection):
            webservice_url = f'{host}:{port}'
            url_to_request = template.render(webservice_url=webservice_url)

            try:
                response = do_request(url_to_request)
                logger.debug(response)
            except Exception as ex:
                return False, None

    return True, None
