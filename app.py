"""This is the main file to be called to start the web server.
   We split 'app' into a set of blueprints: users, actors, movies and blogposts
   This is ideal for larger applications, for more details visit
   http://flask.pocoo.org/docs/1.0/blueprints/
"""
from myproject import app
from myproject.models import Actor
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import current_user

@app.route('/')
def index():
    """This is the main endpoint that render the home page along with all
       actors. Instead of displaying all actors in the same page, we use the
       paginate method in order to display just 5 actors per page.
    """
    page = request.args.get('page', 1, type=int)
    actors = Actor.query.order_by(Actor.added_on.desc()).paginate(page=page,
                                                                  per_page=5)
    return render_template('home.html', actors=actors)

@app.route('/json')
def show_json():
    """This view will display a json object containing all actors added with
        theirs movies
    """
    actors = Actor.query.all()
    return jsonify(actors=[a.serialize for a in actors])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
