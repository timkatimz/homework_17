# app.py
import json

import sqlalchemy.exc
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)
api.app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 4}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

movie_ns = api.namespace("movies")
genre_ns = api.namespace("genres")
director_ns = api.namespace("directors")


# Models
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# Schemas
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()
    genre = fields.Str()
    director = fields.Str()


movie_schema = MovieSchema()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


genre_schema = GenreSchema()


class GenreSchema2(Schema):
    id = fields.Int()
    title = fields.Str()
    name = fields.Str()


genre_schema_2 = GenreSchema2()


# Movie views
@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        page = request.args.get("page", type=int)
        genre = request.args.get("genre", type=int)
        director = request.args.get("director", type=int)
        if page is None:
            page = 1
        per_page = 10

        movies = db.session.query(Movie.id,
                                  Movie.title,
                                  Movie.description,
                                  Movie.trailer,
                                  Movie.year,
                                  Movie.rating,
                                  Genre.name.label("genre"),
                                  Director.name.label("director")
                                  ).join(Movie.genre).join(Movie.director)
        if genre is not None:
            movies = movies.filter(Movie.genre_id == genre)
        if director is not None:
            movies = movies.filter(Movie.director_id == director)
        if genre is not None and director is not None:
            movies = movies.filter(Movie.genre_id == genre,
                                   Movie.director_id == director)
        movies = movies.limit(per_page).offset((page - 1) * per_page)

        return movie_schema.dump(movies, many=True), 200

    def post(self):
        new_movie = request.get_json()
        m = Movie(**new_movie)
        db.session.add(m)
        db.session.commit()
        return "New movie successful added", 201


@movie_ns.route("/<int:mid>/")
class MovieView(Resource):
    def get(self, mid):
        movie = db.session.query(Movie.id,
                                 Movie.title,
                                 Movie.description,
                                 Movie.trailer,
                                 Movie.year,
                                 Movie.rating,
                                 Genre.name.label("genre"),
                                 Director.name.label("director")
                                 ).join(Movie.genre).join(Movie.director).filter(Movie.id == mid).one()

        return movie_schema.dump(movie), 200

    def put(self, mid):
        updated_movie = request.json
        movie = Movie.query.get(mid)
        movie.title = updated_movie["title"]
        movie.description = updated_movie["description"]
        movie.trailer = updated_movie["trailer"]
        movie.year = updated_movie["year"]
        movie.rating = updated_movie["rating"]
        movie.genre_id = updated_movie["genre_id"]
        movie.director_id = updated_movie["director_id"]

        db.session.add(movie)
        db.session.commit()
        return "Movie successful updated", 201


    def delete(self, mid):
        movie = Movie.query.get(mid)
        db.session.delete(movie)
        db.session.commit()
        return "movie successful deleted", 204



# Genre views
@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        return genre_schema.dump(genres, many=True), 200

    def post(self):
            new_genre = request.json
            g = Genre(**new_genre)
            db.session.add(g)
            db.session.commit()
            return "New genre successful added", 201


@genre_ns.route("/<int:gid>")
class GenreView(Resource):
    def get(self, gid):
        genre = Genre.query.get(gid)
        return genre_schema.dump(genre), 200

    def put(self, gid):
        updated_genre = request.json
        genre = Genre.query.get(gid)
        genre.name = updated_genre["name"]
        db.session.add(genre)
        db.session.commit()
        return "Genre successful updated", 201

    def delete(self, gid):
        genre = Genre.query.get(gid)
        db.session.delete(genre)
        db.session.commit()
        return "Genre successful deleted", 204


# Director views
@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        return director_schema.dump(directors, many=True), 200

    def post(self):
        new_director = request.json
        d = Director(**new_director)
        db.session.add(d)
        db.session.commit()
        return "New director successful added", 201


@director_ns.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did):
        director = Director.query.get(did)
        return director_schema.dump(director), 200


    def put(self, did):
        updated_director = request.json
        director = Director.query.get(did)
        director.name = updated_director["name"]
        db.session.add(director)
        db.session.commit()
        return "Director successful updated", 201


    def delete(self, did):
            director = Director.query.get(did)
            db.session.delete(director)
            db.session.commit()
            return "director successful deleted", 204


if __name__ == '__main__':
    app.run()
