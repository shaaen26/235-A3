import csv
import os
from typing import List, Set
from datetime import date
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.engine import Engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash

from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack

from movie.domain.model import *
from movie.adapters.repository import AbstractRepository

genres_global = None
actors_global = None
directors_global = None


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, username) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter_by(user_name=username).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user

    def get_genres(self) -> Set[Genre]:
        result = self._session_cm.session.query(Genre).all()
        return set(result)

    def add_movie(self, movie: Movie):
        with self._session_cm as scm:
            scm.session.add(movie)
            scm.commit()

    def add_actor(self, actor: Actor):
        with self._session_cm as scm:
            scm.session.add(actor)
            scm.commit()

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.add(genre)
            scm.commit()

    def add_director(self, director: Director):
        with self._session_cm as scm:
            scm.session.add(director)
            scm.commit()

    def get_movies_by_genre(self, genre) -> List[Genre]:
        movies = self._session_cm.session.query(Movie).all()
        result = []
        for movie in movies:
            for genre1 in movie.genres:
                if genre1.genre_name.lower() == genre.lower():
                    result.append(movie)
                    break
        return result

    def get_reviews_by_movie(self, movie: Movie) -> List[Review]:
        reviews = self._session_cm.session.query(Review).all()
        result = []
        for review in reviews:
            if review.movie.title == movie.title:
                result.append(review)
        return result

    def add_review(self, review: Review):
        self._session_cm.session.add(review)

    def get_movie_by_id(self, movie_id: int) -> Movie:
        return self._session_cm.session.query(Movie).filter_by(_rank=movie_id).one()

    def get_movie_by_actor(self, actor_str: str) -> List[Movie]:
        movies = self._session_cm.session.query(Movie).all()
        result = []
        for movie in movies:
            for actor in movie.actors:
                if actor_str.lower() in actor.actor_full_name.lower():
                    result.append(movie)
                    break
        return result

    def get_movie_by_director(self, director_str: str) -> List[Movie]:
        movies = self._session_cm.session.query(Movie).all()
        result = []
        for movie in self._movies:
            if director_str.lower() in movie.director.director_full_name.lower():
                result.append(movie)
        return result


def process_user(user_row):
    user_row[2] = generate_password_hash(user_row[2])
    return user_row


def parse_movie_file(filename):
    with open(filename) as f:
        reader = csv.DictReader(f)
        movie_id = 0

        director_id = 0
        actor_id = 0
        genre_id = 0

        for row in reader:
            rank = int(row['Rank'])
            title = row['Title']
            genres = row['Genre']
            description = row['Description']
            director = row['Director']
            actors = row['Actors']
            year = int(row['Year'])
            runtime_minutes = int(row['Runtime (Minutes)'])

            # parse all genres
            current_genre_id = None
            genres_split = genres.split(',')
            for i in genres_split:
                i = i.strip()
                if i in genres_global:
                    current_genre_id = genres_global[i][0][0]
                    genres_global[i].append((current_genre_id, movie_id))
                else:
                    current_genre_id = genre_id
                    genres_global[i] = list()
                    genres_global[i].append((current_genre_id, movie_id))
                    genre_id += 1

            # parse all actors
            current_actor_id = None
            actors_split = actors.split(",")
            for i in actors_split:
                i = i.strip()
                if i in actors_global:
                    current_actor_id = actors_global[i][0][0]
                    actors_global[i].append((current_actor_id, movie_id))
                else:
                    current_actor_id = actor_id
                    actors_global[i] = list()
                    actors_global[i].append((current_actor_id, movie_id))
                    actor_id += 1

            # parse all director
            current_director_id = None
            if director in directors_global:
                current_director_id = directors_global[director][0][0]
                directors_global[director].append((current_director_id, movie_id))
            else:
                current_director_id = director_id
                directors_global[director] = list()
                directors_global[director].append((current_director_id, movie_id))
                director_id += 1



            yield movie_id, title, year, rank, description, runtime_minutes, current_director_id
            movie_id += 1


def generate_genre_movie_relationship():
    index = 0
    for key in genres_global:
        for item in genres_global[key]:
            yield index, item[1], item[0]
            index += 1


def generate_actor_movie_relationship():
    index = 0
    for key in actors_global:
        for item in actors_global[key]:
            yield index, item[1], item[0]
            index += 1


def generate_director():
    for key in directors_global:
        yield directors_global[key][0][0], key


def generate_actor():
    for key in actors_global:
        yield actors_global[key][0][0], key


def generate_genre():
    for key in genres_global:
        yield genres_global[key][0][0], key


def populate(engine: Engine, data_path: str):
    conn = engine.raw_connection()
    cursor = conn.cursor()

    global genres_global
    global actors_global
    global directors_global

    genres_global = dict()
    actors_global = dict()
    directors_global = dict()

    movies_list = []
    for i in parse_movie_file(os.path.join(data_path, "Data1000Movies.csv")):
        movies_list.append(i)

    data1 = genres_global
    data2 = actors_global
    data3 = directors_global

    insert_directors = """
        INSERT INTO directors (
        id, director_full_name)
        VALUES (?, ?)"""
    cursor.executemany(insert_directors, generate_director())

    insert_actors = """
        INSERT INTO actors (
        id, actor_full_name)
        VALUES (?, ?)"""
    cursor.executemany(insert_actors, generate_actor())

    insert_genres = """
        INSERT INTO genres (
        id, genre_name)
        VALUES (?, ?)"""
    cursor.executemany(insert_genres, generate_genre())


    insert_movies = """
            INSERT INTO movies (
            id, title, release_year, rank, description, runtime_minutes, director_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert_movies, movies_list)

    insert_movie_genre = """
            INSERT INTO  movie_genre (
            id, movie_id, genre_id)
            VALUES (?, ?, ?)
    """
    cursor.executemany(insert_movie_genre, generate_genre_movie_relationship())

    insert_movie_actor = """
        INSERT INTO movie_actor (
        id, movie_id, actor_id)
        VALUES (?, ?, ?)
    """
    cursor.executemany(insert_movie_actor, generate_actor_movie_relationship())

    conn.commit()
    conn.close()
