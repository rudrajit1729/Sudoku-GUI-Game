import pygame
#from pygame.locals import *
import time
import Boards as BO
from random import randint as r
pygame.font.init()
smallfont = pygame.font.SysFont("comicsansms", 25)
medfont = pygame.font.SysFont("comicsansms", 40)
largefont = pygame.font.SysFont("comicsansms", 75)
paused=False
intro=False
red = (255, 0, 0)
green = (0, 100, 0)
white = (255, 255, 255)
black = (0, 0, 0)
yellow=(255,255,0)
blue=(0,0,255)
# Play background sound(initialized)
pygame.mixer.init(44100, -16, 2, 2048)

clock = pygame.time.Clock()
win = pygame.display.set_mode((540,600))
icon = pygame.image.load('icon2.png')
pygame.display.set_icon(icon)  # to set icon to your window
pygame.display.set_caption("Sudoku")

class Grid:
    board=BO.board[r(0,2)]#1,4,5 are difficult
    def __init__(self, rows, cols, width, height, win):
        self.rows = rows
        self.cols = cols
        self.index = r(0, 2)
        self.board = BO.board[self.index]
        self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        #print(self.index)
        self.update_model()
        self.selected = None
        self.win = win


    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row,col)) and self.solve():
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self):
        # Draw Grid Lines
        gap = self.width // 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.win, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
            pygame.draw.line(self.win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.win)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos):
        """
        :param: pos
        :return: (row, col)
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y),int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    def solve(self):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i

                if self.solve():
                    return True

                self.model[row][col] = 0

        return False

    def solve_gui(self,pace):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i
                self.cubes[row][col].set(i)
                self.cubes[row][col].draw_change(self.win, True)
                self.update_model()
                pygame.display.update()
                if pace==0:
                    pygame.time.delay(100)

                if self.solve_gui(pace):
                    return True

                self.model[row][col] = 0
                self.cubes[row][col].set(0)
                self.update_model()
                self.cubes[row][col].draw_change(self.win, False)
                pygame.display.update()
                if pace==0:
                    pygame.time.delay(100)

        return False


class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width // 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128,128,128))
            win.blit(text, (x+5, y+5))
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap//2 - text.get_width()//2), y + (gap//2 - text.get_height()//2)))

        if self.selected:
            pygame.draw.rect(win, (255,0,0), (x,y, gap ,gap), 3)

    def draw_change(self, win, g=True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width // 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap), 0)

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        win.blit(text, (x + (gap // 2 - text.get_width() // 2), y + (gap // 2 - text.get_height() // 2)))
        if g:
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None


def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if bo[i][j] == num and (i,j) != pos:
                return False

    return True


def redraw_window(win, board, time, strikes):
    win.fill((255,255,255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw()


def format_time(secs):
    sec = secs%60
    minute = secs//60
    hour = minute//60

    mat = " " + str(minute) + ":" + str(sec)
    return mat

def text_objects(text,color,size):
    if size=="small":
        textSurface=smallfont.render(text,True,color)
    elif size=="medium":
        textSurface=medfont.render(text,True,color)
    if size=="large":
        textSurface=largefont.render(text,True,color)

    return textSurface,textSurface.get_rect()

def message_to_screen(msg, color,y_displace=0,size="small"):
    textSurf,textRect=text_objects(msg,color,size)
    textRect.center=(540//2),(600//2)+y_displace
    win.blit(textSurf,textRect)

def pause():
    paused=True
    pygame.mixer.music.pause()
    while(paused):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_c:
                    paused=False
                    pygame.mixer.music.unpause()
                    pygame.mixer.music.set_volume(0.5)
                elif event.key==pygame.K_q:
                    pygame.quit()
                    quit()
        win.fill(yellow)
        message_to_screen("Paused!!", red, -250, size="large")
        message_to_screen("The objective of the game:-Fill all squares.", green, -180)
        message_to_screen("Rule:- 1-9 occurs exactly once", black, -150)
        message_to_screen("          in one row/column/block.", black, -130)  # spaces given for layouts
        message_to_screen("***Controls***", green, -90)
        message_to_screen("Press space to see the computer solve.", black, -65)
        message_to_screen("Press f for fast solution(Answer).", black, -30)
        message_to_screen("Click on a sqaure to select it.", black, 0)
        message_to_screen("Press numbers(1-9) to pencil in values.", black, 30)
        message_to_screen("Press del/backsp to delete a penciled value.", black, 60)
        message_to_screen("Press Enter to confirm a value in a place.", black, 90)
        message_to_screen("***Caution***", green, 140)
        message_to_screen("14 wrong guesses and the game ends:(", black, 170)
        message_to_screen("Press c to continue or q to quit.", red, 220)
        pygame.display.update()
        clock.tick(5)

def game_intro():
    intro=True
    while intro:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_c:
                    intro=False
                    pygame.mixer.music.load("Quiet_Time_-_David_Fesliyan.mp3")
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                if event.key==pygame.K_q:
                    pygame.quit()
                    quit()
        win.fill(yellow)
        message_to_screen("Sudoku!",green,-250,size="large")
        message_to_screen("The objective of the game:-Fill all squares.",green,-180)
        message_to_screen("Rule:- 1-9 occurs exactly once", black, -150)
        message_to_screen("          in one row/column/block.", black, -130)#spaces given for layouts
        message_to_screen("***Controls***",green,-90)
        message_to_screen("Press space to see the computer solve.",black,-65)
        message_to_screen("Press f for fast solution(Answer).", black, -30)
        message_to_screen("Click on a sqaure to select it.",black,0)
        message_to_screen("Press numbers(1-9) to pencil in values.",black,30)
        message_to_screen("Press del/backsp to delete a penciled value.",black,60)
        message_to_screen("Press Enter to confirm a value in a place.",black,90)
        message_to_screen("***Caution***", green, 140)
        message_to_screen("14 wrong guesses and the game ends:(",black,170)
        message_to_screen("Press c to play, p to pause or q to quit.", red, 220)
        message_to_screen("                       -Created by Rudrajit Choudhuri",blue,280)
        pygame.display.update()
        clock.tick(15)

def gameOver(msg=""):
    over = True
    v=0#view mode
    prev=0#prev board status
    while (over):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    v=1#wants to view the solved board
                    over=False
                elif event.key==pygame.K_c:
                    over=False
                    prev=1
                    main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        win.fill(yellow)
        message_to_screen("Game Over!!!", red, -220, size="large")
        if msg=="":
            message_to_screen("What's Sudoku?",red,-120,size="medium")
            message_to_screen("Chocolate for the brain :)", red, -60,size="medium")
        else:
            message_to_screen(msg, red, -100, "large")
        message_to_screen("Press v to view the solution.", green, 20,size="medium")
        message_to_screen("Press c to play again.",blue,80,size="medium")
        message_to_screen("Press q to quit.", blue, 140, size="medium")
        pygame.display.update()
        clock.tick(5)
    return v,prev

def main():
    board = Grid(9, 9, 540, 540, win)
    key = None
    run = True
    start = time.time()
    strikes = 0
    solved=0
    help=0
    prev=0#prev board status
    v=0#v for view mode 0 for off 1 for on
    while run:

        play_time = round(time.time() - start)
        if solved==1:
            solved=0
            pygame.time.delay(5000)
            if help==0:
                v,prev=gameOver("You Win :)")
            else:
                v,prev=gameOver()
        if prev==1:
            run=False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 or event.key==pygame.K_KP1:
                    key = 1
                if event.key == pygame.K_2 or event.key==pygame.K_KP2:
                    key = 2
                if event.key == pygame.K_3 or event.key==pygame.K_KP3:
                    key = 3
                if event.key == pygame.K_4 or event.key==pygame.K_KP4:
                    key = 4
                if event.key == pygame.K_5 or event.key==pygame.K_KP5:
                    key = 5
                if event.key == pygame.K_6 or event.key==pygame.K_KP6:
                    key = 6
                if event.key == pygame.K_7 or event.key==pygame.K_KP7:
                    key = 7
                if event.key == pygame.K_8 or event.key==pygame.K_KP8:
                    key = 8
                if event.key == pygame.K_9 or event.key==pygame.K_KP9:
                    key = 9
                if event.key == pygame.K_DELETE or event.key ==pygame.K_BACKSPACE:
                    board.clear()
                    key = None
                if event.key == pygame.K_p:
                    pause()
                if event.key==pygame.K_q:
                    run=False
                if event.key == pygame.K_SPACE:
                    help=1
                    board.solve_gui(0)
                    solved=1
                if event.key==pygame.K_f:
                    help=1
                    board.solve_gui(1)
                    solved=1

                if event.key == pygame.K_RETURN or event.key==pygame.K_KP_ENTER:
                    try:
                        i, j = board.selected
                        k=i*j
                    except:
                        continue
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("")
                        else:
                            #print("Wrong")
                            strikes += 1
                            if strikes==14:
                                pygame.time.delay(1000)
                                gameOver(msg="You Lose :(")
                                help=1
                                board.solve_gui(1)

                        key = None

                        if board.is_finished():
                            solved=1

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()
        if v == 1:#if view mode on display the board for some amount of time.
            pygame.time.delay(10000)
            v = gameOver()

game_intro()
main()
pygame.quit()
