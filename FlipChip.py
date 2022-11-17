#--------------------------------------------------------------------------------------------------
# Purpose            : This is the classic board game Othello or Reversi
#                      The human plays white and the computer plays black
#                      The goal is to turn as many chips as possible to your colour
#                      This is done by trapping your opponent's chips between your chips 
# Date Created       : 25Oct2022
# Author             : A.S.Harrison
# Amendment History  : Date         Author          Description
#                      25Oct2022    A.S.Harrison    Created
#                      02Nov2022    A.S.Harrison    Fixed a bug whereby play stopped when the 
#                 '                                 computer made a move and there was no move
#                                                   available to the player (see the click event).
#                      02Nov2022    A.S.Harrison    The PlaySequence list was one entry too short,
#                                                   this meant that play would be ended if the last 
#                                                   available square was the extreme bottom right.
#                      17Nov2022    A.S.Harrison    Now using messagebox from tkinter instead of the
#                                                   Windows MsgBox (so that it works on iOS too)
#                      17Nov2022    A.S.Harrison    Constants for the chip colours.
#                      17Nov2022    A.S.Harrison    The range in the best_move method was one too
#                                                   short to cover all the squares.
#                      17Nov2022    A.S.Harrison    Now regenerating PlaySequence for each new game
#                                                   so the computer evaluates moves differently for
#                                                   each new game.
#                      17Nov2022    A.S.Harrison    Minor performance enhancement - best_move now
#                                                   has an additional parameter which is used to 
#                                                   see if ANY move is available for the specified
#                                                   colour.
#                      17Nov2022    A.S.Harrison    Now updating the GUI in the draw_chips method.
#                      17Nov2022    A.S.Harrison    The line_points method wasn't working properly
#                                                   for diagonals - it was returning a valid diagonal
#                                                   when the line wrapped around the vertical edges of
#                                                   the board.
#--------------------------------------------------------------------------------------------------

import sys                                                              # Used when exitting the code
import time                                                             # Used when pausing to show the player what the computer's move is going to be
import random                                                           # For generating random numbers (used when deciding what the computer's next move is)
from tkinter import *                                                   # For GUI functionality
from tkinter import messagebox                                          # To get at the MsgBox (at the end of a game)

# Define all the constants-------------------------------------------------------------------------
SIZE_OF_BOARD = int(400)                                                # 400 pixel board size
COLUMNS = int(8)                                                        # Define the grid size
ROWS = COLUMNS                                                          # We always want a square board
CELLS = int(COLUMNS * ROWS)                                             # Total number of cells
CELL_SIZE = int(SIZE_OF_BOARD / COLUMNS)                                # Pixel width/height of one cell

NORTH = int(-COLUMNS)                                                   # Direction constants - these are used when a
SOUTH = int(COLUMNS)                                                    # chip is placed on the board and we need to
WEST = int(-1)                                                          # flip chips in all these directions
EAST = int(1)
NORTH_EAST = int(-(COLUMNS - 1))
SOUTH_EAST = int(COLUMNS + 1)
SOUTH_WEST = int(COLUMNS - 1)
NORTH_WEST = int(-(COLUMNS + 1))

NO_CHIP = int(0)                                                        # This represents an empty square
BLACK_CHIP = int(-1)                                                    # This represents a black chip
WHITE_CHIP = int(+1)                                                    # This represents a white chip

# Globals------------------------------------------------------------------------------------------
Grid = [0] * CELLS                                                      # This represents the playing grid
                                                                        # A value of -1 represents a black chip and
                                                                        # A value of +1 represents a white chip

PlaySequence = random.sample(list(range(0, CELLS, 1)), CELLS)           # This is used when the computer is selecting the next move
                                                                        # It's to ensure that the computer evaluates moves in
                                                                        # a different order for every game


