from flask import Flask

from moto.webservice import webservice
from moto.frontend import frontend

app = Flask(__name__)

app.register_blueprint(frontend)
app.register_blueprint(webservice)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
