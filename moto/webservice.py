from flask import Blueprint, jsonify, request

from moto import exceptions
from moto.logging import get_logger
from moto.env import load_hosts, load_services
from moto.testrunner import run_all_tests
from moto.cache import CacheDict

import asyncio

logger = get_logger(__name__)

cache = CacheDict()
webservice = Blueprint('webservice', __name__, url_prefix='/api')


def run_tests_and_cache(service_name=None):
    loop = asyncio.new_event_loop()

    test_results = loop.run_until_complete(
        run_all_tests(service_name=service_name))

    cache[service_name] = test_results

    return jsonify({**test_results, 'cached': False})


@webservice.route('/status')
@webservice.route('/status/<service_name>')
def get_status(service_name=None):
    try:
        get_from_cache = request.args.get('get_from_cache') == 'true'
        logger.info('get from cache: %s' % (get_from_cache))

        if get_from_cache:
            return jsonify({**cache[service_name], 'cached': True})
        else:
            return run_tests_and_cache(service_name)
    except KeyError:
        return run_tests_and_cache(service_name)
    except exceptions.ServiceNotFound:
        return jsonify({'message': 'SERVICE_NOT_FOUND', 'service_name': service_name}), 404


@webservice.route('/services')
def get_service_names():
    hosts = load_hosts('hosts.yml')
    return jsonify([
        {
            'name': service.get('name'),
            'hosts': hosts.get(service.get('name')),
        } for service in load_services('services.yml')
    ])


if __name__ == '__main__':
    webservice.run(port=3000)
