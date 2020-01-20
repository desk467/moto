import yaml
import plugins
import paramiko
import sys
import logging
from collections import defaultdict


def get_logger(nome):
    '''
    Responsável por retornar uma instância de um logger
    '''

    logger = logging.getLogger('logger_' + nome)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)-10s [%(levelname)-4s] - %(message)-14s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)

    return logger


def load_hosts():
    def generate_section_hosts_pair():
        with open('hosts.yml', 'r') as hosts_file:
            hosts_dict = yaml.load(hosts_file.read(), Loader=yaml.SafeLoader)

            for section, hosts in hosts_dict.items():
                for host in hosts:
                    yield (section, host)

    hosts = defaultdict(list)

    for section, host in generate_section_hosts_pair():
        hosts[section].append(host)
        hosts[host].append(section)

    return hosts


def load_services():
    with open('services.yml', 'r') as services_file:
        services_dict = yaml.load(services_file.read(), Loader=yaml.SafeLoader)

        return services_dict


def connect_ssh(hosts, user):
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for host in hosts:
        ssh_client.connect(host, username=user,
                           look_for_keys=True, timeout=5000)
        yield ssh_client

        ssh_client.close()


def run_tests():
    logger = get_logger('test')

    all_hosts = load_hosts()
    all_services = load_services()

    for service in all_services:
        hosts_to_execute = service.get('hosts')
        user_to_execute = service.get('user')

        hosts = all_hosts.get(hosts_to_execute)

        all_test_results = {}

        for plugin_attrs in service.get('plugins', []):
            plugin_name = plugin_attrs.get('name')
            plugin_args = {key: val for key,
                           val in plugin_attrs.items() if key != 'name'}

            plugin_args['logger'] = logger
            plugin_args['ssh_connections'] = connect_ssh(
                hosts, user_to_execute)

            plugin_func = getattr(plugins, plugin_name)

            is_test_passed = plugin_func(**plugin_args)

            all_test_results[plugin_name] = is_test_passed

            if is_test_passed:
                logger.info(
                    f'Teste do plugin "{plugin_name}" passou')
            else:
                logger.info(
                    f'Teste do plugin "{plugin_name}" não passou')

        if all(all_test_results.values()):
            logger.info('Todos os testes passaram.')
        else:
            logger.info('Os testes a seguir falharam:')

            for plugin_name, is_test_passed in all_test_results.items():
                if not is_test_passed:
                    logger.info(f'\t{plugin_name}')


if __name__ == '__main__':
    run_tests()
