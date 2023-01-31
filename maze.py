"""A Graphical representation of the following search algorithms:BFS,DFS,double BFS,Dijckstraw,A Star.

The user can draw walls or let the program draw maze randomly , pick a starting and ending point , pick an algorithm
and start the search .

Additional libraries required : Pygame , random and the import of constants.

The file contains the following functions and classes:
    :class Cube: which represents a square in the maze
    :class Grid: which represents the menu with the buttons and the grid for the maze
    :class Button: which controls the buttons

In addition have a few methods"
    :method draw_grid: Draws the 'empty' grid
    :method manhattan_distance: counts Manhattan distance between two points
    :method restore_path: goes back through the father till there are no more and builds a path
    :method check_neighbor: checks if the current Cube is the target
    :method iterations: a single iteration of the searching algorithm (in a aze concept this step is the same for all
                        except from DFS)
    :method DFSIteration: the same as 'Iterations' but the neighbors are picked randomly and it uses a stack instead of
                        a queue
    :method main: builds a grid and enters an infinite while loop which updates the grid all the time and starts
                  different search algorithms according to what the user choose.
"""

import pygame
import random
from constants import *


class Cube:
    """The class that represents a square in the maze.

    :atr self.row: the row of the cube
    :type self.row: int
    :atr self.col: the column of the cube
    :type self.col: int
    :atr self.parent: previous cube that was picked before that (for backtracking)
    :type self.parent: Cube
    :atr self.g: amount of steps that were made after the start of the game
    :type self.g: int
    :atr self.h: the distance that is left from the current point to the target
    :type self.h: int
    :atr self.f: sum of 'g' and 'h' , represents the final distance between two points
    :type self.f: int

    :method __init__: Initiates the Cube
    :method draw: draws the Cube

    """
    def __init__(self, row, col, parent=None):
        """Initiates the Cube

        :param row: the row of the cube
        :type: int
        :param col: the column of the cube
        :type: int
        :param: the previous Cube (parent)
        :type: Cube (default None)
        """
        self.row = row
        self.col = col
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def draw(self, win):
        """draws the Cube.

        Makes each Cube a rectangle and draws it with the default color which is white.

        :param win: the interface of Pygame
        """
        pygame.draw.rect(win, WHITE, (CUBE_SIZE*self.col+1, CUBE_SIZE*self.row+1, CUBE_SIZE-1, CUBE_SIZE-1))


