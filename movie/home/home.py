from flask import Blueprint, render_template
import movie.utilities.utilities as utilities

home_blueprint = Blueprint(
    'home_bp', __name__)


@home_blueprint.route('/', methods=['GET'])
def home():
    print(utilities.get_all_genre_urls())
    return render_template(
        'home/home.html',
        genre_urls=utilities.get_all_genre_urls()
    )
