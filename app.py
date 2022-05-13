# app.py
import sqlalchemy.exc
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)
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
@movie_ns.route("/")  # Обрабатывает запросы "/movies/" и "/movies/?page=<int>"
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

        return movie_schema.dump(movies, many=True)

    def post(self):
        try:
            new_movie = request.json
            m = Genre(**new_movie)
            db.session.add(m)
            db.session.commit()
            return "New movie successful added"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"


@movie_ns.route("/<int:mid>/")  # Обрабатывает запрос "/movies/<int:id>/"
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
        try:
            updated_movie = request.json
            movie = Genre.query.get(mid)
            movie.name = updated_movie["name"]
            db.session.add(movie)
            db.session.commit()
            return "Movie successful updated"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"

    def delete(self, mid):
        try:
            movie = Movie.query.get(mid)
            db.session.delete(movie)
            db.session.commit()
            return "movie successful deleted"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"


# Genre views
@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).join(Movie.genre).all()
        return genre_schema.dump(genres, many=True), 200

    def post(self):
        try:
            new_genre = request.json
            g = Genre(**new_genre)
            db.session.add(g)
            db.session.commit()
            return "New genre successful added"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"


@genre_ns.route("/<int:gid>")
class GenreView(Resource):
    def get(self, gid):
        try:
            genre = db.session.query(Genre.name,
                                     Movie.title).join(Movie.genre
                                    ).filter(Genre.id == gid)
            return genre_schema_2.dump(genre, many=True), 200
        except sqlalchemy.exc.NoResultFound:
            return "No row was found when one was required"

    def put(self, gid):
        try:
            updated_genre = request.json
            genre = Genre.query.get(gid)
            genre.name = updated_genre["name"]
            db.session.add(genre)
            db.session.commit()
            return "Genre successful updated"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"

    def delete(self, gid):
        try:
            genre = Genre.query.get(gid)
            db.session.delete(genre)
            db.session.commit()
            return "Genre successful deleted"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"


# Director views
@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        return genre_schema.dump(directors, many=True), 200

    def post(self):
        try:
            new_director = request.json
            d = Director(**new_director)
            db.session.add(d)
            db.session.commit()
            return "New director successful added"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"


@director_ns.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did):
        try:
            director = Director.query.get(did)
            return genre_schema.dump(director), 200
        except sqlalchemy.exc.NoResultFound:
            return "No row was found when one was required"

    def put(self, did):
        try:
            updated_director = request.json
            director = Director.query.get(did)
            director.name = updated_director["name"]
            db.session.add(director)
            db.session.commit()
            return "Director successful updated"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"

    def delete(self, did):
        try:
            director = Director.query.get(did)
            db.session.delete(director)
            db.session.commit()
            return "director successful deleted"
        except Exception as e:
            return f"Something went wrong. Error code: {e}"


if __name__ == '__main__':
    app.run()
