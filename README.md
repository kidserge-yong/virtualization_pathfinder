# virtualization_pathfinder
This project was inspirited by Tech With Tim, feel free to go to his channel https://www.youtube.com/watch?v=jl5yUEdekEM.

## The program based on python.
https://www.python.org/downloads/

Program use pygame,
Start by install all requirement using 
```
pip install -r requirement.txt
```
Run program by
```
python gui_pathfinder.py
```
Currently only A* algorithm is available
You can changes G value (value from origin) in vertical and horizontal direction

```
    x
    ^
    |
x <-x->x
    |
    v
    x
```

Enable Diagonal Motion or not
G value (value from origin) in Diagonal

Enable step to use left mouse click as step controller, right click to pass though every step.
## Control
* Left Click to add start, end, blocked.
* Middle Click to clear all spot.
* Right Click to clear spot on cursor.
* Spacebar to start algorithm
* r to return to menu
