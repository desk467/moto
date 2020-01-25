from flask import Blueprint, jsonify

import exceptions
from util import get_logger
from env import load_hosts, load_services
from testrunner import run_all_tests

import asyncio

logger = get_logger(__name__)


webservice = Blueprint('webservice', __name__, url_prefix='/api')
loop = asyncio.get_event_loop()


@webservice.route('/status')
@webservice.route('/status/<service_name>')
def get_status(service_name=None):
    try:
        test_results = loop.run_until_complete(
            run_all_tests(service_name=service_name))

        return jsonify(test_results)
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
