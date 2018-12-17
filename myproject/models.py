from datetime import datetime
from myproject import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
#--------------------------------------------------------------------------#
# By inheriting the UserMixin we get access to a lot of built-in attributes#
# which we will be able to call in our views!                              #
# is_authenticated()                                                       #
# is_active()                                                              #
# is_anonymous()                                                           #
# get_id()                                                                 #
#--------------------------------------------------------------------------#

# The user_loader decorator allows flask-login to load the current user
# and grab their id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#-------------Project Models: USER, ACTOR, MOVIE AND BLOGPOST-----------------

class User(db.Model, UserMixin):
    """This class represents a table users in the database
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String())
    provider = db.Column(db.String(20))
    provider_id = db.Column(db.String())

    # This connects Actor to a User Adder.
    actors = db.relationship('Actor', backref='adder', lazy=True)
    # This connects Movie to a User Creator.
    movies = db.relationship('Movie', backref='creator', lazy=True)
    # This connects BlogPost to a User Poster.
    posts = db.relationship('BlogPost', backref='poster', lazy=True)

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        """This method helps to easily print an instance of the class"""
        return f"<User ID: {self.id} -- Username: {self.username}>"

    @property
    def serialize(self):
        """This method will help to represent the class User as a json object"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'actors': [a.serialize for a in self.actors],
            'movies': [m.serialize for m in self.movies],
            'posts': [p.serialize for p in self.posts]
        }


class Actor(db.Model):
    """This class represents a table actors in the database
    """
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    short_bio = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String())
    # Connecting the Actor to a particular user (adder)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Setup the relationship to the User table
    users = db.relationship(User)

    # This connects Movie to an Actor Author.
    movies = db.relationship('Movie', backref='author', lazy=True)

    def __repr__(self):
        """This method helps to easily print an instance of the class"""
        return f"<Actor ID: {self.id} --{self.name}--Added_on:{self.added_on}>"

    @property
    def serialize(self):
        """This method will help to represent the class User as a json object"""
        return {
            'id': self.id,
            'name': self.name,
            'added_on': self.added_on,
            'short_bio': self.short_bio,
            'picture': self.picture,
            'user_id': self.user_id,
            'movies': [m.serialize for m in self.movies]
        }


class Movie(db.Model):
    """This class represents a table movies in the database
    """
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(20))
    picture = db.Column(db.String())
    # Connecting the Movie to a particular actor (author)
    actor_id = db.Column(db.Integer, db.ForeignKey('actors.id'), nullable=False)
    # Connecting the Movie to a particular user (creator)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Setup the relationship to the Actor table
    actors = db.relationship(Actor)
    # Setup the relationship to the User table
    users = db.relationship(User)

    @property
    def serialize(self):
        """This method will help to represent the class User as a json object"""
        return {
            'id': self.id,
            'added_on': self.added_on,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'picture': self.picture,
            'actor_id': self.actor_id,
            'user_id': self.user_id
        }

    def __repr__(self):
        """This method helps to easily print an instance of the class"""
        return f"<Movie ID: {self.id} -- {self.title} --- Genre: {self.genre}>"


class BlogPost(db.Model):
    """This class represents a table movies in the database
    """
    __tablename__ = 'blogPosts'

    id = db.Column(db.Integer, primary_key=True)
    posted_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(140), nullable=False)
    text = db.Column(db.Text, nullable=False)
    # Connecting the BlogPost to a particular user (poster)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Setup the relationship to the User table
    users = db.relationship(User)

    @property
    def serialize(self):
        """This method will help to represent the class User as a json object"""
        return {
            'id': self.id,
            'posted_on': self.posted_on,
            'title': self.title,
            'text': self.text,
            'user_id': self.user_id
        }

    def __repr__(self):
        """This method helps to easily print an instance of the class"""
        return f"<Post ID: {self.id} -- Date: {self.date} --- {self.title}>"
