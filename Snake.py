import pygame
import neat
import os
import random
from enum import Enum
import numpy as np
import sys
import math
pygame.font.init()

WIN_WIDTH = 704
WIN_HEIGHT = 704

GEN = 0
clockSpeed = 100
highest_score = 0

TILE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'Tile.png')))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Snake:
    # North, South, East, West
    HEAD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'HeadNorth.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'HeadSouth.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'HeadEast.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'HeadWest.png')))]

    # North, South, East, West
    TAIL_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'TailNorth.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'TailSouth.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'TailEast.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'TailWest.png')))]

    # North to South, North to West, North to East, West to East, South to West, South to East 
    BODY_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'BodyN2S.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'BodyN2W.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'BodyN2E.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'BodyW2E.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'BodyS2W.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'BodyS2E.png')))]

    SNAKE_IMGS = []
    SNAKE_IMGS.extend(HEAD_IMGS)
    SNAKE_IMGS.extend(TAIL_IMGS)
    SNAKE_IMGS.extend(BODY_IMGS)

    class directions(Enum):
        NORTH = 0
        SOUTH = 1
        WEST = 2
        EAST = 3

    class images(Enum):
        HEAD_NORTH = 0
        HEAD_SOUTH = 1
        HEAD_EAST = 2
        HEAD_WEST = 3
        TAIL_NORTH = 4 
        TAIL_SOUTH = 5
        TAIL_EAST = 6
        TAIL_WEST = 7
        BODY_N2S = 8
        BODY_N2W = 9
        BODY_N2E = 10
        BODY_W2E = 11
        BODY_S2W = 12
        BODY_S2E = 13
        NONE = 14
    
    class Node:
        def __init__(self, direction, position, image, next=None, prev=None):
            self.direction = direction
            self.position = position
            self.image = image
            self.next = next
            self.prev = prev

        def __str__(self):
            return  (self.position)

    class LinkedList:
        def __init__(self, tail=None):
            self.tail = tail

        def getHead(self):
            node = self.tail
            while node.next != None:
                node = node.next
            return node

    def __init__(self, rand_x=None, rand_y=None):
        self.body_len = 1
        if rand_x == None:
            rand_x = random.randrange(7, 14)
        if rand_y == None:
            rand_y = random.randrange(7, 14)
        self.body = self.LinkedList(self.Node(self.directions.EAST, (rand_x - 1, rand_y), self.images.TAIL_WEST))
        self.body.tail.next = self.Node(self.directions.EAST, (rand_x, rand_y), self.images.BODY_W2E, prev=self.body.tail)
        self.body.tail.next.next = self.Node(self.directions.EAST, (rand_x + 1, rand_y), self.images.HEAD_EAST, prev=self.body.tail.next)

    def move(self, direction, rabbitPos):
        head = self.body.getHead()
        if self.getNextPosition(head, direction) == rabbitPos:
            self.eat(direction)
            return 'Rabbit Eaten'
        else:
            self.update(self.body.tail, direction, rabbitPos)
            self.updateImages(self.body.tail)
            colission = self.checkCollision()
            if colission:
                return 'Game Over'
            else:
                return ''

    def getMatrix(self, rabbitPos):
        positions = np.zeros((22,22))
        node = self.body.tail
        while node != None:
            positions[node.position[0]][node.position[1]] = 1
            node = node.next
        positions[rabbitPos[0], rabbitPos[1]] = 2
        return positions.flatten() 

    # Returns: nparray of size 9
    # [0] -> Is there an obstable in front
    # [1] -> Is there an obstacle to the left
    # [2] -> Is there an obscacle to the right
    # [3] -> Is there an obstable in front in two spaces
    # [4] -> Is there an obstacle to the left in two spaces
    # [5] -> Is there an obscacle to the right in two spaces
    # [6] -> Angle to rabbit
    # [7] -> Is there an obstacle to the front/left diagonal
    # [8] -> Is there an obscacle to the front/right diagonal
    def extGetData2(self, rabbitPos):
        data = np.zeros(9)
        positions = self.getPositions()
        head = self.body.getHead()
        if head.direction == self.directions.NORTH:
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[0] = 1
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[1] = 1
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[2] = 1
            if (head.position[0], head.position[1] - 2) in positions or head.position[1] in (0,1):
                data[3] = 1
            if (head.position[0] - 2, head.position[1]) in positions or head.position[0] in (0,1):
                data[4] = 1
            if (head.position[0] + 2, head.position[1]) in positions or head.position[0] in (21,20):
                data[5] = 1
            if (head.position[0] - 1, head.position[1] - 1) in positions or head.position[1] == 0 or head.position[0] == 21:
                data[7] = 1
            if (head.position[0] + 1, head.position[1] - 1) in positions or head.position[1] == 21 or head.position[0] == 21:
                data[8] = 1

            opposite = head.position[0] - rabbitPos[0]
            adjacent = head.position[1] - rabbitPos[1]
            #if adjacent !=  0:
            data[6] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.WEST:
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[0] = 1
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[1] = 1
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[2] = 1
            if (head.position[0] - 2, head.position[1]) in positions or head.position[0] in (0,1):
                data[3] = 1
            if (head.position[0], head.position[1] + 2) in positions or head.position[1] in (20,21):
                data[4] = 1
            if (head.position[0], head.position[1] - 2) in positions or head.position[1] in (0,1):
                data[5] = 1
            if (head.position[0] - 1, head.position[1] + 1) in positions or head.position[0] == 0 or head.position[1] == 21:
                data[7] = 1
            if (head.position[0] - 1, head.position[1] - 1) in positions or head.position[0] == 21 or head.position[1] == 0:
                data[8] = 1

            opposite = rabbitPos[1] - head.position[1]
            adjacent = head.position[0] - rabbitPos[0]
            #if adjacent !=  0:
            data[6] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.EAST:
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[0] = 1
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[1] = 1
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[2] = 1
            if (head.position[0] + 2, head.position[1]) in positions or head.position[0] in (20,21):
                data[3] = 1
            if (head.position[0], head.position[1] - 2) in positions or head.position[1] in (0,1):
                data[4] = 1
            if (head.position[0], head.position[1] + 2) in positions or head.position[1] in (20,21):
                data[5] = 1
            if (head.position[0] + 1, head.position[1] - 1) in positions or head.position[0] == 21 or head.position[1] == 0:
                data[7] = 1
            if (head.position[0] + 1, head.position[1] + 1) in positions or head.position[0] == 21 or head.position[1] == 21:
                data[8] = 1
            
            opposite = head.position[1] - rabbitPos[1]
            adjacent = rabbitPos[0] - head.position[0]
            #if adjacent !=  0:
            data[6] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.SOUTH:
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[0] = 1
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[1] = 1
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[2] = 1
            if (head.position[0], head.position[1] + 2) in positions or head.position[1] in (20,21):
                data[3] = 1
            if (head.position[0] + 2, head.position[1]) in positions or head.position[0] in (20,21):
                data[4] = 1
            if (head.position[0] - 2, head.position[1]) in positions or head.position[0] in (0,1):
                data[5] = 1
            if (head.position[0] - 1, head.position[1] + 1) in positions or head.position[0] == 0 or head.position[1] == 21:
                data[7] = 1
            if (head.position[0] + 1, head.position[1] + 1) in positions or head.position[0] == 21 or head.position[1] == 21:
                data[8] = 1

            opposite = rabbitPos[0] - head.position[0]
            adjacent = rabbitPos[1] - head.position[1]
            #if adjacent !=  0:
            data[6] = math.atan2(opposite, adjacent)


        return data       

    # Returns: nparray of size 7
    # [0] -> Is there an obstable in front
    # [1] -> Is there an obstacle to the left
    # [2] -> Is there an obscacle to the right
    # [3] -> Is there an obstable in front in two spaces
    # [4] -> Is there an obstacle to the left in two spaces
    # [5] -> Is there an obscacle to the right in two spaces
    # [6] -> Angle to rabbit
    def extGetData(self, rabbitPos):
        data = np.zeros(7)
        positions = self.getPositions()
        head = self.body.getHead()
        if head.direction == self.directions.NORTH:
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[0] = 1
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[1] = 1
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[2] = 1
            if (head.position[0], head.position[1] - 2) in positions or head.position[1] in (0,1):
                data[3] = 1
            if (head.position[0] - 2, head.position[1]) in positions or head.position[0] in (0,1):
                data[4] = 1
            if (head.position[0] + 2, head.position[1]) in positions or head.position[0] in (21,20):
                data[5] = 1


            opposite = head.position[0] - rabbitPos[0]
            adjacent = head.position[1] - rabbitPos[1]
            #if adjacent !=  0:
            data[6] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.WEST:
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[0] = 1
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[1] = 1
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[2] = 1
            if (head.position[0] - 2, head.position[1]) in positions or head.position[0] in (0,1):
                data[3] = 1
            if (head.position[0], head.position[1] + 2) in positions or head.position[1] in (20,21):
                data[4] = 1
            if (head.position[0], head.position[1] - 2) in positions or head.position[1] in (0,1):
                data[5] = 1
            opposite = rabbitPos[1] - head.position[1]
            adjacent = head.position[0] - rabbitPos[0]
            #if adjacent !=  0:
            data[6] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.EAST:
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[0] = 1
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[1] = 1
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[2] = 1
            if (head.position[0] + 2, head.position[1]) in positions or head.position[0] in (20,21):
                data[3] = 1
            if (head.position[0], head.position[1] - 2) in positions or head.position[1] in (0,1):
                data[4] = 1
            if (head.position[0], head.position[1] + 2) in positions or head.position[1] in (20,21):
                data[5] = 1
            
            opposite = head.position[1] - rabbitPos[1]
            adjacent = rabbitPos[0] - head.position[0]
            #if adjacent !=  0:
            data[6] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.SOUTH:
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[0] = 1
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[1] = 1
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[2] = 1
            if (head.position[0], head.position[1] + 2) in positions or head.position[1] in (20,21):
                data[3] = 1
            if (head.position[0] + 2, head.position[1]) in positions or head.position[0] in (20,21):
                data[4] = 1
            if (head.position[0] - 2, head.position[1]) in positions or head.position[0] in (0,1):
                data[5] = 1


            opposite = rabbitPos[0] - head.position[0]
            adjacent = rabbitPos[1] - head.position[1]
            #if adjacent !=  0:
            data[6] = math.atan2(opposite, adjacent)


        return data

    # Returns: nparray of size 4
    # [0] -> Is there an obstable in front
    # [1] -> Is there an obstacle to the left
    # [2] -> Is there an obscacle to the right
    # [3] -> Angle to rabbit
    def getData(self, rabbitPos):
        data = np.zeros(4)
        positions = self.getPositions()
        head = self.body.getHead()
        if head.direction == self.directions.NORTH:
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[0] = 1
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[1] = 1
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[2] = 1


            opposite = head.position[0] - rabbitPos[0]
            adjacent = head.position[1] - rabbitPos[1]
            #if adjacent !=  0:
            data[3] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.WEST:
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[0] = 1
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[1] = 1
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[2] = 1

            opposite = rabbitPos[1] - head.position[1]
            adjacent = head.position[0] - rabbitPos[0]
            #if adjacent !=  0:
            data[3] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.EAST:
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[0] = 1
            if (head.position[0], head.position[1] - 1) in positions or head.position[1] == 0:
                data[1] = 1
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[2] = 1
            
            opposite = head.position[1] - rabbitPos[1]
            adjacent = rabbitPos[0] - head.position[0]
            #if adjacent !=  0:
            data[3] = math.atan2(opposite, adjacent)

        elif head.direction == self.directions.SOUTH:
            if (head.position[0], head.position[1] + 1) in positions or head.position[1] == 21:
                data[0] = 1
            if (head.position[0] + 1, head.position[1]) in positions or head.position[0] == 21:
                data[1] = 1
            if (head.position[0] - 1, head.position[1]) in positions or head.position[0] == 0:
                data[2] = 1

            opposite = rabbitPos[0] - head.position[0]
            adjacent = rabbitPos[1] - head.position[1]
            #if adjacent !=  0:
            data[3] = math.atan2(opposite, adjacent)


        return data



    def checkCollision(self):
        posList = self.getPositions()
        if len(posList) == len(set(posList)):
            for pos in posList:
                if pos[0] < 0 or pos[0] >= 22 or pos[1] < 0 or pos[1] >= 21:
                    return True 
            return False
        else:
            return True
    
    def getPositions(self):
        posList = []
        node = self.body.tail
        while node != None:
            posList.append(node.position)
            node = node.next
        return posList

    def eat(self, direction):
        head = self.body.getHead()
        nextPos = self.getNextPosition(head, direction)
        image = None
        if direction == self.directions.NORTH:
            image = self.images.HEAD_NORTH
        elif direction == self.directions.SOUTH:
            image = self.images.HEAD_SOUTH
        elif direction == self.directions.EAST:
            image = self.images.HEAD_EAST
        elif direction == self.directions.WEST:
            image = self.images.HEAD_WEST
        head.next = self.Node(direction, nextPos, image, prev=head)

        if head.next.direction in (self.directions.EAST, self.directions.WEST) and head.direction in (self.directions.EAST, self.directions.WEST):
            head.image = self.images.BODY_W2E
        elif head.next.direction in (self.directions.NORTH, self.directions.SOUTH) and head.direction in (self.directions.NORTH, self.directions.SOUTH):
            head.image = self.images.BODY_N2S
        elif head.next.direction in (self.directions.NORTH, self.directions.EAST) and head.direction in (self.directions.SOUTH, self.directions.WEST):
            head.image = self.images.BODY_N2E
        elif head.next.direction in (self.directions.NORTH, self.directions.WEST) and head.direction in (self.directions.SOUTH, self.directions.EAST):
            head.image = self.images.BODY_N2W
        elif head.next.direction in (self.directions.EAST, self.directions.SOUTH) and head.direction in (self.directions.WEST, self.directions.NORTH):
            head.image = self.images.BODY_S2E
        elif head.next.direction in (self.directions.WEST, self.directions.SOUTH) and head.direction in (self.directions.EAST, self.directions.NORTH):
            head.image = self.images.BODY_S2W       

        self.body_len += 1

    def update(self, node, finalDir, rabbitPos):
        if node.next != None:
            node.direction = node.next.direction
            node.position = self.getNextPosition(node)
            self.update(node.next, finalDir, rabbitPos)
        else:
            # Prevents reversing direction
            if not ((node.direction == self.directions.NORTH and finalDir == self.directions.SOUTH) or
            (node.direction == self.directions.SOUTH and finalDir == self.directions.NORTH) or
            (node.direction == self.directions.EAST and finalDir == self.directions.WEST) or
            (node.direction == self.directions.WEST and finalDir == self.directions.EAST)):
                node.direction = finalDir

            node.position = self.getNextPosition(node)

    def updateImages(self, node):
        self.updateImage(node)
        if node.next != None:
            self.updateImages(node.next)

    def updateImage(self, node):
        if node.image in (self.images.HEAD_NORTH, self.images.HEAD_SOUTH, self.images.HEAD_EAST, self.images.HEAD_WEST):
            if node.direction == self.directions.NORTH:
                node.image = self.images.HEAD_NORTH
            elif node.direction == self.directions.SOUTH:
                node.image = self.images.HEAD_SOUTH
            elif node.direction == self.directions.EAST:
                node.image = self.images.HEAD_EAST
            elif node.direction == self.directions.WEST:
                node.image = self.images.HEAD_WEST
        elif node.image in (self.images.TAIL_NORTH, self.images.TAIL_SOUTH, self.images.TAIL_EAST, self.images.TAIL_WEST):
            if node.next.direction == self.directions.NORTH:
                node.image = self.images.TAIL_SOUTH
            elif node.next.direction == self.directions.SOUTH:
                node.image = self.images.TAIL_NORTH
            elif node.next.direction == self.directions.EAST:
                node.image = self.images.TAIL_WEST
            elif node.next.direction == self.directions.WEST:
                node.image = self.images.TAIL_EAST
        else:
            if node.next.direction in (self.directions.EAST, self.directions.WEST) and node.direction in (self.directions.EAST, self.directions.WEST):
                node.image = self.images.BODY_W2E
            elif node.next.direction in (self.directions.NORTH, self.directions.SOUTH) and node.direction in (self.directions.NORTH, self.directions.SOUTH):
                node.image = self.images.BODY_N2S
            elif node.next.direction in (self.directions.NORTH, self.directions.EAST) and node.direction in (self.directions.SOUTH, self.directions.WEST):
                node.image = self.images.BODY_N2E
            elif node.next.direction in (self.directions.NORTH, self.directions.WEST) and node.direction in (self.directions.SOUTH, self.directions.EAST):
                node.image = self.images.BODY_N2W
            elif node.next.direction in (self.directions.EAST, self.directions.SOUTH) and node.direction in (self.directions.WEST, self.directions.NORTH):
                node.image = self.images.BODY_S2E
            elif node.next.direction in (self.directions.WEST, self.directions.SOUTH) and node.direction in (self.directions.EAST, self.directions.NORTH):
                node.image = self.images.BODY_S2W

    def draw(self, win):
        node = self.body.tail
        while node != None:
            win.blit(Snake.SNAKE_IMGS[node.image.value], (node.position[0] * 32, node.position[1] * 32))
            node = node.next

    def getNextPosition(self, node, direc=None):
        if direc == None:
            direc = node.direction

        if direc == self.directions.NORTH:
            return (node.position[0], node.position[1] - 1)
        elif direc == self.directions.SOUTH:
            return (node.position[0], node.position[1] + 1)
        elif direc == self.directions.EAST:
            return (node.position[0] + 1, node.position[1])
        elif direc == self.directions.WEST:
            return (node.position[0] - 1, node.position[1])

