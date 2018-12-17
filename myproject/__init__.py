import os
import random
import string
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# for blueprints registration
from myproject.users.views import users
from myproject.actors.views import actors
from myproject.movies.views import movies

# ---pseudo random string used as secret key and anti forgery state token------
state = ''.join(random.choice(string.ascii_uppercase + string.digits) for
                x in range(32))
# --------------------------setup flask app------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = state

# --------------------------setup database------------------------------------
# Creating the full file path regardless of your OS (linux, windows or mac)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
app.config['SQLALCHEMY_DATABASE_URI'] += os.path.join(basedir,
                                                      'movieactors.db')
# This will avoid some warnings to be printed out
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

# ----------------------------setup login------------------------------------
login_manager = LoginManager(app)
# Tell users what view to go to when they need to login.
login_manager.login_view = 'users.login'

# --------------------------register blueprints------------------------------
app.register_blueprint(users, url_prefix="/user")
app.register_blueprint(actors, url_prefix="/actor")
app.register_blueprint(movies, url_prefix="/movie")
