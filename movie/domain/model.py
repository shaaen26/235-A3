import datetime


class Director:

    def __init__(self, director_full_name: str):
        if director_full_name == "" or type(director_full_name) is not str:
            self._director_full_name = None
        else:
            self._director_full_name = director_full_name.strip()

    @property
    def director_full_name(self) -> str:
        return self._director_full_name

    def __repr__(self):
        return f'<Director {self._director_full_name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.director_full_name == self.director_full_name

    def __lt__(self, other):
        return self.director_full_name < other.director_full_name

    def __hash__(self):
        return hash(self._director_full_name)


class Genre:

    def __init__(self, genre_name: str):
        if genre_name == "" or type(genre_name) is not str:
            self._genre_name = None
        else:
            self._genre_name = genre_name.strip()

    @property
    def genre_name(self) -> str:
        return self._genre_name

    def __repr__(self):
        return f'<Genre {self._genre_name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.genre_name == self._genre_name

    def __lt__(self, other):
        return self._genre_name < other.genre_name

    def __hash__(self):
        return hash(self.genre_name)


class Actor:

    def __init__(self, actor_full_name: str):
        if actor_full_name == "" or type(actor_full_name) is not str:
            self._actor_full_name = None
        else:
            self._actor_full_name = actor_full_name.strip()

        self._actors_this_one_has_worked_with = set()

    @property
    def actor_full_name(self) -> str:
        return self._actor_full_name

    def add_actor_colleague(self, colleague):
        if isinstance(colleague, self.__class__):
            self._actors_this_one_has_worked_with.add(colleague)

    def check_if_this_actor_worked_with(self, colleague):
        return colleague in self._actors_this_one_has_worked_with

    def __repr__(self):
        return f'<Actor {self._actor_full_name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.actor_full_name == self._actor_full_name

    def __lt__(self, other):
        return self._actor_full_name < other.actor_full_name

    def __hash__(self):
        return hash(self._actor_full_name)


class Movie:

    def _set_title_internal(self, title: str):
        if title.strip() == "" or type(title) is not str:
            self._title = None
        else:
            self._title = title.strip()


    def _set_release_year_internal(self, release_year: int):
        if release_year >= 1900 and type(release_year) is int:
            self._release_year = release_year
        else:
            self._release_year = None

    def __init__(self, title: str, release_year: int, rank: int):

        self._set_title_internal(title)
        self._set_release_year_internal(release_year)

        self._description = None
        self._director = None
        self._actors = []
        self._genres = []
        self._runtime_minutes = None
        self._rank = rank

    # essential attributes

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str):
        self._set_title_internal(title)

    @property
    def release_year(self) -> int:
        return self._release_year

    @release_year.setter
    def release_year(self, release_year: int):
        self._set_release_year_internal(release_year)

    # additional attributes

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str):
        if type(description) is str:
            self._description = description.strip()
        else:
            self._description = None

    @property
    def director(self) -> Director:
        return self._director

    @director.setter
    def director(self, director: Director):
        if isinstance(director, Director):
            self._director = director
        else:
            self._director = None

    @property
    def actors(self) -> list:
        return self._actors

    def add_actor(self, actor: Actor):
        if not isinstance(actor, Actor) or actor in self._actors:
            return

        self._actors.append(actor)

    def remove_actor(self, actor: Actor):
        if not isinstance(actor, Actor):
            return

        try:
            self._actors.remove(actor)
        except ValueError:
            # print(f"Movie.remove_actor: Could not find {actor} in list of actors.")
            pass

    @property
    def genres(self) -> list:
        return self._genres

    def add_genre(self, genre: Genre):
        if not isinstance(genre, Genre) or genre in self._genres:
            return

        self._genres.append(genre)

    def remove_genre(self, genre: Genre):
        if not isinstance(genre, Genre):
            return

        try:
            self._genres.remove(genre)
        except ValueError:
            # print(f"Movie.remove_genre: Could not find {genre} in list of genres.")
            pass

    @property
    def runtime_minutes(self) -> int:
        return self._runtime_minutes

    @runtime_minutes.setter
    def runtime_minutes(self, val: int):
        if val > 0:
            self._runtime_minutes = val
        else:
            raise ValueError(f'Movie.runtime_minutes setter: Value out of range {val}')

    def __get_unique_string_rep(self):
        return f"{self._title}, {self._release_year}"

    def __repr__(self):
        return f'<Movie {self.__get_unique_string_rep()}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__get_unique_string_rep() == other.__get_unique_string_rep()

    def __lt__(self, other):
        if self.title == other.title:
            return self.release_year < other.release_year
        return self.title < other.title

    def __hash__(self):
        return hash(self.__get_unique_string_rep())


class Review:

    def __init__(self, movie: Movie, review_text: str, rating: int):
        if isinstance(movie, Movie):
            self._movie = movie
        else:
            self._movie = None
        if type(review_text) is str:
            self._review_text = review_text
        else:
            self._review_text = None
        if type(rating) is int and rating >= 1 and rating <= 10:
            self._rating = rating
        else:
            self._rating = None
        self._timestamp = datetime.datetime.now()

    @property
    def movie(self) -> Movie:
        return self._movie

    @property
    def review_text(self) -> str:
        return self._review_text

    @property
    def rating(self) -> int:
        return self._rating

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.movie == self._movie and other.review_text == self._review_text and other.rating == self._rating and other.timestamp == self._timestamp

    def __repr__(self):
        return f'<Review of movie {self._movie}, rating = {self._rating}, timestamp = {self._timestamp}>'


class User:

    def __init__(self, user_name: str, password: str):
        if user_name == "" or type(user_name) is not str:
            self.user_name = None
        else:
            self.user_name = user_name.strip().lower()
        if password == "" or type(password) is not str:
            self._password = None
        else:
            self._password = password
        self.__watched_movies = list()
        self._reviews = list()
        self.__time_spent_watching_movies_minutes = 0

    @property
    def username(self) -> str:
        return self.user_name

    @property
    def password(self) -> str:
        return self._password

    @property
    def watched_movies(self) -> list:
        return self.__watched_movies

    @property
    def reviews(self) -> list:
        return self._reviews

    @property
    def time_spent_watching_movies_minutes(self) -> int:
        return self.__time_spent_watching_movies_minutes

    def watch_movie(self, movie: Movie):
        if isinstance(movie, Movie):
            self.__watched_movies.append(movie)
            self.__time_spent_watching_movies_minutes += movie.runtime_minutes

    def add_review(self, review: Review):
        if isinstance(review, Review):
            self._reviews.append(review)

    def __repr__(self):
        return f'<User {self.user_name}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.username == self.user_name

    def __lt__(self, other):
        return self.user_name < other.user_name

    def __hash__(self):
        return hash(self.user_name)


