"""
Flask extension instances, initialised in the app factory to avoid circular
imports.  Import from here rather than from individual blueprint files.
"""

from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

mongo = PyMongo()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()
