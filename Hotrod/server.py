
from kivy.network.urlrequest import UrlRequest

def get_best_score(player, level):
    request = UrlRequest('http://bsccg02.ga.fal.io/getbest.py?player=' + player + '&level=' + str(level))
    return request

def get_high_scores(level):
    request = UrlRequest('http://bsccg02.ga.fal.io/getscores.py?level=' + str(level))
    return request

def submit_high_score(player, level, score):
    request = UrlRequest('http://bsccg02.ga.fal.io/submitscore.py?player=' + player +
                   '&level=' + str(level) + '&score=' + str(score))
    return request

def update_high_score(player, level, score):
    request = UrlRequest('http://bsccg02.ga.fal.io/updatescore.py?player=' + player +
               '&level=' + str(level) + '&score=' + str(score))
    return request