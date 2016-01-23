"""Store classes for managing the user interface.

This module contains classes that relate to the display and
management of the user interface.

Classes:
Screen(FloatLayout) - class that all screens inherit from
GameOverScreen(Screen) - class for the game over screen
StartScreen(Screen) - class for the start screen
LoginScreen(Screen) - class for the login screen
HeadsUpDisplay(Screen) - class for the HUD
NameInput(TextInput) - class for player name input
HUDText(Label) - class for the HUD text
TitleText(Label) - class for title text
"""

# Standard python library
import json

# Kivy modules
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

# Own modules
import server


class Screen(FloatLayout):
    """Contain methods relating to all screens.

    This abstract class contains a method that relates to all screens.
    This class should not be instantiated directly.
    All menu/UI screens should inherit from it, so that its
    method can be called.
    """

    def set_size(self, instance, value):
        """Set the size of the screen correctly.

        This method should be bound to the window size changing using
        Kivy's bind. It ensures that the screen and its elements are
        resized appropriately.
        """

        self.size = self.parent.size
        self.center = self.parent.center


class GameOverScreen(Screen):

    """Store methods relating to the display of the game over screen.

    This class stores methods related to the display of the game over
    screen.

    Public Methods:
    show_score -- displays the given score
    show_high_scores -- displays the top 10 high scores
    show_best -- displays the player's best score
    """

    def show_final_score(self, score):
        """Set the score text to display the score.

        This method sets the game over screen's score text to
        display the given score.

        Arguments:
        score -- the score to display
        """

        self.player_score_text.text = "Score: " + str(score)

    def show_high_scores(self, level):
        """Show the high scores.

        This method requests the high scores for the given level
        from the server, and then sets the high scores and level labels to
        display this information.

        Arguments:
        level -- the level to show high scores of
        """

        high_request = server.get_high_scores(level)
        high_request.wait ()

        high_scores = json.loads(high_request.result)
        text = ''
        for entry in high_scores:
            name, level, score = entry
            text = text + name + ": " + str(score) + "\n"
        self.high_scores_text.text = text
        self.level_number_text.text = str(level)

    def show_best_score(self, player, level, score):
        """Show the player's best score.

        This method retrieves the given player's best score stored
        on the server, and compares it with the given current score.
        If the current score is less than the best, it sets the best
        score text to display the best score.

        Arguments:
        player -- the player to show the best score of
        level -- the level to get the score from
        score -- the new score to compare with the player's best score
        """

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

    """Store things relating to the display of the start screen.

    The widgets that are children of this class are defined in the
    kv file.
    """

    pass


class LoginScreen(Screen):

    """Store things relating to the display of the login screen.

    The widgets that are children of this class are defined in the
    kv file.
    """

    pass


class HeadsUpDisplay(Screen):

    """Store things relating to the display of the HUD

    The widgets that are children of this class are defined in the
    kv file.
    """

    pass


class NameInput(TextInput):
    """Provide a custom text input.

    This class allows a text input box with custom behaviour
    to be created.
    """

    def insert_text(self, substring, from_undo=False):
        """Override the default text input behaviour.

        This method overrides Kivy's default text input behaviour for
        inserting text, so that the text is capitalised and limited to
        three characters in length.
        """

        character = substring.upper()
        if len(self.text) >= 3:
            text = self.text[:2]
            new_text = text + character
            self.text = ''
            return super(NameInput, self).insert_text(new_text, from_undo=from_undo)
        else:
            return super(NameInput, self).insert_text(character, from_undo=from_undo)


class HUDText(Label):
    """Store things relating to the HUD text.

    This class is defined in the kv file.
    """

    pass


class TitleText(Label):
    """Store things relating to the title text.

    This class is defined in the kv file.
    """

    pass