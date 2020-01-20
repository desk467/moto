'''
systemd.py

Plugin responsável por verificar em um servidor
se um serviço está ativo.

'''

__author__ = 'Ricardo Gomes'


def systemd(service_name, logger, ssh_connections):
    logger.debug(f'Verificando a execução do serviço "{service_name}"')

    for connection in ssh_connections:
        stdin, stdout, stderr = connection.exec_command(
            f'systemctl is-active {service_name}')

        for line in stdout:
            if line.strip('\n') != 'active':
                return False

        return True