class Grid:
    """The class represents the menu with the buttons and the grid for the maze.

    The class holds in itself all sets of buttons : algorithms , play or reset , and the draw buttons.
    And draws the maze grid.

    :method __init__: initiates the Grid
    :method maintain_buttons: maintains the button sets in a way that only one button can be pressed
    :method update: updates the search steps and the buttons
    :method draw: draws the cubes and the lines in the colors that should be according to the searches
    :method get_pos: gets the position of the cube in the maze
    :method random_walls: draws maze randomly
    :method reset_grid: resets all the objects in the grid such as buttons and Cubes.

    :atr self.isIterating: a flag that shows if the search has started
    :type self.isIterating: bool
    :atr self.isPlayed: a flag that show if the search has ended
    :type self.isPlayed: bool
    :atr self.maze: the maze itself in numbers
    :type self.maze: list[int*int]
    :atr self.randomW: flag that shows if the random walls were pressed (can be pressed only once)
    :type self.randomW: bool
    :atr self.startPos: will contain the positions of the starting point
    :type self.startPos: list
    :atr self.targetPos: will contain the positions of the target point
    :type self.targetPos: list
    :atr self.grays: a priority queue that contains the Cubes
    :type self.grays: list
    :atr self.secondGrays: a priority queue that contains the Cubes (used only for Double BFS)
    :type self.secondGrays: list
    :atr self.algorithm_buttons: list of all the algorithm Buttons
    :type self.algorithm_buttons: list
    :atr self.play_reset_buttons: list of the Buttons Play and Reset
    :type self.play_reset_buttons: list
    :atr self.objects_buttons: list of object Buttons ( start,target,draw,random)
    :type self.objects_buttons: list

    """
    def __init__(self):
        """initiates the Grid"""

        # isIterating is to block some actions and buttons when the algorithm is running
        self.isIterating = False
        # isPlayed need to know if to run algorithm step by step or run it quickly
        self.isPlayed = False
        # draws the grid: black if it is borders , white if not
        self.maze = [[1 if (i == rows-1 or j == cols-1 or j == 0 or i == 0) else 0 for j in range(cols)]for i in
                     range(rows)]
        self.randomW = False
        self.startPos = []
        self.targetPos = []
        self.grays = []
        self.secondGrays = []
        self.algorithm_buttons = {"BFS": Button(770, 220, 'BFS'), "DFS": Button(770, 270, 'DFS'),
                                  "DBFS": Button(770, 320, 'DoubleBFS'), "Dijkstra":Button(770, 370, 'Dijkstra'),
                                   "A*": Button(770, 420, 'A*')}
        self.play_reset_buttons = {"Play": Button(720, 550, 'Play'), "Reset":Button(840, 550, 'Reset')}
        self.objects_buttons = {"Draw": Button(720, 50, 'Draw'), "Random": Button(840, 50, 'Random'),
                                "Start": Button(720, 100, 'Start'), "Target": Button(840, 100, 'Target')}

    def maintain_buttons(self, buttons, win):
        """maintains the button sets in a way that only one button can be pressed.

        :param buttons: the set of button needed to maintain
        :param win: Pygame interface we are working on
        """
        for b in buttons.values():
            if b.update(win):
                for button in buttons.values():
                    if button is not b:
                        button.unpress()

    def update(self, win):
        """updates the search steps and the buttons.

        Appointing an object (target,start,wall) on mouse click and sets its coordinates.
        Pushes the Buttons according to users choice and maintains them.
        Lets you drag the target and start after finding finished according to the search Algorithm that was chosen.

        :param win:
        :return:
        """
        self.maintain_buttons(self.objects_buttons, win)
        self.maintain_buttons(self.play_reset_buttons, win)
        self.maintain_buttons(self.algorithm_buttons, win)

        def clear_maze():
            """goes throwout all the maze and puts 1 (black) if border and 0 (white) if not"""
            for i in range(rows):
                for j in range(cols):
                    if self.maze[i][j] != WALL and self.maze[i][j] != START and self.maze[i][j] != TARGET:
                        self.maze[i][j] = SPACE

        def quickBFS(list, target=TARGET, start=START, checked=CHECKED_CUBE, marked=MARKED_CUBE):
            """ Clears the maze and runs BFS quickly without the visualization .

            :param list: list of Cubes
            :param target: Target number on maze (default 3)
            :param start:  Start number on maze (default 2)
            :param checked: Checked number on maze (default 5)
            :param marked: Marked number on maze (default 4)
            """
            clear_maze()
            while self.isIterating:
                iterations(self, list, start, target, checked, marked)

        def quickDBFS():
            """Clears the maze and runs Double BFS quickly without the visualization .

            Runs BFS from two ends (from start and from target), by swapping the target and start in one of them
            and giving different Cube lists and marked and checked numbers for maze and search.
            """
            clear_maze()
            while self.isIterating:
                iterations(self, self.grays, START, MARKED_CUBE_2)
                iterations(self, self.secondGrays, TARGET, MARKED_CUBE, CHECKED_CUBE_2, MARKED_CUBE_2)

        def quickDFS():
            """Clears the maze and runs DFS quickly without the visualization ."""
            clear_maze()
            while self.isIterating:
                DFSIteration(self)

        # if "random" is pressed then draw random walls and disable the random function with self.randomW flag
        if self.objects_buttons["Random"].pressed and not self.isIterating:
            if not self.randomW:
                self.random_walls()
                self.randomW = True

        # else if mouse if pointed on the grid then check the place of the mouse and transform it into ros and cols
        elif pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if pos[0] < width - PANEL:
                row = pos[1] // CUBE_SIZE
                col = pos[0] // CUBE_SIZE
                # if 'draw' is pressed then just draw 1 on maze
                if self.objects_buttons["Draw"].pressed:
                    if self.maze[row][col] != START and self.maze[row][col] != TARGET:
                        self.maze[row][col] = WALL
                # if 'Start' is pressed : check that it isn't wall , delete previous position of start from startPos
                # enter current position of start to startPos and mark it on maze
                # OR the game was played and we want to move the START point then we can move but not on a WALL
                elif self.objects_buttons["Start"].pressed:
                    if (self.maze[row][col] == SPACE and not self.isIterating) or(self.maze[row][col] != WALL and
                                            not self.isIterating and self.isPlayed and self.maze[row][col] != TARGET):
                        if len(self.startPos) != 0:
                            self.maze[self.startPos[0]][self.startPos[1]] = 0
                            self.startPos.pop()
                            self.startPos.pop()
                        self.startPos.append(row)
                        self.startPos.append(col)
                        self.maze[row][col] = START
                        self.grays.clear()
                        self.grays.append(Cube(row, col))
                        # if just to move static algorithm(played game)
                        if self.isPlayed:
                            self.isIterating = True
                            self.secondGrays.clear()
                            self.secondGrays.append(Cube(self.targetPos[0], self.targetPos[1]))
                            if self.algorithm_buttons["BFS"].pressed:
                                quickBFS(self.grays)
                            elif self.algorithm_buttons["DFS"].pressed:
                                quickDFS()
                            elif self.algorithm_buttons["DBFS"].pressed:
                                quickDBFS()
                            elif self.algorithm_buttons["Dijkstra"].pressed:
                                quickBFS(self.grays)
                            elif self.algorithm_buttons["A*"].pressed:
                                quickBFS(self.grays)
                # the same as on the previous button but with target
                elif self.objects_buttons["Target"].pressed:
                    if (self.maze[row][col] == SPACE and not self.isIterating) or(self.maze[row][col] != WALL and not self.isIterating
                                and self.isPlayed and self.maze[row][col] != START):
                        if len(self.targetPos) != 0:
                            self.maze[self.targetPos[0]][self.targetPos[1]] = 0
                            self.targetPos.pop()
                            self.targetPos.pop()
                        self.targetPos.append(row)
                        self.targetPos.append(col)
                        self.maze[row][col] = TARGET
                        self.secondGrays.clear()
                        self.secondGrays.append((Cube(row, col)))
                        # in addition will need to clear the greys and put the Start a new
                        if self.isPlayed:
                            self.grays.clear()
                            self.grays.append(Cube(self.startPos[0], self.startPos[1]))
                            self.isIterating = True
                            if self.algorithm_buttons["BFS"].pressed:
                                quickBFS(self.grays)
                            elif self.algorithm_buttons["DFS"].pressed:
                                quickDFS()
                            elif self.algorithm_buttons["DBFS"].pressed:
                                quickDBFS()
                            elif self.algorithm_buttons["Dijkstra"].pressed:
                                quickBFS(self.grays)
                            elif self.algorithm_buttons["A*"].pressed:
                                quickBFS(self.grays)
        # resets the grid if reset button is pressed
        if self.play_reset_buttons["Reset"].pressed:
            self.reset_grid()
        # if play is pressed then checks that target and start are positioned on the grid and that
        # one of the algorithms is picked.
        elif self.play_reset_buttons["Play"].pressed and not self.isPlayed:
            if len(self.startPos) != 0 and len(self.targetPos) != 0\
                    and (self.algorithm_buttons["BFS"].pressed or self.algorithm_buttons["DFS"].pressed
                    or self.algorithm_buttons["DBFS"].pressed or self.algorithm_buttons["Dijkstra"].pressed
                    or self.algorithm_buttons["A*"].pressed):
                self.isIterating = True
                for b in self.algorithm_buttons.values():
                    b.locked = True
                self.objects_buttons["Random"].locked = True
            else:
                self.play_reset_buttons["Play"].unpress()

    def draw(self, win):
        """draws the cubes and the lines in the colors that should be according to the searches

        :param win: our Pygame interface
        """
        for i in range(rows):
            for j in range(cols):
                if self.maze[i][j] == 1:
                    pygame.draw.rect(win, BLACK,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))
                elif self.maze[i][j] == 0:
                    pygame.draw.rect(win, WHITE,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))
                elif self.maze[i][j] == START:
                    pygame.draw.rect(win, BLUE,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))
                elif self.maze[i][j] == TARGET:
                    pygame.draw.rect(win, RED,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))
                elif self.maze[i][j] == MARKED_CUBE:
                    pygame.draw.rect(win, GREEN,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))
                elif self.maze[i][j] == CHECKED_CUBE:
                    pygame.draw.rect(win, YELLOW,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))
                elif self.maze[i][j] == PATH:
                    pygame.draw.rect(win, ORANGE,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))
                elif self.maze[i][j] == MARKED_CUBE_2:
                    pygame.draw.rect(win, PURPLE,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))
                elif self.maze[i][j] == CHECKED_CUBE_2:
                    pygame.draw.rect(win, PINK,
                                     (CUBE_SIZE * j + 1, CUBE_SIZE * i + 1, CUBE_SIZE - 1, CUBE_SIZE - 1))

    def get_pos(self, pos):
        """gets position on maze and translates it to the position on maze

        :param pos : position on grid
        :return x,y: x and y of Cube on maze
        """
        x = width/pos[0]
        y = height/pos[1]
        return x, y

    def random_walls(self):
        """Draws random maze on the grid"""
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                if self.maze[i][j] != TARGET and self.maze[i][j] != START:
                    if i % 2 == 0:
                        if random.randrange(0, 100) < 55:
                            self.maze[i][j] = WALL
                        else:
                            self.maze[i][j] = SPACE
                    else:
                        if random.randrange(0, 100) < 85:
                            self.maze[i][j] = SPACE
                        else:
                            self.maze[i][j] = WALL

    def reset_grid(self):
        """Resets the grid by resetting all the buttons and clearing the maze to starting point.

        Clears all the objects and Cube and position lists.
        """
        def reset_buttons(buttons):
            """Resets all the buttons ( unlocks and unpress them)"""
            for b in buttons.values():
                b.locked = False
                b.unpress()
        self.isIterating = False
        self.randomW = False
        self.isPlayed = False
        self.targetPos = []
        self.startPos = []
        reset_buttons(self.objects_buttons)
        reset_buttons(self.play_reset_buttons)
        reset_buttons(self.algorithm_buttons)
        self.maze = [[1 if (i == rows - 1 or j == cols - 1 or j == 0 or i == 0) else 0 for j in range(cols)] for i in
                     range(rows)]
        self.grays.clear()
        self.secondGrays.clear()


