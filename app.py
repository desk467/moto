import yaml
import plugins
import paramiko
import sys
import logging
import coloredlogs

from collections import defaultdict


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    logger.addHandler(stdout_handler)

    return logger


def load_hosts(filepath):
    def generate_section_hosts_pair():
        with open(filepath, 'r') as hosts_file:
            hosts_dict = yaml.load(hosts_file.read(), Loader=yaml.SafeLoader)

            for section, hosts in hosts_dict.items():
                for host in hosts:
                    yield (section, host)

    hosts = defaultdict(list)

    for section, host in generate_section_hosts_pair():
        hosts[section].append(host)
        hosts[host].append(section)

    return hosts


def load_services(filepath):
    with open(filepath, 'r') as services_file:
        return yaml.load(services_file.read(), Loader=yaml.SafeLoader)


def connect_ssh(hosts, user):
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for host in hosts:
        ssh_client.connect(host, username=user,
                           look_for_keys=True, timeout=5000)
        yield host, ssh_client

        ssh_client.close()


def get_plugin_name(attrs):
    return [key for key in attrs.keys() if key != 'name'][0]


def run_tests(hosts_filepath='hosts.yml', services_filepath='services.yml'):
    logger = get_logger('test_runner')

    coloredlogs.install(logger=logger)

    logger.info('Test runner started')

    all_hosts = load_hosts(hosts_filepath)
    all_services = load_services(services_filepath)

    for service in all_services:
        hosts_to_execute = service.get('hosts')
        user_to_execute = service.get('user')

        hosts = all_hosts.get(hosts_to_execute)

        all_test_results = {}

        for test_attrs in service.get('tests', []):
            test_name = test_attrs.get('name')
            test_plugin = get_plugin_name(test_attrs)
            test_plugin_args = test_attrs.get(test_plugin)

            test_plugin_args['logger'] = logger
            test_plugin_args['ssh_connections'] = connect_ssh(
                hosts, user_to_execute)

            plugin_func = getattr(plugins, test_plugin)

            is_test_passed, extradata = plugin_func(**test_plugin_args)

            all_test_results[test_name] = is_test_passed

            if is_test_passed:
                logger.info(
                    f'Task "{test_name}" passed')
            else:
                logger.error(
                    f'Task "{test_name}" did not pass')

        logger.info('Test runner done all tests')
        logger.info('** Summary **')

        if all(all_test_results.values()):
            logger.info('All tests PASSED.')
        else:
            logger.info('The following tests have FAILED')

            for test_name, is_test_passed in all_test_results.items():
                if not is_test_passed:
                    logger.info(f'\t{test_name}')


if __name__ == '__main__':
    run_tests()
