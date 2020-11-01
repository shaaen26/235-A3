from flask import Blueprint, request, render_template, redirect, url_for, session

from movie.adapters.repository import repo_instance
import movie.utilities.services as services


def get_all_genre_urls():
    genres = services.get_genres_names(repo_instance)
    genres_url = dict()
    for genre_name in genres:
        genres_url[genre_name] = url_for('movies_bp.movies_by_genre', genre=genre_name)
    return genres_url
