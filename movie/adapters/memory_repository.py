from abc import ABC

from ..domain.model import *
import csv
import os
from datetime import date, datetime
from typing import List, Set

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash
from movie.adapters.repository import AbstractRepository, RepositoryException


class MemoryRepository(AbstractRepository):
    # Articles ordered by date, not id. id is assumed unique.

    def __init__(self):
        self._users = list()
        self._movies = list()
        self._actors = set()
        self._geners = set()
        self._directors = set()
        self._reviews = list()


    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def add_movie(self, movie: Movie):
        self._movies.append(movie)

    def add_actor(self, actor: Actor):
        self._actors.add(actor)

    def add_genre(self, gener: Genre):
        self._geners.add(gener)

    def add_director(self, director: Director):
        self._directors.add(director)

    def get_genres(self) -> Set[Genre]:
        return self._geners

    def get_movies_by_genre(self, genre) -> List[Movie]:
        result = []
        for movie in self._movies:
            for genre1 in movie.genres:
                if genre1.genre_name.lower() == genre.lower():
                    result.append(movie)
                    break
        return result

    def add_review(self, review: Review):
        self._reviews.append(review)

    def get_reviews_by_movie(self, movie: Movie) -> List[Review]:
        result = []
        for review in self._reviews:
            if review.movie.title == movie.title:
                result.append(review)
        return result

    def get_movie_by_id(self, movie_id: int) -> Movie:
        for movie in self._movies:
            if movie.id == movie_id:
                return movie
        return None

    def get_movie_by_actor(self, actor_str: str) -> List[Movie]:
        result = []
        for movie in self._movies:
            for actor in movie.actors:
                if actor_str.lower() in actor.actor_full_name.lower():
                    result.append(movie)
                    break
        return result

    def get_movie_by_director(self, director_str: str) -> List[Movie]:
        result = []
        for movie in self._movies:
            if director_str.lower() in movie.director.director_full_name.lower():
                result.append(movie)
        return result


class MovieFileCSVReader:

    def __init__(self, file_name: str):
        self.__file_name = file_name
        self.__dataset_of_movies = []
        self.__dataset_of_actors = set()
        self.__dataset_of_directors = set()
        self.__dataset_of_genres = set()

    def read_csv_file(self):
        with open(self.__file_name, mode='r', encoding='utf-8-sig') as csvfile:
            movie_file_reader = csv.DictReader(csvfile)

            for row in movie_file_reader:
                movie = Movie(row['Title'], int(row['Year']), int(row["Rank"]))
                movie.description = row['Description']
                movie.runtime_minutes = int(row['Runtime (Minutes)'])

                director = Director(row['Director'])
                self.__dataset_of_directors.add(director)
                movie.director = director

                parsed_genres = row['Genre'].split(',')
                for genre_string in parsed_genres:
                    genre = Genre(genre_string)
                    self.__dataset_of_genres.add(genre)
                    movie.add_genre(genre)

                parsed_actors = row['Actors'].split(',')
                for actor_string in parsed_actors:
                    actor = Actor(actor_string)
                    self.__dataset_of_actors.add(actor)
                    movie.add_actor(actor)

                self.__dataset_of_movies.append(movie)

    @property
    def dataset_of_movies(self) -> list:
        return self.__dataset_of_movies

    @property
    def dataset_of_actors(self) -> set:
        return self.__dataset_of_actors

    @property
    def dataset_of_directors(self) -> set:
        return self.__dataset_of_directors

    @property
    def dataset_of_genres(self) -> set:
        return self.__dataset_of_genres




def populate(data_path: str, repo: MemoryRepository):
    movieReader = MovieFileCSVReader(os.path.join(data_path, "Data1000Movies.csv"))
    movieReader.read_csv_file()
    for movie in movieReader.dataset_of_movies:
        repo.add_movie(movie)

    for genre in movieReader.dataset_of_genres:
        repo.add_gener(genre)

    for actor in movieReader.dataset_of_actors:
        repo.add_actor(actor)

    for director in movieReader.dataset_of_directors:
        repo.add_director(director)
