"""Contain functions for accessing the server.

This module contains functions for accessing the server that
handles the database of players and high scores.
"""

from kivy.network.urlrequest import UrlRequest


def get_best_score(player, level):
    """Request the best score for a given player on a given level.

    This functions sends a GET request to the server to retrieve the best score
    for a given player on a given level. The function returns the request for the
    thing that called it to handle.

    Arguments:
    player -- the name of the player as a string
    level -- the level number top get the score from
    """

    request = UrlRequest('http://bsccg02.ga.fal.io/getbest.py?player=' + player + '&level=' + str(level))
    return request


def get_high_scores(level):
    """Request the high scores for the level.

    This functions sends a GET request to the server to retrieve the top 10
    high scores for the given level. The function returns the request for the
    thing that called it to handle.


    Arguments:
    level -- the level number to get the scores of
    """

    request = UrlRequest('http://bsccg02.ga.fal.io/getscores.py?level=' + str(level))
    return request


def submit_high_score(player, level, score):
    """Request that a score be added to the database.

    This functions sends a GET request to the server to add a score for the
    given player and level to the database. The function returns the request for the
    thing that called it to handle.

    Arguments:
    player -- the name of the player as a string
    level -- the level number to submit the score to
    score -- the score to submit
    """

    request = UrlRequest('http://bsccg02.ga.fal.io/submitscore.py?player=' + player +
                   '&level=' + str(level) + '&score=' + str(score))
    return request


def update_high_score(player, level, score):
    """Request that a score be updated in the database.

    This functions sends a GET request to the server to update the high score
    for the given player on a given level. The function returns the request for the
    thing that called it to handle.

    Arguments:
    player -- the name of the player as a string
    level -- the level number to update the score of
    score -- the new score to submit
    """

    request = UrlRequest('http://bsccg02.ga.fal.io/updatescore.py?player=' + player +
               '&level=' + str(level) + '&score=' + str(score))
    return request