class Button:
    """A class that represents a Button.

    :method __init__: initiates the Button
    :method update: changes the color of the button depending if it is press or not
    :method press: if Button not locked then presses it
    :method unpress: if Button not locked then unpresses it

    :atr self.x: x position of button
    :type self.x: int
    :atr self.y: y position of button
    :type self.y: int
    :atr self.color: starting color of button
    :type self.color: tuple
    :atr self.pressed: a flag that shows shows if the Button is pressed or not
    :type self.pressed: bool
    :atr self.text: the text on the button
    :type self.text: str
    :atr self.locked: a flag that shows if the button is locked
    :type self.locked: bool
    :atr button_height: height of Button
    :type button_height: int
    :atr button_width: width of Button
    :type button_width: int

    :param x: x position of Button
    :type x: int
    :param y: y position of Button
    :type y: int
    :param text: text on the Button
    :type text: str
    """
    button_height = 30
    button_width = 100

    def __init__(self, x, y, text):
        """initiates the Button"""
        self.x = x
        self.y = y
        self.color = (83, 104, 120)
        self.pressed = False
        self.text = text
        self.locked = False

    def update(self, win):
        """changes the color of the button depending if it is press or not

        :param win: Pygame interface that is used
        """
        # if pressed then changes color and the border is wider
        if self.pressed:
            pygame.draw.rect(win, (112, 128, 120), (self.x, self.y, self.button_width, self.button_height))
            pygame.draw.rect(win, BLACK, (self.x - 1, self.y - 1, self.button_width + 2, self.button_height + 2), 3)
        # if not pressed then blue color with thin border
        else:
            pygame.draw.rect(win, self.color, (self.x, self.y, self.button_width, self.button_height))
            pygame.draw.rect(win, BLACK, (self.x-1, self.y-1, self.button_width+2, self.button_height+2), 1)
        pygame.font.init()
        my_font = pygame.font.SysFont('Comic Sans MS', 20)
        text_surface = my_font.render(self.text, False, (0, 0, 0))
        win.blit(text_surface, (self.x, self.y))

        # checks that mouse was pressed and the mouse position is in the button position
        # If so then button is pressed
        if pygame.mouse.get_pressed()[0] and not self.locked:
            pos = pygame.mouse.get_pos()
            if self.x < pos[0] < self.x+self.button_width and self.y < pos[1] < self.y+self.button_height:
                self.pressed = True
                return True
        return False

    def press(self):
        """if Button not locked then presses it"""
        if not self.locked:
            self.pressed = True

    def unpress(self):
        """if Button not locked then unpresses it"""
        if not self.locked:
            self.pressed = False


