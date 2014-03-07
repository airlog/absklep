
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

__version__ = "0.1.0"
__envvar__ = "ABSKLEP_SETTINGS"

def load_config(a):
    """
    Loading application configuration from environment variable or, if not set, from config file
    distributed with this module.
    
    :param a:   flask's application object
    """
    a.config.from_object("{}.config".format(__name__))    # default settings
    try: a.config.from_envvar(__envvar__)                 # override defaults
    except RuntimeError: pass

app = Flask(__name__)
db  = SQLAlchemy(app)

load_config(app)

# dummy function to see if everything set up correctly
@app.route("/")
def hello_world():
    return """
            <div style="text-align: center;">
                <h1>Hello world</h1>
                <span style="font-size: 24px;">get ready for <b>absklep</b>!</span>
            </div>
        """

