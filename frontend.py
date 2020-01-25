from flask import Blueprint, render_template
from util import get_logger


logger = get_logger(__name__)


frontend = Blueprint('frontend', __name__,
                     template_folder='templates', static_folder='static', url_prefix='/')


@frontend.route('/')
def index():
    return render_template('index.html')
