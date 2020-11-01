from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session
import movie.movies.services as services

import movie.adapters.repository as repo
import movie.utilities.utilities as utilities
from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange

from movie.authentication.authentication import login_required

# Configure Blueprint.
movie_blueprint = Blueprint('movies_bp', __name__)


@movie_blueprint.route('/movie_by_genre', methods=['GET'])
def movies_by_genre():
    movies_per_page = 5

    # Read query parameters.
    genre_name = request.args.get('genre')
    cursor = request.args.get('cursor')
    movie_to_show_review = request.args.get('view_reviews')

    if movie_to_show_review is None:
        # No movie_to_show_review query parameter, so set to false
        movie_to_show_review = False
    else:
        # Convert article_to_show_comments from string to int.
        movie_to_show_review = True

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movies and parse them to dict
    movies = [services.movie_to_dict(i) for i in services.get_movies_by_genre(genre_name)]

    specific_movies = movies[cursor:cursor + movies_per_page]

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=cursor - movies_per_page)
        first_movie_url = url_for('movies_bp.movies_by_genre', genre=genre_name)

    if cursor + movies_per_page < len(movies):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movies) / movies_per_page)
        if len(movies) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=last_cursor)

    # Construct urls for viewing article comments and adding comments.
    for movie in specific_movies:
        movie['view_review_url'] = url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=cursor,
                                           view_reviews=True)
        movie['add_review_url'] = url_for('movies_bp.review_on_movie', id=movie["_rank"], genre=genre_name, cursor=cursor)

    # Generate the webpage to display the articles.
    return render_template(
        'movies/movielist.html',
        movies_title='Movies Genre: ' + genre_name,
        movies=specific_movies,
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_reviews_for_movie=movie_to_show_review,
        genre_urls=utilities.get_all_genre_urls()
    )


@movie_blueprint.route('/review_on_movie', methods=['GET', 'POST'])
@login_required
def review_on_movie():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an article id, when subsequently called with a HTTP POST request, the article id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the article id, representing the commented article, from the form.
        movie_id = int(form.movie_id.data)

        genre_name = str(form.genre.data)
        search_keyword = str(form.search_keyword.data)
        search_type = str(form.search_type.data)
        cursor = int(form.cursor.data)

        # Use the service layer to store the new comment.
        services.add_reviews(movie_id, str(form.comment.data), int(form.rank.data), username, repo.repo_instance)

        if search_type == 'None':
            return redirect(url_for('movies_bp.movies_by_genre', genre=genre_name, cursor=cursor,
                                view_reviews=True))
        else:
            return redirect(url_for('movies_bp.search_by_keyword', type=search_type, keyword=search_keyword,
                                 cursor=cursor, view_reviews=True))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the article id, representing the movie to review, from a query parameter of the GET request.
        movie_id = int(request.args.get('id'))
        cursor = int(request.args.get("cursor"))
        genre = request.args.get("genre")

        search_type = request.args.get('type')
        search_keyword = request.args.get('keyword')

        # Store the article id in the form.
        form.movie_id.data = movie_id
        form.cursor.data = cursor

        if genre is None:
            form.genre.data = "None"
        else:
            form.genre.data = str(genre)

        if search_type is None:
            form.search_type.data = "None"
            form.search_keyword.data = "None"
        else:
            form.search_type.data = str(search_type)
            form.search_keyword.data = str(search_keyword)


    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the article id of the article being commented from the form.
        movie_id = int(form.movie_id.data)

    # For a GET or an unsuccessful POST, retrieve the article to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    return render_template(
        'movies/comment_on_movies.html',
        title='Review for movie',
        form=form,
        handler_url=url_for('movies_bp.review_on_movie'),
    )


@movie_blueprint.route('/search', methods=['GET', 'POST'])
def search_movies():

    form = SearchForm()

    if form.validate_on_submit():

        search_keyword = str(form.keyword.data)
        search_type = str(form.option.data)


        return redirect(url_for('movies_bp.search_by_keyword', type=search_type, keyword=search_keyword))


    # For a GET or an unsuccessful POST, retrieve the article to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    return render_template(
        'movies/search.html',
        title='Search for movie',
        form=form,
        handler_url=url_for('movies_bp.search_movies'),
    )


@movie_blueprint.route('/search_by_keyword', methods=["GET"])
def search_by_keyword():
    movies_per_page = 5

    # Read query parameters.
    search_type = request.args.get('type')
    search_keyword = request.args.get('keyword')
    cursor = request.args.get('cursor')

    movie_to_show_review = request.args.get('view_reviews')

    if movie_to_show_review is None:
        # No movie_to_show_review query parameter, so set to false
        movie_to_show_review = False
    else:
        # Convert article_to_show_comments from string to int.
        movie_to_show_review = True

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movies and parse them to dict
    all_target_movies = []
    if search_type.lower() == 'actor':
        all_target_movies = [services.movie_to_dict(i) for i in
                             services.get_movies_by_actor(search_keyword, repo.repo_instance)]
    else:
        all_target_movies = [services.movie_to_dict(i) for i in
                             services.get_movies_by_director(search_keyword, repo.repo_instance)]

    specific_movies = all_target_movies[cursor:cursor + movies_per_page]

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('movies_bp.search_by_keyword', type=search_type, keyword=search_keyword,
                                 cursor=cursor - movies_per_page)
        first_movie_url = url_for('movies_bp.search_by_keyword', type=search_type, keyword=search_keyword)

    if cursor + movies_per_page < len(all_target_movies):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('movies_bp.search_by_keyword', type=search_type, keyword=search_keyword,
                                 cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(all_target_movies) / movies_per_page)
        if len(all_target_movies) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('movies_bp.search_by_keyword', type=search_type, keyword=search_keyword,
                                 cursor=last_cursor)

    # Construct urls for viewing article comments and adding comments.
    for movie in specific_movies:
        movie['view_review_url'] = url_for('movies_bp.movies_by_genre', type=search_type, keyword=search_keyword,
                                           cursor=cursor,
                                           view_reviews=True)
        movie['add_review_url'] = url_for('movies_bp.review_on_movie', id=movie["_rank"], type=search_type, keyword=search_keyword, cursor=cursor)

    # Generate the webpage to display the articles.
    return render_template(
        'movies/movielist.html',
        movies_title='Movies search by ' + search_type + ' with keyword: ' + search_keyword,
        movies=specific_movies,
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_reviews_for_movie=movie_to_show_review,
        genre_urls=utilities.get_all_genre_urls()
    )


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short'),
        ProfanityFree(message='Your comment must not contain profanity')])
    rank = IntegerField('Rank', [
        DataRequired(),
        NumberRange(min=0, max=10, message="rank integer 0 - 10")
    ])

    movie_id = HiddenField("MovieId")
    genre = HiddenField("Genre")
    cursor = HiddenField("Cursor")
    search_type = HiddenField('type')
    search_keyword= HiddenField('search_keyword')

    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    option = SelectField('Option: ', choices=["Actor", "Director"])
    keyword = StringField('Keyword: ', [
        DataRequired()
    ])

    submit = SubmitField('Submit')