class Rabbit:
    RABBIT_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'Rabbit.png')))
    def __init__(self, snakeSpaces, rand_X=None, rand_Y=None) -> None:
        if rand_X == None:
            rand_X = random.randrange(0,21)
        if rand_Y == None:
            rand_Y = random.randrange(0,21)
        while (rand_X, rand_Y) in snakeSpaces:
            rand_X = random.randrange(0,21)
            rand_Y = random.randrange(0,21)
        self.position = (rand_X, rand_Y)

    def draw(self, win):
        win.blit(Rabbit.RABBIT_IMG, (self.position[0] * 32, self.position[1] * 32))

def user_draw_window(win, snake, rabbit, dir):
    draw_background(win)
    result = snake.move(dir, rabbit.position)
    if result == 'Rabbit Eaten':
        rabbit = Rabbit(snake.getPositions())
    snake.draw(win)
    rabbit.draw(win)
    text = STAT_FONT.render("Score: " + str(snake.body_len), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()
    if result == 'Rabbit Eaten':
        return rabbit
    else:
        return result
        
def draw_background(win):
    x = 0
    y = 0
    for _ in range(22):
        for _ in range(22):
            win.blit(TILE_IMG, (x, y))
            x += 32
        x = 0
        y += 32 

def userRun():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    snake = Snake()
    rabbit = Rabbit(snake.getPositions())
    dir = Snake.directions.EAST
    while run:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    dir = Snake.directions.EAST
                elif event.key == pygame.K_LEFT:
                    dir = Snake.directions.WEST
                elif event.key == pygame.K_UP:
                    dir = Snake.directions.NORTH
                elif event.key == pygame.K_DOWN:
                    dir = Snake.directions.SOUTH

        result = user_draw_window(win, snake, rabbit, dir)
        if type(result) == Rabbit:
            rabbit = result
        elif result == 'Game Over':
            run = False
            pygame.quit()
            quit()



def trainRun(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,None)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

def main(genomes, config):
    global GEN
    global clockSpeed
    GEN += 1
    nets = []
    ge = []
    snakes = []
    rabbits = []
    timeSince = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        newSnake = Snake()
        snakes.append(newSnake)
        g.fitness = 0
        ge.append(g)
        rabbits.append(Rabbit(newSnake.getPositions()))
        timeSince.append(0)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    highest_score_this_gen = 0
    global highest_score
    run = True
    while run:
        clock.tick(clockSpeed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = False
                elif event.key == pygame.K_UP:
                    clockSpeed += 5
                elif event.key == pygame.K_DOWN:
                    clockSpeed -= 5

        for x, snake in enumerate(snakes):
            data = snake.extGetData2(rabbits[x].position)#np.concatenate((snake.extGetData2(rabbits[x].position), snake.getMatrix(rabbits[x].position)), axis=None)
            output = nets[x].activate(data)
            max_value = max(output)
            max_index = output.index(max_value)

            headDir = snake.body.getHead().direction 
            # [0] = Forward
            # [1] = Left
            # [2] = Right
            dir = Snake.directions.NORTH
            if headDir == Snake.directions.NORTH:
                if max_index == 0:
                    dir = Snake.directions.NORTH
                elif max_index == 1:
                    dir = Snake.directions.WEST
                elif max_index == 2:
                    dir = Snake.directions.EAST
            elif headDir == Snake.directions.SOUTH:
                if max_index == 0:
                    dir = Snake.directions.SOUTH
                elif max_index == 1:
                    dir = Snake.directions.EAST
                elif max_index == 2:
                    dir = Snake.directions.WEST
            elif headDir == Snake.directions.WEST:
                if max_index == 0:
                    dir = Snake.directions.WEST
                elif max_index == 1:
                    dir = Snake.directions.SOUTH
                elif max_index == 2:
                    dir = Snake.directions.NORTH
            elif headDir == Snake.directions.EAST:
                if max_index == 0:
                    dir = Snake.directions.EAST
                elif max_index == 1:
                    dir = Snake.directions.NORTH
                elif max_index == 2:
                    dir = Snake.directions.SOUTH


            result = snake.move(dir, rabbits[x].position)
            if snake.body_len - 1 > highest_score_this_gen:
                highest_score_this_gen = snake.body_len - 1
            if snake.body_len - 1 > highest_score:
                highest_score = snake.body_len - 1
            if result == 'Rabbit Eaten':
                rabbits[x] = Rabbit(snake.getPositions())
                ge[x].fitness += 500
                timeSince[x] = 0
            elif result == 'Game Over':
                ge[x].fitness -= 5
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)
                rabbits.pop(x)
                timeSince.pop(x)
            elif (timeSince[x] > 100 and snake.body_len <= 6) or timeSince[x] > 5000:
                ge[x].fitness -= timeSince[x]
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)
                rabbits.pop(x)
                timeSince.pop(x)
            else:
                timeSince[x] += 1
                ge[x].fitness += 1



        train_draw_window(win, snakes, rabbits, GEN, clockSpeed, highest_score_this_gen, highest_score)
        if len(snakes) == 0:
            run = False


def train_draw_window(win, snakes, rabbits, gen, clockSpeed, highest_score_this_gen, highest_score):
    draw_background(win)
    for snake in snakes:
        snake.draw(win)
    for rabbit in rabbits:
        rabbit.draw(win)
    font_color = (0,0,0) 
    text = STAT_FONT.render("Alive: " + str(len(snakes)), 1, font_color)
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    text = STAT_FONT.render("Clock Speed: " + str(clockSpeed), 1, font_color)
    win.blit(text, (500 - text.get_width(), 10))
    text = STAT_FONT.render("Gen: " + str(gen), 1, font_color)
    win.blit(text, (10, 10))
    text = STAT_FONT.render("Highest Score This Gen: " + str(highest_score_this_gen), 1, font_color)
    win.blit(text, (10, 60))
    text = STAT_FONT.render("Highest Score All Gens: " + str(highest_score), 1, font_color)
    win.blit(text, (10, 110))


    pygame.display.update()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'User':
            userRun()
        if sys.argv[1] == 'Train':
            local_dir = os.path.dirname(__file__)
            config_path = os.path.join(local_dir + "\config-feedforward.txt")

            trainRun(config_path)
    else:
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir + "\config-feedforward.txt")

        trainRun(config_path)

