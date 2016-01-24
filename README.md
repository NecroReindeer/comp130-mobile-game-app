# COMP130 Mobile Game App

Creativity Cards: Hotrod and Beetle

Game: Pac-man

[Trello Board](https://trello.com/b/HY4IBdXG/kivy-mobile-game)

##Contained in this README.md
* Hotrod the Beetle Design
* Trello Board Sprints
Please see the README.md in the 'Hotrod' folder for documentation relating to the application.

##Hotrod the Beetle
Hotrod the Beetle will be a game with mechanics like Pac-Man - the player must collect pellet objects in a maze, and the level is complete when all have been collected. The player character is a beetle named Hotrod, and the enemies are rival beetles.  
The mazes will be procedurally generated. After the player completes a maze, a new one will be generated and the difficulty will be increased. The player can collect the equivilent of Pac-Man power pellets in order to defeat the enemy beetles, and send them back to their starting area.

The game is survival-based, levels will continue to be generated until you run out of lives. Your score and level can be uploaded after getting a game over, and compared with the scores of others who reached the same level.

###Design/Mechanics
####Levels
The player will be required to collect all pellets in a randomly generated maze in order to advance to the next level. When the player advances to the next level, a new maze will be generated and several parameters will be adjusted to increase the difficulty of the level, such as reducing the number of powerups and increasing the speed. The player is rewarded with an extra life and the points earned from defeating enemies and collecting pellets will also be increased. 

####Enemies
The enemies will decide where they are going to move in a way similar to the original Pac-Man ghosts, as described [here](http://gameinternals.com/post/2072558330/understanding-pac-man-ghost-behavior). Similarly, the enemies will switch between 'chase' and 'scatter' mode. When the enemies are in chase mode, their target positions will be related to catching the player. When the enemies are in scatter mode, their target positions will be at different corners of the maze. The enemies start out in the Beetle Den, and are released at separate intervals.  
When the player collects a power-up, the enemies become frightened. The enemies can only become frightened if they are active and outside of the Beetle Den. If the player goes into a frightened enemy, the enemy will return to the Beetle Den, stop being frightened, and come back out again.
If the player goes into an enemy that is not frightened, the player dies and all characters are returned to their starting positions.
The game is over if the player runs out of lives.

## Trello Board Sprints
In the screenshots below, the complete requirements for the corresponding sprint are in the 'Review' column. The tasks for the next sprint are in the 'To do' column.

#### Label Colour Key
![Labels](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/Labels.png)

####First Sprint Complete 04/12/2015
![First Sprint](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/First%20Sprint.png)

####Second Sprint Complete 07/12/2015
![Second Sprint](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/Second%20Sprint.png)

####Third Sprint Complete 09/12/2015
![Third Sprint](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/Third%20Sprint.png)

####Fourth Sprint Complete 11/12/2015
![Fourth Sprint](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/Fourth%20Sprint.png)

####Fifth Sprint Complete 07/01/2016
![Fifth Sprint](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/Fifth%20Sprint.png)

####Sixth Sprint Complete 20/01/2016
![Sixth Sprint](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/Sixth%20Sprint.png)

####Seventh Sprint Complete 21/01/2016
![Seventh Sprint](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/Seventh%20Sprint.png)

####Final Sprint Complete 23/01/2016
![Final Sprint](https://github.com/NecroReindeer/comp130-mobile-game-app/blob/master/Sprint%20Plans/Final%20Sprint.png)
