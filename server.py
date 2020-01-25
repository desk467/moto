from flask import Flask

from webservice import webservice
from frontend import frontend

app = Flask(__name__)

app.register_blueprint(frontend)
app.register_blueprint(webservice)


if __name__ == '__main__':
    app.run(debug=True)