# This class looks after everything. Go to the end of the code to see where
# an instance of FlipChip is created and the GUI interactions are started
class FlipChip():

    # This gets execute when an instance of FlipChip is created------------------------------------
    # This is where we do all the game initialisation
    def __init__(me):
        intWinX = int(0)
        intWinY = int(0)
        me.window = Tk()                                                # Create the window
        me.window.title('FlipChip')                                     # Set the window title
        me.canvas = Canvas(me.window, width = SIZE_OF_BOARD, height = SIZE_OF_BOARD, bg = 'green')  # Set the size and background colour
        me.window.resizable(width = False, height = False)              # Make it non-sizeable
        me.canvas.pack()                                                # This is some kind of geometry manager that looks after positioning of widgets - we don't have any widgets but without this line of code, nothing appears on the window
        
        me.window.bind('<Button-1>', me.click)                          # Create an event handler for a left click on the board

        me.reset()                                                      # Starting positions
        me.draw_grid()                                                  # Draw the grid lines
        me.draw_chips()                                                 # Draw the chips
        

    # This starts the GUI (which then raises the click event when the board is clicked)------------
    def mainloop(me):
        me.window.mainloop()


    # Fired when the board is clicked--------------------------------------------------------------
    def click(me, event):                                             
        intRow = int(((event.y / CELL_SIZE)))                           # Calculate which row was clicked
        intCol = int(((event.x / CELL_SIZE)))                           # Calculate which column was clicked
        intCell = me.cell_from_coords(intRow, intCol)                   # Which grid cell is it?
        if Grid[intCell] == NO_CHIP:                                    # If the cell doesn't have a chip in it
            if me.move_points(+1, intCell) > 0:                         # If it will result in some of the opponents chips being turned over
                me.make_move(WHITE_CHIP, intCell)                       # Then make the player's move
                me.draw_chips()                                         # Redraw the chips
                while True:                                             # Now start a loop (this is used when the computer has a go and then the human has no available moves)
                    me.computer_move()                                  # And let the computer have a go
                    if me.best_move(WHITE_CHIP, True) != -1: break      # If the human has any move available, quit the loop
                    if me.finished(): break                             # If the game is finished, quit the loop
        if me.finished():                                               # If there are no more valid moves for either player
            me.finish()                                                 # Display the results and ask if the user wants another game


    # Finish the current game----------------------------------------------------------------------
    def finish(me):                                                   
        intScoreWhite = int(me.score(WHITE_CHIP))                       # Count the white tiles
        intScoreBlack = int(me.score(BLACK_CHIP))                       # Count the black tiles
        strMsg = str("")                                                # Initialise the display string
        
        if intScoreWhite == intScoreBlack: strMsg = "It's a tie!\r\n"   # Build the display string
        if intScoreWhite >  intScoreBlack: strMsg = "White wins!\r\n"
        if intScoreWhite <  intScoreBlack: strMsg = "Black wins!\r\n"
        strMsg = strMsg + "\r\nThere are no available moves left for either player\r\n" 
        strMsg = strMsg + "\r\nBlack has " + str(intScoreBlack) + " chips and White has " + str(intScoreWhite) + " chips\r\n" 
        strMsg = strMsg + "\r\nDo you want to play again?"

        if messagebox.askquestion("FlipChip", strMsg) == "yes":         # Ask the user if s/he wants to go again
            me.reset()                                                  # S/he does, so reset the board
            me.draw_chips()                                             # aAnd redraw the (starting) chips
        else:                                                           # Otherwise the player has had enough
            sys.exit()                                                  # So quit


    # Play the computer's move---------------------------------------------------------------------
    def computer_move(me): 
        intBestCell = me.best_move(BLACK_CHIP, False)                   # Find the 'best' move for black
        if intBestCell != -1:                                           # As long as we found a valid move
            me.make_move(BLACK_CHIP, intBestCell)                       # Make the move
            me.draw_chips()                                             # Redraw the chips
        if me.finished():                                               # If there are no more valid moves for either player
            me.finish()                                                 # Display the results and ask if the user wants another game


    # Work out the best move for a colour----------------------------------------------------------
    def best_move(me, intColor: int, blnAnyMove: bool):
        i = int(0)                                                      # For looping through the cells
        intCell = int(0)                                                # The cell currently being tested
        intBestCell = int(-1)                                           # The cell that results in the best move (-1 means there are no moves available)
        intFlips = int(0)                                               # Number of chips that are flipped in each possible move
        intBestFlips = int(0)                                           # The best number of chips
        intRow = int(0)                                                 # The row of the cell being tested
        intCol = int(0)                                                 # The column of the cell being tested

        for i in range(0, CELLS):                                       # For each cell in the grid
            intCell = PlaySequence[i]                                   # This just randomises the order in which the computer evaluates the available moves
            if Grid[intCell] == 0:                                      # If this is an empty cell
                intFlips = me.move_points(intColor, intCell)            # See how many chips would be flipped if we played this cell
                if intFlips > 0:                                        # If it is a valid move (i.e. some chips would be flipped)
                    intRow = me.row_from_cell(intCell)                  # Get the row co-ordinate
                    intCol = me.col_from_cell(intCell)                  # Get the column co-ordinate
                    if intRow == 0 or intRow == ROWS-1:                 # If it's the left or right edge of the board
                        intFlips += 256                                 # Then weight it heavily
                    if intCol == 0 or intCol == ROWS-1:                 # If it's the top or bottom row of the board
                        intFlips += 256                                 # Then weight it heavily
                                                                        # Note that corners will get doubly weighted
                if intFlips > intBestFlips:                             # If this is the best move we have found so far
                    intBestCell = intCell                               # Remember its cell location
                    intBestFlips = intFlips                             # And remember its weighting
                    if blnAnyMove == True: break                        # If we're just looking if ANY move is available then we can quit the loop

        return intBestCell                                              # Return the cell with the best move


    # Calculate how many chips will be flipped for a given cell/colour-----------------------------
    def move_points(me, intColor: int, intCell: int):
        intRes = int(0)                                                 # Initialise the result

        # Straight lines
        intRes = intRes + me.line_points(intColor, intCell, NORTH)      # Add in the points gained from a line going UP from the cell being tested
        intRes = intRes + me.line_points(intColor, intCell, SOUTH)      # Add in the points gained from a line going DOWN from the cell being tested
        intRes = intRes + me.line_points(intColor, intCell, EAST)       # Add in the points gained from a line going RIGHT from the cell being tested
        intRes = intRes + me.line_points(intColor, intCell, WEST)       # Add in the points gained from a line going LEFT from the cell being tested

        # Diagonal lines
        intRes = intRes + me.line_points(intColor, intCell, NORTH_EAST) # Add in the points gained from a line going UP & RIGHT from the cell being tested
        intRes = intRes + me.line_points(intColor, intCell, SOUTH_EAST) # Add in the points gained from a line going DOWN & RIGHT from the cell being tested
        intRes = intRes + me.line_points(intColor, intCell, SOUTH_WEST) # Add in the points gained from a line going DOWN & LEFT from the cell being tested
        intRes = intRes + me.line_points(intColor, intCell, NORTH_WEST) # Add in the points gained from a line going UP & LEFT from the cell being tested

        return intRes                                                   # Return the total number of chips that would be flipped

    
    # Calculate how many chips will be flipped for a given cell/colour/direction-------------------
    def line_points(me, intColor: int, intCell: int, intDirection: int):
        intRes = int(0)                                                 # Initialise the result
        blnOther = bool(False)                                          # Have we found a chip of the opponents colour
        intRowThen = int(me.row_from_cell(intCell))                     # Starting row
        intColThen = int(me.col_from_cell(intCell))                     # Starting col
        intRowNow = int(0)                                              # Ending row
        intColNow = int(0)                                              # Ending col
        intWorkingCell = int(intCell)                                   # Which cell are we examining

        while 1:                                                        # Loop
            intWorkingCell += intDirection                              # Move to the next cell in te specified direction
            intRowNow = int(me.row_from_cell(intWorkingCell))           # Get the row of the new cell
            intColNow = int(me.col_from_cell(intWorkingCell))           # Get the column of the new cell

            if intWorkingCell < 0 or intWorkingCell > CELLS-1: return 0 # If we've gone off the grid, just quit

            if intDirection == EAST or intDirection == WEST:            # For LEFT/ RIGHT directions
                if intRowNow != intRowThen: return 0                    # We have to stay on the same row

            if intDirection == NORTH_WEST or intDirection == SOUTH_WEST:    # For diagonally LEFT directions
                if intColNow >= intColThen: return 0                    # We can't have moved to a higher column or be on the same column

            if intDirection == NORTH_EAST or intDirection == SOUTH_EAST:    # For diagonally RIGHT directions
                if intColNow <= intColThen: return 0                    # We can't have moved to a lower column or be on the same column

            if Grid[intWorkingCell] == 0: return 0                      # If there's no chip in this cell then it's not a valid move

            if blnOther == True:                                        # Have we previously come across an opponents chip yet
                if Grid[intWorkingCell] == intColor: break              # If we have now come across one of our own chips then the run is finished so return the count
                intRes += 1                                             # We ar mid-run so increment the count of chips that would be flipped
            else:                                                       # Otherwise, we have not yet come across an opponents chip
                if Grid[intWorkingCell] == me.other_color(intColor):    # If this is an opponents chip
                    blnOther = True                                     # Then this is the start of a run of opponents chips
                    intRes += 1                                         # Increment the count of chips that would be flipped
                else:                                                   # Otherwise, it's not an opponents chip (must be one of ours)
                    break                                               # So that's the end of the run and we can exit the loop
    
        return intRes                                                   # Return the number of chips that would be flipped


    # Given a colour, return the opposite colour---------------------------------------------------
    def other_color(me, intColor: int):
        if intColor == +1:                                              # If the colour is white
            return -1                                                   # Return black
        else:                                                           # Otherwise
            return +1                                                   # Return white


    # Actually place a chip and do all the flipping------------------------------------------------
    def make_move(me, intColor: int, intCell: int):

        if intColor == -1:                                              # If it's a black move (i.e. the computer's move)
            me.draw_cell(intCell,'lime')                                # Highlight the cell
            me.window.update()                                          # Make sure the UI is refreshed
            time.sleep(.5)                                              # Wait half a second
            me.draw_cell(intCell,'green')                               # De-highlight the cell
            me.window.update()                                          # Make sure the UI is refreshed

        Grid[intCell] = intColor                                        # Plant the chip colour into the grid
        me.move_line(intColor, intCell, NORTH)                          # Do all the flipping
        me.move_line(intColor, intCell, SOUTH)
        me.move_line(intColor, intCell, EAST)
        me.move_line(intColor, intCell, WEST)

        me.move_line(intColor, intCell, NORTH_EAST)
        me.move_line(intColor, intCell, SOUTH_EAST)
        me.move_line(intColor, intCell, SOUTH_WEST)
        me.move_line(intColor, intCell, NORTH_WEST)


    # Flip the chips in a specified direction------------------------------------------------------
    def move_line(me, intColor: int, intCell: int, intDirection: int):
        intWorkingCell = int(intCell)                                   # Start off with the specified cell
        if me.line_points(intColor, intWorkingCell, intDirection) > 0:  # If there are flips in the specified direction
            while 1:                                                    # Loop
                intWorkingCell += intDirection                          # Move in the specified direction
                if Grid[intWorkingCell] == intColor: break              # If we've reached the end, exit the loop
                Grid[intWorkingCell] = intColor                         # Flip the chip 


    # Draw an individual cell of the grid----------------------------------------------------------
    def draw_cell(me, intCell: int, intColor: int):
        intRow = int(me.row_from_cell(intCell))                         # Get the row
        intCol = int(me.col_from_cell(intCell))                         # Get the column
                                                                        # Draw the cell in the requested colour
        me.canvas.create_rectangle(intCol*CELL_SIZE+2,intRow*CELL_SIZE+2,(intCol+1)*CELL_SIZE-2,(intRow+1)*CELL_SIZE-2,outline=intColor,fill=intColor)


    # Count up all the chips of a specifed colour (i.e. the player's score)------------------------
    def score(me, intPlayer: int):
        intScore = int(0)                                               # Initialise the score
        for i in range(CELLS):                                          # For each cell in the grid
            if Grid[i] == intPlayer: intScore += 1                      # If it contains this player's chip, increment the score
        return intScore                                                 # Return the total value for this player


    # Draw the grid lines--------------------------------------------------------------------------
    def draw_grid(me):                                                
        for i in range(ROWS-1):                                         # For each row
            me.canvas.create_line((i + 1) * SIZE_OF_BOARD / ROWS, 0, (i + 1) * SIZE_OF_BOARD / ROWS, SIZE_OF_BOARD)       # Draw a vertical
            me.canvas.create_line(0, (i + 1) * SIZE_OF_BOARD / COLUMNS, SIZE_OF_BOARD, (i + 1) * SIZE_OF_BOARD / COLUMNS) # Draw a horizontal

    
    # Draw all the chips that have been played so far----------------------------------------------
    def draw_chips(me):                                               
        for i in range(0, ROWS):                                        # For each row
            for j in range(0, COLUMNS):                                 # For each column
                me.draw_chip(i,j)                                       # Draw the chip
        me.window.update()                                              # Make sure the GUI is up to date


    # Draw an individual chip----------------------------------------------------------------------
    def draw_chip(me, intRow: int, intCol: int):                                
        intCell = int(me.cell_from_coords(intRow,intCol))               # Calculate which cell we are drawing
        chip_color = 'green'                                            # Default to green (i.e. no chip present)
        if Grid[intCell] == BLACK_CHIP: chip_color = 'black'            # -1 indicates a black chip
        if Grid[intCell] == WHITE_CHIP: chip_color = 'white'            # +1 indicates a white chip
        me.canvas.create_oval(intCol*CELL_SIZE+4,intRow*CELL_SIZE+4,(intCol+1)*CELL_SIZE-4,(intRow+1)*CELL_SIZE-4,outline=chip_color,fill=chip_color)


    # Calculate the cell number from the row and column coordinates--------------------------------
    def cell_from_coords(me, intRow: int, intCol: int):
        return intRow * ROWS + intCol                                   # Return the equivalent grid cell


    # Calculate the row number from a cell number
    def row_from_cell(me, intCell: int):
        return int(intCell / COLUMNS)                                   # Easy one, just divide by the number of columns


    # Calculate the column number from a cell number-----------------------------------------------
    def col_from_cell(me, intCell: int):
        return int(intCell % ROWS)                                      # It's the modulus (the remainder after dividing by ROWS)


    # Reset the grid to starting positions---------------------------------------------------------
    def reset(me): 
        for i in range(0, CELLS):Grid[i] = NO_CHIP                      # Remove all chips (from previous game)
        Grid[int(CELLS / 2 - COLUMNS / 2)] = BLACK_CHIP                 # Set up the starting chips in the centre of the board
        Grid[int(CELLS / 2 - COLUMNS / 2 - 1)] = WHITE_CHIP
        Grid[int(CELLS / 2 + COLUMNS / 2)] = WHITE_CHIP
        Grid[int(CELLS / 2 + COLUMNS / 2 - 1)] = BLACK_CHIP
        PlaySequence = random.sample(list(range(0, CELLS, 1)), CELLS)   # Regenerate the computer's playing order (i.e. the order in which the computer evaluates moves)


    # Is the game over?----------------------------------------------------------------------------
    def finished(me):
        if me.best_move(WHITE_CHIP, True) != -1: return False           # If there's a white move available then we've not finished
        if me.best_move(BLACK_CHIP, True) != -1: return False           # If there's a black move available then we've not finished
        return True                                                     # Otherwise the game is over




# This is where code execution actually starts

reversi = FlipChip()                                                    # Create an instance of the game
reversi.mainloop()                                                      # Start the GUI

