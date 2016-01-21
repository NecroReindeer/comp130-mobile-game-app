
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

class Screen(FloatLayout):
    def set_size(self, instance, value):
        self.size = self.parent.size
        self.center = self.parent.center

class StartScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class ScoreScreen(Screen):
    pass

class GameOverScreen(Screen):
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