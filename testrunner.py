import yaml
import plugins
import paramiko
import sys
import asyncio
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor

from collections import defaultdict

from env import load_hosts, load_services
from util import get_logger
import exceptions


logger = get_logger('testrunner')


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


def run_test_for_service(service, hosts, test_attrs):
    test_name = test_attrs.get('name')
    test_plugin = get_plugin_name(test_attrs)
    test_plugin_args = test_attrs.get(test_plugin)

    service_name = service.get('name')
    user_to_execute = service.get('user')

    test_plugin_args['ssh_connections'] = connect_ssh(hosts, user_to_execute)

    plugin_func = getattr(plugins, test_plugin)

    is_test_passed, extradata = plugin_func(**test_plugin_args)

    if is_test_passed:
        logger.info(
            f'[{service_name}] Test "{test_name}" passed')
    else:
        logger.error(
            f'[{service_name}] Test "{test_name}" did not pass')

    return test_name, is_test_passed, extradata


async def run_all_tests_for_service(user, hosts, service):
    service_name = service.get('name')
    hosts_to_execute = service.get('hosts')

    logger.info(f'[{service.get("name")}] Starting test suite')

    service_test_summary = {}

    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        loop = asyncio.get_event_loop()

        futures = [loop.run_in_executor(
            executor, run_test_for_service, service, hosts, test_attrs) for test_attrs in service.get('tests', [])]

        for test_name, is_test_passed, extradata in await asyncio.gather(*futures):
            service_test_summary[test_name] = {
                'is_test_passed': is_test_passed,
                'extradata': extradata,
            }

    logger.info(f'[{service.get("name")}] Test suit finished')

    return service_name, service_test_summary


def get_hosts_for_service(hosts_filepath, service):
    all_hosts = load_hosts(hosts_filepath)

    return all_hosts.get(service.get('name'))


async def run_all_tests(hosts_filepath='hosts.yml', services_filepath='services.yml', service_name=None):
    logger.info('Test runner started')

    all_services = load_services(services_filepath)

    test_summary = {}

    if service_name:
        all_services = [service for service in all_services if service.get(
            'name') == service_name]

        if no_services_found := len(all_services) == 0:
            logger.error(f'Service "{service_name}" not found.')
            raise exceptions.ServiceNotFound(service_name)

    loop = asyncio.get_event_loop()

    for service in all_services:
        hosts = get_hosts_for_service(hosts_filepath, service)

        service_name, test_results = await run_all_tests_for_service(service.get('user'), hosts, service)

        test_summary[service_name] = test_results

    logger.info('Done all tests.')

    return test_summary


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.run_until_complete(run_all_tests())