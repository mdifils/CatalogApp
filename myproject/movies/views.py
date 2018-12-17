import requests
from myproject import db, state
from myproject.models import User, Actor, Movie, BlogPost
from flask_login import login_user, current_user, logout_user, login_required
from flask import (render_template, redirect, url_for, request, Blueprint,
                   flash, jsonify, make_response, session as login_session,
                   abort)

movies = Blueprint('movies', __name__, template_folder='templates/movies')


@movies.route('/<int:actor_id>/add', methods=['GET', 'POST'])
@login_required
def add_movie(actor_id):
    """This view Render a page to add a movie if method is GET otherwise
       it records in the database movie's informations provided
    """
    if request.method == 'POST':
        # Record the actor in our Actor Model table
        movie = Movie(title=request.form['title'],
                      genre=request.form['genre'],
                      picture=request.form['picture'],
                      description=request.form['description'],
                      actor_id=actor_id,
                      user_id=current_user.id)

        db.session.add(movie)
        db.session.commit()
        flash('Thanks for adding a new movie!')

        return redirect(url_for('actors.show_actor', actor_id=actor_id))

    return render_template('addMovie.html', actor_id=actor_id)


@movies.route('/<int:actor_id>/<int:movie_id>/')
@login_required
def show_movie(actor_id, movie_id):
    """Display full details about a movie"""
    actor = Actor.query.get(actor_id)
    movie = Movie.query.get(movie_id)
    return render_template('showMovie.html', actor=actor, movie=movie)


@movies.route('/<int:actor_id>/<int:movie_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_movie(actor_id, movie_id):
    """Edit movie's details"""

    actor = Actor.query.get(actor_id)
    movie = Movie.query.get(movie_id)
    if request.method == 'POST':
        if request.form['title']:
            movie.title = request.form['title']
        if request.form['genre']:
            movie.genre = request.form['genre']
        if request.form['description']:
            movie.description = request.form['description']
        if request.form['picture']:
            movie.picture = request.form['picture']
        db.session.add(movie)
        db.session.commit()

        flash('Movie Updated')
        return redirect(url_for('movies.show_movie', actor_id=actor_id,
                                movie_id=movie_id))

    return render_template('editMovie.html', actor=actor, movie=movie)


@movies.route("/<int:actor_id>/<int:movie_id>/delete", methods=['POST'])
@login_required
def delete_movie(actor_id, movie_id):
    """delete a movie from the database"""

    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Movie has been deleted')
    return redirect(url_for('actors.show_actor', actor_id=actor_id))
