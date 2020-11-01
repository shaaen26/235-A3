from movie.adapters.repository import repo_instance
from typing import List
from movie.domain.model import *
from movie.adapters.repository import AbstractRepository


def get_movies_by_genre(genre: str) -> List[Movie]:
    match_genre = repo_instance.get_movies_by_genre(genre)
    return match_genre


def get_reviews_by_movie(movie: Movie) -> List[Review]:
    return repo_instance.get_reviews_by_movie(movie)


def add_reviews(movie_id: int, review_content: str, rank: int, username: str, repo: AbstractRepository):
    movie = repo.get_movie_by_id(movie_id)
    # create the review
    review = Review(movie, review_content, rank)
    # add reviews to repository
    repo.add_review(review)


def get_movies_by_actor(actor_string: str, repo: AbstractRepository) -> List[Movie]:
    return repo.get_movie_by_actor(actor_string)


def get_movies_by_director(director_string: str, repo: AbstractRepository) -> List[Movie]:
    return repo.get_movie_by_director(director_string)


## helper functions
def movie_to_dict(movie: Movie) -> dict:
    result = {}
    result["_rank"] = int(movie._rank)
    result["title"] = movie.title
    result["running_time"] = movie.runtime_minutes
    result["release_year"] = movie.release_year
    result["actors"] = "，".join([actor.actor_full_name for actor in movie.actors])
    result["director"] = movie.director.director_full_name
    result["genre"] = ", ".join([genre.genre_name for genre in movie.genres])
    result["description"] = movie.description
    # all reviews
    result["reviews"] = [i for i in get_reviews_by_movie(movie)]

    return result
