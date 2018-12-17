import requests
from myproject import db, state
from myproject.models import User, Actor, Movie, BlogPost
from flask_login import login_user, current_user, logout_user, login_required
from flask import (render_template, redirect, url_for, request, Blueprint, abort,
                   flash, jsonify, make_response, session as login_session)

actors = Blueprint('actors', __name__, template_folder='templates/actors')

@actors.route('/add', methods=['GET', 'POST'])
@login_required
def add_actor():
    """This view Render a page to add an actor if method is GET otherwise
       it records in the database actor's informations provided
    """
    if request.method == 'POST':
        # Record the actor in our Actor Model table
        actor = Actor(name=request.form['name'],
                      short_bio=request.form['short_bio'],
                      picture=request.form['picture'],
                      user_id=current_user.id)

        db.session.add(actor)
        db.session.commit()
        flash('Thanks for adding a new actor!')

        return redirect(url_for('index'))

    return render_template('addActor.html')

@actors.route('/<int:actor_id>')
def show_actor(actor_id):
    """Display full details about an actor"""

    # grab the requested actor by id number
    actor = Actor.query.get_or_404(actor_id)
    # grab all movies recorded for this actor.
    movies = Movie.query.filter_by(author=actor).all()
    if not movies:
        flash('No movies recorded for this actor yet.')
    return render_template('showActor.html', actor=actor, movies=movies)

@actors.route('/<int:actor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_actor(actor_id):
    """Edit actor's details"""

    # grab the requested actor by id number
    actor = Actor.query.get_or_404(actor_id)
    if request.method == 'POST':
        if request.form['short_bio']:
            actor.short_bio = request.form['short_bio']
        if request.form['picture']:
            actor.picture = request.form['picture']
        db.session.add(actor)
        db.session.commit()

        flash('Post Updated')
        return redirect(url_for('actors.show_actor', actor_id=actor_id))

    return render_template('editActor.html', actor=actor)

@actors.route("/<int:actor_id>/delete", methods=['POST'])
@login_required
def delete_actor(actor_id):
    """delete an actor from the database"""

    actor = Actor.query.get(actor_id)
    db.session.delete(actor)
    db.session.commit()
    flash('Actor has been deleted')
    return redirect(url_for('index'))

@actors.route('/json')
def json_actor():
    """Grab all actors added and display them with their movies in a json
       object.
    """
    actors = Actor.query.all()
    return jsonify(actors=[a.serialize for a in actors])

@actors.route('/results', methods=['POST'])
@login_required
def find_actor():
    """Find all actors whose names contain the provided string"""
    
    if request.method == 'POST':
        search = request.form['search']
        actors = Actor.query.filter(Actor.name.contains(search)).all()
        if actors:
            flash(f"{len(actors)} matches, click on the name to see details!")
        else:
            flash("Sorry, no matches. Please add new actor!")

        return render_template('find_actor.html', actors=actors)
