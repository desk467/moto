from flask import Blueprint, render_template
from util import get_logger
from env import load_hosts, load_services

logger = get_logger(__name__)


frontend = Blueprint('frontend', __name__,
                     template_folder='templates', static_folder='static', url_prefix='/')


@frontend.route('/')
def index():
    hosts = load_hosts('hosts.yml')
    services = [
        {
            'name': service.get('name'),
            'hosts': hosts.get(service.get('name')),
        } for service in load_services('services.yml')
    ]

    return render_template('index.html', services=services)