def draw_grid(win):
    """Draws the 'empty' grid"""
    global rows, cols, width, height
    for i in range(cols):
        pygame.draw.line(win, BLACK, (i*CUBE_SIZE, 0), (i*CUBE_SIZE, height))
    for j in range(rows):
        pygame.draw.line(win, BLACK, (0, j*CUBE_SIZE), (width-PANEL-1, j*CUBE_SIZE))

    pygame.draw.line(win, BLACK, (720, 180), (930,180),2)
    pygame.draw.line(win, BLACK, (720, 500), (930, 500),2)
    grid.draw(win)
    pygame.display.update()


def manhattan_distance(currnetRow, currentCol, targetRow, targetCol):
    """counts Manhattan distance between two points"""
    return abs(targetRow-currnetRow)+abs(targetCol-currentCol)


def restore_path(maze, current):
    """goes back through the father till there are no more and builds a path"""
    while current.parent:
        maze[current.row][current.col] = PATH
        current = current.parent


def check_neighbor(grid, list, target, marked, current, row, col):
    """checks if the current Cube is the target

    :param grid: grid class which we use
    :param list: list of Cubes
    :param target: target number for maze
    :param marked: marked number for maze
    :param current: the Cube from which we came now
    :param row: row of 'current' Cube
    :param col: column of 'current' Cube
    """
    # if targert found
    if grid.maze[row][col] == target:
        grid.isIterating = False
        grid.isPlayed = True
        grid.play_reset_buttons["Play"].unpress()
        restore_path(grid.maze, current)
        # in Double BFS there are two scenarios:
        # 1. start found target
        # 2. target found start
        # and we need to act accordingly in each scenario
        if grid.algorithm_buttons["DBFS"].pressed:
            if target == MARKED_CUBE_2:
                secondList = grid.secondGrays
            elif target == MARKED_CUBE:
                secondList = grid.grays
            while True:
                secondCube = secondList.pop(0)
                if secondCube.row == row and secondCube.col == col:
                    restore_path(grid.maze, secondCube)
                    break
    # if not found then make create a Cube and insert it into Cube list
    else:
        grid.maze[row][col] = marked
        newCube = Cube(row, col, current)
        # if A* then need to calculate distance
        if grid.algorithm_buttons["A*"].pressed:
            newCube.g = current.g + 1
            newCube.h = manhattan_distance(row, col, grid.targetPos[0], grid.targetPos[1])
            newCube.g = current.g + 1
        # if Dijkstra then need to assign distance which is always +1
        elif grid.algorithm_buttons["Dijkstra"].pressed:
            newCube.g = current.g + 1
        newCube.f = newCube.g+newCube.h
        list.append(newCube)


