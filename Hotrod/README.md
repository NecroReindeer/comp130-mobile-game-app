#Hotrod the Beetle

The application can be run from main.py.

##Additional Libraries/Modules/Frameworks Used:
[Kivy](http://kivy.org/)  
[enum34](https://pypi.python.org/pypi/enum34)

##Application-Specific Modules
###character
Contains enemy and player classes

###collectable
Contains class for pellets. Will contain classes for other collectables, such as power-ups and other score items.

###direction
Contains enum class to represent the directions up, left, down and right.

###level
Contains a class for the level with methods for level generation.

###level_cell
Contains classes relating to the cells of the levels, including the cell itself and its edges.

###user_interface
Contains classes relating to any graphical user interface elements. Currently only has game over screen and HUD, but it will also contain classes for the start screen and high score screen.
