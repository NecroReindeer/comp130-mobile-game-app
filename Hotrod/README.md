#Hotrod the Beetle

The application can be run from main.py.
I have structured it so that the root game widget has access to all main game element widgets (the characters and level), and all main game widgets have access to the root game widget. The main game element widgets can access each other through the root game widget.
As my program became larger, this became the least confusing way of structuring and managing interaction between elements of the game.

Some of the other design decisions about the structure of my code were made with features in mind that I did not have time to implement for the assignment, but intend to add if I ever get bored and have spare time!

##Additional Libraries/Modules/Frameworks Used:
[Kivy](http://kivy.org/)  
[enum34](https://pypi.python.org/pypi/enum34)

##Application-Specific Modules
###character
Contains classes for the enemies and player

###collectable
Contains a class for pellets and power-ups. 
It was originally going to contain classes for other collectables, such as lives and other score items. I did not have time to add those additional features in this assignment.

###direction
Contains enum class to represent the directions up, left, down and right.

###level
Contains a class for the level with methods for level generation.

###level_cell
Contains classes relating to the cells of the levels, including the cell itself and its edges.

###server
Contains functions for accessing the server where high scores are kept

###user_interface
Contains classes relating to any graphical user interface elements, such as the start and game over screen.

##Assets
All images and sounds used in the game were made by me