def iterations(grid, list, start=START, target=TARGET, checked=CHECKED_CUBE, marked=MARKED_CUBE):
    """A single iteration of the searching algorithm (in a aze concept this step is the same for all except from DFS)

    :param grid: grid class which we use
    :param list: list of Cubes
    :param start: start number for maze (default 2)
    :param target: target number for maze (default 3)
    :param marked: marked number for maze (default 6)
    :param checked: checked number for maze (default 7)

    """
    # sorts the priority queue by their f. If f the same then nothing happens.
    list.sort(key=lambda x: x.f)
    # if Cube list is empty then there is no solution
    if len(list) == 0:
        grid.isIterating = False
        grid.isPlayed = True
        grid.play_reset_buttons["Play"].unpress()
    # else take a Cube and check its neighbors
    else:
        current = list.pop(0)
        row = current.row
        col = current.col
        if grid.maze[row][col] != start:
            grid.maze[row][col] = checked
        if grid.isIterating:
            if grid.maze[row+1][col] == SPACE or grid.maze[row+1][col] == target:
                check_neighbor(grid, list, target, marked, current, row+1, col)
        if grid.isIterating:
            if grid.maze[row-1][col] == SPACE or grid.maze[row-1][col] == target:
                check_neighbor(grid, list, target, marked, current, row-1, col)
        if grid.isIterating:
            if grid.maze[row][col+1] == SPACE or grid.maze[row][col+1] == target:
                check_neighbor(grid, list, target, marked, current, row, col+1)
        if grid.isIterating:
            if grid.maze[row][col-1] == SPACE or grid.maze[row][col-1] == target:
                check_neighbor(grid, list, target, marked, current, row, col-1)


