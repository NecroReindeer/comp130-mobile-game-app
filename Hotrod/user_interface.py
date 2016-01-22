import json

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

import server

class Screen(FloatLayout):
    def set_size(self, instance, value):
        self.size = self.parent.size
        self.center = self.parent.center


class GameOverScreen(Screen):

    def show_score(self, score):
        self.player_score_text.text = "Score: " + str(score)

    def show_high_scores(self, level):
        high_request = server.get_high_scores(level)
        high_request.wait ()

        high_scores = json.loads(high_request.result)
        text = ''
        for entry in high_scores:
            name, level, score = entry
            text = text + name + ": " + str(score) + "\n"
        self.high_scores_text.text = text
        self.level_number_text.text = str(level)

    def show_best(self, player, level, score):
        best_request = server.get_best_score(player, level)
        best_request.wait()
        current_best = json.loads(best_request.result)

        if current_best is None:
            server.submit_high_score(player, level, score).wait()
            self.best_score_text.text = "New personal best!"
        elif score > current_best:
            server.update_high_score(player, level, score).wait()
            self.best_score_text.text = "New personal best!"
        else:
            self.best_score_text.text = "Personal best: " + str(current_best)


class StartScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class HeadsUpDisplay(Screen):
    pass


class NameInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        character = substring.upper()
        if len(self.text) >= 3:
            text = self.text[:2]
            new_text = text + character
            self.text = ''
            return super(NameInput, self).insert_text(new_text, from_undo=from_undo)
        else:
            return super(NameInput, self).insert_text(character, from_undo=from_undo)


class HUDText(Label):
    pass


class TitleText(Label):
    pass