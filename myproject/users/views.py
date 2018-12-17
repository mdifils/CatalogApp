import os
import requests
from myproject import db, state
from myproject.models import User, Actor, Movie, BlogPost
from flask_login import login_user, current_user, logout_user, login_required
from flask import (render_template, redirect, url_for, request, Blueprint,
                   flash, jsonify, make_response, session as login_session,
                   abort)
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

users = Blueprint('users', __name__,
                  template_folder='templates/users',
                  static_folder='static')

basedir = os.path.abspath(os.path.dirname(__file__))
# YOU HAVE TO PUT YOUR 'client_secrets.json' FILE YOU DOWNLOADED AFTER
# REGISTERING YOUR APP at https://console.cloud.google.com/apis/credential
# Put it the same directory than this views.py (myproject/users)
client_secrets = os.path.join(basedir, 'client_secrets.json')


def respond(message, status):
    """Make a flask response for handling errors"""
    response = make_response(json.dumps(message), status)
    response.headers['Content-Type'] = 'application/json'
    print("response: {}".format(repr(response)))
    return response


@users.route('/login', methods=['GET', 'POST'])
def login():
    """This view render the login page if the method is GET """
    if request.method == 'POST':
        # Grab the user from our User Model table
        user = User.query.filter_by(email=request.form['email']).first()
        # check if the user exits and matches the password
        if user and user.check_password(request.form['password']):
            login_user(user)
            flash(f"You successfully logged in as {current_user.username}!")
            return redirect(url_for('index'))

    login_session['state'] = state
    return render_template('login.html', STATE=state)


@users.route('/register', methods=['GET', 'POST'])
def register():
    """This view render the registration page if the method is GET """
    if request.method == 'POST':
        # Record the user in the our User Model table
        user = User(email=request.form['email'],
                    username=request.form['username'])
        user.hash_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')

        return redirect(url_for('users.login'))

    return render_template('register.html')


@users.route('/fblogin', methods=['POST'])
def fblogin():
    """This view handle the authentication and authorization with facebook"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        return respond('Invalid state parameter.', 401)

    token = request.data.decode()

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    params = {"access_token": token, "fields": "name,id,email"}
    resp = requests.get(userinfo_url, params=params)

    assert resp.ok, resp.text
    facebook_info = resp.json()
    user = User.query.filter_by(email=facebook_info['email']).first()

    if not user:
        user = User(email=facebook_info['email'],
                    username=facebook_info['name'],
                    token=token,
                    provider='facebook',
                    provider_id=facebook_info['id'])
        db.session.add(user)
        db.session.commit()

    else:
        user.token = token
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(f"you are now logged in as {current_user.username}")

    return redirect(url_for('index'))


@users.route('/glogin', methods=['POST'])
def glogin():
    """This view handle the authentication and authorization with google"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        return respond('Invalid state parameter.', 401)
    # Obtain authorization code
    code = request.data
    print(f'code: {code}')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(client_secrets, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        return respond('Failed to upgrade the authorization code.', 401)

    # Check that the access token is valid.
    tokeninfo_url = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    resp = requests.get(tokeninfo_url, params=params)

    assert resp.ok, resp.text

    result = resp.json()
    # Verify that the access token is used for the intended user.
    if result['sub'] != credentials.id_token['sub']:
        return respond("Token's user ID doesn't match given user ID.", 401)

    # Verify that the access token is valid for this app.
    if result['azp'] != credentials.id_token['azp']:
        return respond("Token's client ID does not match app's.", 401)

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    resp = requests.get(userinfo_url, params=params)

    assert resp.ok, resp.text
    data = resp.json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user:
        user = User(email=data['email'],
                    username=data['name'],
                    token=credentials.access_token,
                    provider='google',
                    provider_id=result['azp'])
        db.session.add(user)
        db.session.commit()

    else:
        user.token = credentials.access_token
        db.session.add(user)
        db.session.commit()

    login_user(user)

    flash(f"you are now logged in as {current_user.username}")

    return redirect(url_for('index'))


@users.route('/logout')
@login_required
def logout():
    """This view checks first if the user was authenticated via oauth2 or not
    """
    if current_user.provider:
        # check which provider it is then revoke the token
        if current_user.provider == 'google':
            revoke_url = 'https://accounts.google.com/o/oauth2/revoke'
            params = {'token': current_user.token, 'alt': 'json'}
            # headers = {'content-type': 'application/x-www-form-urlencoded'}
            resp = requests.post(revoke_url, params=params)

            if resp.status_code == 200:
                logout_user()
                flash("You successfully logged out!")
            else:
                flash('An error occurred.')
            return redirect(url_for('index'))
        elif current_user.provider == 'facebook':
            facebook_id = current_user.provider_id
            revoke_url = f'https://graph.facebook.com/{facebook_id}/'
            revoke_url += 'permissions?'
            params = {'access_token': current_user.token, 'alt': 'json'}
            # headers = {'content-type': 'application/x-www-form-urlencoded'}
            resp = requests.delete(revoke_url, params=params)

            if resp.status_code == 200:
                logout_user()
                flash("You successfully logged out!")
            else:
                flash('An error occurred.')
            return redirect(url_for('index'))
    else:
        logout_user()
        flash("You have logged out")
        return redirect(url_for("index"))
