import abc
from typing import List, Set
from datetime import date

from movie.domain.model import User, Movie, Director, Actor, Review, Genre

repo_instance = None


class RepositoryException(Exception):

    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: User):
        """" Adds a User to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, username) -> User:
        """ Returns the User named username from the repository.

        If there is no User with the given username, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_genres(self) -> Set[Genre]:
        """ Returns all genres.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_movie(self, movie: Movie):
        raise NotImplementedError

    @abc.abstractmethod
    def add_actor(self, actor: Actor):
        raise NotImplementedError

    @abc.abstractmethod
    def add_genre(self, gener: Genre):
        raise NotImplementedError

    @abc.abstractmethod
    def add_director(self, director: Director):
        raise NotImplementedError

    @abc.abstractmethod
    def get_movies_by_genre(self, genre) -> List[Genre]:
        """ Returns all matching movies based on genre
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_reviews_by_movie(self, movie: Movie) -> List[Review]:
        """ Returns all review
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_review(self, review: Review):
        """
        Add review
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie_by_id(self, movie_id: int) -> Movie:
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie_by_actor(self, actor_str: str) -> List[Movie]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie_by_director(self, director_str: str) -> List[Movie]:
        raise NotImplementedError