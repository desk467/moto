import yaml
import plugins
import paramiko
import sys

from collections import defaultdict

from env import load_hosts, load_services
from util import get_logger


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


def run_tests(hosts_filepath='hosts.yml', services_filepath='services.yml', service_name=None):
    logger = get_logger('test_runner')

    logger.info('Test runner started')

    all_hosts = load_hosts(hosts_filepath)
    all_services = load_services(services_filepath)

    test_summary = {}

    if service_name:
        all_services = (service for service in all_services if service.get(
            'name') == service_name)

    for service in all_services:
        hosts_to_execute = service.get('hosts')
        user_to_execute = service.get('user')

        logger.info(f'[{service.get("name")}] Starting test suite')

        hosts = all_hosts.get(hosts_to_execute)

        service_test_summary = {}

        for test_attrs in service.get('tests', []):
            test_name = test_attrs.get('name')
            test_plugin = get_plugin_name(test_attrs)
            test_plugin_args = test_attrs.get(test_plugin)

            test_plugin_args['logger'] = logger
            test_plugin_args['ssh_connections'] = connect_ssh(
                hosts, user_to_execute)

            plugin_func = getattr(plugins, test_plugin)

            is_test_passed, extradata = plugin_func(**test_plugin_args)

            service_test_summary[test_name] = {
                "is_test_passed": is_test_passed,
                "extradata": extradata,
            }

            if is_test_passed:
                logger.info(
                    f'[{service.get("name")}] Test "{test_name}" passed')
            else:
                logger.error(
                    f'[{service.get("name")}] Test "{test_name}" did not pass')

        logger.info(f'[{service.get("name")}] Test suit finished')

        test_summary[service.get('name')] = service_test_summary
        service_test_summary = {}

    logger.info('Done all tests.')

    return test_summary


if __name__ == '__main__':
    run_tests()
