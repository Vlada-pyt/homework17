# app.py
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


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


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    genre = fields.Str()
    director_id = fields.Int()
    director = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
# наследуем класс от класса Resource
class MovieView(Resource):

# получение списка фильмов, мы отдаем список всех фильмов из БД
    def get(self):
        all_movie = Movie.query.all()
        return movies_schema.dump(all_movie), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201

    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        query = Movie.query
        if director_id:
            query = query.filter(Movie.director_id == director_id)
        if genre_id:
            query = query.filter(Movie.genre_id == genre_id)
        return MovieSchema(many=True).dump(query.all()), 200


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
# получение конкретной сущности по идентификатору
    def get(self, uid: int):
        try:
            movie = Movie.query.get(uid)
            return movie_schema.dump(movie), 200
        except Exception as e:
            return "", 404

    def put(self, uid: int):
        movie = Movie.query.get(uid)
        req_json = request.json
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre_id = req_json.get("genre_id")
        movie.genre = req_json.get("genre")
        movie.director_id = req_json.get("director_id")
        movie.director = req_json.get("director")
        db.session.add(movie)
        db.session.commit()
        return "", 204


    def delete(self, uid: int):
        movie = Movie.query.get(uid)
        db.session.delete(movie)
        db.session.commit()
        return "", 204

#получение фильмов с определенным режиссеро
@director_ns.route('/')
class DirectorView(Resource):
    def get(self):
        all_directors = Director.query.all()
        return movies_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid: int):

        director = Director.query.get(uid)
        return movie_schema.dump(director), 200

    def put(self, uid: int):
        director = Director.query.get(uid)
        req_json = request.json
        director.id = req_json.get("id")
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        director = Director.query.get(uid)
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genre_ns.route('/')
class GenreView(Resource):
    def get(self):
      all_genres = Genre.query.all()
      return movies_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        genre = Genre.query.get(uid)
        return movie_schema.dump(genre)

    def put(self, uid: int):
        genre = Genre.query.get(uid)
        req_json = request.json
        genre.id = req_json.get("id")
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204


    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
