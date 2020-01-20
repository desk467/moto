'''
webservice.py

Plugin responsável por enviar requisições para um webservice
e informar se o retorno dele é positivo ou não

'''

__author__ = 'Ricardo Gomes'


import requests
import jinja2
import json


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


def webservice(routes, request_from_server, logger, ssh_connections):
    port_pattern = routes.get('port')
    host = routes.get('host')
    url = routes.get('route')
    template = jinja2.Template(url)

    def create_do_local_request(connection):
        def do_local_request(url):
            stdin, stdout, stderr = connection.exec_command(f'curl {url}')

            return json.loads(stdout.read())
        return do_local_request

    for connection in ssh_connections:
        if request_from_server:
            do_request = create_do_local_request(connection)
        else:
            do_request = getattr(requests, routes.get('method', 'get').lower())

        for port in get_active_ports(host, port_pattern, connection):
            webservice_url = f'{host}:{port}'
            url_to_request = template.render(webservice_url=webservice_url)

            try:
                response = do_request(url_to_request)
                logger.debug(response)
            except:
                return False

    return True
