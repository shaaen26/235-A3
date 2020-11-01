from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

from movie.domain import model

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

directors = Table(
    'directors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('director_full_name', String(255), unique=True, nullable=False),
)

genres = Table(
    'genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('genre_name', String(255), unique=True, nullable=False),
)

actors = Table(
    'actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('actor_full_name', String(255), unique=True, nullable=False),
)

movies = Table(
    'movies', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('release_year', Integer, nullable=False),
    Column('rank', Integer, nullable=False),
    Column('description', String(255), nullable=True),
    Column('runtime_minutes', Integer, nullable=True),
    Column('director_id', ForeignKey('directors.id'))
)

movie_genre = Table(
    "movie_genre", metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('genre_id', ForeignKey('genres.id'))
)

movie_actor = Table(
    "movie_actor", metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('actor_id', ForeignKey('actors.id'))
)


reviews = Table(
    "reviews", metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('review_text', String(1000), nullable=False),
    Column("movie_id", ForeignKey('movies.id')),
    Column('rating', Integer, nullable=False)
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        'user_name': users.c.username,
        '_password': users.c.password,
    })
    mapper(model.Director, directors, properties={
        '_director_full_name': directors.c.director_full_name,
        '_movies': relationship(model.Movie, backref='_director')
    })

    movie_mapper = mapper(model.Movie, movies, properties={
        '_title': movies.c.title,
        '_release_year': movies.c.release_year,
        '_rank': movies.c.rank,
        '_description': movies.c.description,
        '_runtime_minutes': movies.c.runtime_minutes,
        '_reviews': relationship(model.Review, backref='_movie')
    })
    mapper(model.Review, reviews, properties={
        '_review_text': reviews.c.review_text,
        '_rating': reviews.c.rating,

    })
    mapper(model.Actor, actors, properties={
        '_actor_full_name': actors.c.actor_full_name,
        '_actor_movies': relationship(
            movie_mapper,
            secondary=movie_actor,
            backref="_actors"
        )


    })
    mapper(model.Genre, genres, properties={
        '_genre_name': genres.c.genre_name,
        '_genre_movies': relationship(
            movie_mapper,
            secondary=movie_genre,
            backref="_genres"
        )
    })


