import requests
from myproject import db, state
from myproject.models import User, Actor, Movie, BlogPost
from flask_login import login_user, current_user, logout_user, login_required
from flask import (render_template, redirect, url_for, request, Blueprint, abort,
                   flash, jsonify, make_response, session as login_session)

blogPosts = Blueprint('blogPosts', __name__, template_folder='templates/blogPosts')