def DFSIteration(grid):
    """The same as 'Iterations' but the neighbors are picked randomly and it uses a stack instead of a queue"""
    if len(grid.grays) == 0:
        grid.isIterating = False
        grid.isPlayed = True
        grid.play_reset_buttons["Play"].unpress()
    else:
        current = grid.grays.pop()
        row = current.row
        col = current.col
        if grid.maze[row][col] != START:
            grid.maze[row][col] = CHECKED_CUBE
        # randomly picks four directions
        directions = [-1, -1, -1, -1]
        for i in range(len(directions)):
            place = random.randrange(0, 4)
            while directions[place] != -1:
                place = random.randrange(0, 4)
            directions[place] = i

        for i in directions:
            if i == 0:
                if grid.isIterating:
                    if grid.maze[row + 1][col] == SPACE or grid.maze[row + 1][col] == TARGET:
                        check_neighbor(grid, grid.grays, TARGET, MARKED_CUBE, current, row + 1, col)
            elif i == 1:
                if grid.isIterating:
                    if grid.maze[row - 1][col] == SPACE or grid.maze[row - 1][col] == TARGET:
                        check_neighbor(grid, grid.grays, TARGET, MARKED_CUBE, current, row - 1, col)
            elif i == 2:
                if grid.isIterating:
                    if grid.maze[row][col + 1] == SPACE or grid.maze[row][col + 1] == TARGET:
                        check_neighbor(grid, grid.grays, TARGET, MARKED_CUBE, current, row, col + 1)
            elif i == 3:
                if grid.isIterating:
                    if grid.maze[row][col - 1] == SPACE or grid.maze[row][col - 1] == TARGET:
                        check_neighbor(grid, grid.grays, TARGET, MARKED_CUBE, current, row, col - 1)


def main():
    """builds a grid and enters an infinite while loop which updates the grid all the time and starts different search
     algorithms according to what the user choose.
     """
    global rows, cols, width, height, grid, clock
    rows = 100
    cols = 100
    width = cols*CUBE_SIZE+PANEL
    width = cols*CUBE_SIZE+PANEL
    height = rows*CUBE_SIZE
    window = pygame.display.set_mode((width, height))
    window.fill(WHITE)
    grid = Grid()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if grid.isIterating and not grid.isPlayed:
            # starts the algorithm the user choose
            if grid.algorithm_buttons["BFS"].pressed:
                iterations(grid, grid.grays)
            elif grid.algorithm_buttons["DFS"].pressed:
                DFSIteration(grid)
            elif grid.algorithm_buttons["Dijkstra"].pressed:
                iterations(grid, grid.grays)
            elif grid.algorithm_buttons["DBFS"].pressed:
                iterations(grid, grid.grays, START, MARKED_CUBE_2)
                iterations(grid, grid.secondGrays, TARGET, MARKED_CUBE, CHECKED_CUBE_2, MARKED_CUBE_2)
            elif grid.algorithm_buttons["A*"].pressed:
                iterations(grid, grid.grays)
        grid.update(window)

        draw_grid(window)


main()

