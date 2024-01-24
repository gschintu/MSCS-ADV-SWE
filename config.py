""" A configuration File """

from os import (
    urandom,
    getenv,
    path
)

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """ A Configuration Class Object """

    # OAuth Configuration
    GOOGLE_CLIENT_SECRET    = getenv("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_CLIENT_ID        = getenv("GOOGLE_CLIENT_ID", None)
    DISCOVERY_URL           = getenv("DISCOVERY_URL")

    # SQL Configuration
    SQLALCHEMY_DATABASE_URI         = getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS  = getenv("SQLALCHEMY_TRACK_MODIFICATIONS")

    # Development Environment Configuration
    SECRET_KEY      = urandom(24)
    FLASK_DEBUG     = getenv('FLASK_DEBUG')
    if FLASK_DEBUG:
        DEBUGGING   = True
    else:
        DEBUGGING   = False
