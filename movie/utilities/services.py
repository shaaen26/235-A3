from movie.adapters.repository import AbstractRepository


def get_genres_names(repo: AbstractRepository):
    genres = repo.get_genres()
    genres_names = [i.genre_name for i in genres]
    return sorted(genres_names)
