
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

__version__ = "0.1.0"

app = Flask(__name__)
app.db = SQLAlchemy(app)

import absklep.controllers
import absklep.models

absklep.controllers.load_config(app, package=__name__)
absklep.controllers.load_database(app)


# dummy function to see if everything set up correctly
@app.route("/")
def hello_world():
    return ("\n"
            "<div style=\"text-align: center;\">\n"
            "   <h1>Hello world</h1>\n"
            "   <span style=\"font-size: 24px;\">get ready for <b>%s</b>!</span>\n"
            " </div>\n" % __name__
            )
