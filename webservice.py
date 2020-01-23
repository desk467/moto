from flask import Flask, jsonify

from util import get_logger
from env import load_hosts, load_services
from testrunner import run_tests

logger = get_logger('webservice')


app = Flask(__name__)

@app.route('/status')
@app.route('/status/<service_name>')
def get_status(service_name=None):
    test_results = run_tests(service_name=service_name)

    return jsonify(test_results)


@app.route('/services')
def get_service_names():
    hosts = load_hosts('hosts.yml')
    return jsonify([
        {
            'name': service.get('name'),
            'hosts': hosts.get(service.get('name')),
        } for service in load_services('services.yml')
    ])


if __name__ == '__main__':
    app.run(port=3000)
