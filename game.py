import pygame
import random
import os
import time
import math
from train_model import GameAgent
# model imports
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from random import sample
import numpy as np
import pandas as pd
from operator import add

pygame.font.init()  # init font

WIN_WIDTH = 1200
WIN_HEIGHT = 1200

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Parking Game")

car_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","4x4_white.png")).convert_alpha(), (100,50))
goal_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","Goal_space.png")).convert_alpha(), (130,65))
parked_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","pickup_red.png")).convert_alpha(), (100,50))
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","Solid_black.png")).convert_alpha(), (1200, 1200))


class Car:

    def __init__(self, x, y, angle=0):

        self.x = x
        self.y = y
        self.speed = 0
        self.angle = angle
        self.image = pygame.transform.rotate(car_img, self.angle)

    def turn_left(self):

        self.angle += 0.75

    def turn_right(self):

        self.angle -= 0.75

    def accelerate(self):

        self.speed += 1

    def reverse(self):

        self.speed -=1

    def brake(self):

        self.speed /= 2
        if self.speed <= 1:
            self.speed = 0

    def fix_angle(self):

        if self.angle < 0:
            self.angle += 360
        elif self.angle > 360:
            self.angle -= 360

    def move(self):

        self.fix_angle()
        radians = self.angle / 180 * math.pi
        x_angle = math.cos(radians)
        y_angle = math.sin(radians)
        self.x += x_angle * self.speed
        self.y -= y_angle * self.speed
        self.image = pygame.transform.rotate(car_img, self.angle)

    def draw(self, window):

        blitRotateCenter(window, self.image, (self.x, self.y), self.angle)

    def get_mask(self):

        return pygame.mask.from_surface(self.image)


class Obstacle:

    def __init__(self, x, y, angle = 0):

        self.x = x
        self.y = y
        self.angle = angle
        self.image = pygame.transform.rotate(parked_img, self.angle)

    def draw(self, window):

        blitRotateCenter(window, self.image, (self.x, self.y), self.angle)

    def get_mask(self):

        return pygame.mask.from_surface(self.image)

    def collide(self, car):

        car_mask = car.get_mask()
        obstacle_mask = self.get_mask()

        offset = (int(self.x - car.x), int(self.y - car.y))

        return car_mask.overlap(obstacle_mask, offset)


class Goal:

    def __init__(self, x, y, angle=0):

        self.x = x
        self.y = y
        self.angle = angle
        self.image = pygame.transform.rotate(goal_img, self.angle)

    def draw(self, window):

        blitRotateCenter(window, self.image, (self.x, self.y), self.angle)

    def get_mask(self):

        return pygame.mask.from_surface(self.image)

    def collide(self, car):

        #offset = (int(self.x - car.x), int(self.y - car.y))

        #return car_mask.overlap_area(goal_mask,offset)
        car_rect = car.image.get_rect(center=(car.x, car.y))
        goal_rect = self.image.get_rect(center=(self.x + 15, self.y))

        return goal_rect.contains(car_rect)


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    new_rect = image.get_rect(center=image.get_rect(topleft=topleft).center)

    surf.blit(image, new_rect.topleft)


def draw_window(window, car, obstacles, goal):

    window.blit(bg_img, (0,0))
    car.draw(window)
    goal.draw(window)

    # all line below draw outlines of cars
    olist = car.get_mask().outline()
    offset_list = []
    for value in olist:
        offset_list.append((int(value[0] + car.x),int(value[1] + car.y)))
    pygame.draw.lines(window, (0, 0, 255), 1, offset_list)

    for obstacle in obstacles:
        olist = obstacle.get_mask().outline()
        offset_list = []
        for value in olist:
            offset_list.append((int(value[0] + obstacle.x), int(value[1] + obstacle.y)))
        obstacle.draw(window)
        pygame.draw.lines(window, (0, 255, 0), 1, offset_list)
    # -- End of outline drawing


def play_game(model=None, gamma=0.9, epsilon=None):
    """

    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    Args:
        epsilon: used to explore the random action when we are not using 
        the model
        gamma: 
    """
    global WIN
    window = WIN
    clock = pygame.time.Clock()

    # 
    reward = 0
    learning_rate = 0.0001
    
    car = Car(200, 510, 0)


    goal = Goal(700, 370)

    obstacles = []
    for i in range(1, 3):

        obstacles.append(Obstacle(700,70 + i * 200,0))

    #obstacle_rect = obstacles[0].image.get_rect()
    #print("check",obstacle_rect.collidepoint(50,25))

    run = True
    while run:

        clock.tick(30)

        car.accelerate()
        # car.accelerate()
        # car.turn_left()

        #car.turn_left()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        car.move()

        for obstacle in obstacles:
            collision = obstacle.collide(car)
            if(collision):
                print(collision)
                print("car crash")
                return 0

        collision = goal.collide(car)
        if(collision):
            print(collision)
            print("car parked")
            return 1

        draw_window(window,car,obstacles, goal)

        angle_adjustments = [0,20,-20,90,-90,180,160,200,60,-60,120, 240]
        start_pos = (car.x + car.image.get_width()/2, car.y + car.image.get_height()/2)
        line_length = 150
        car_lines = []
        state_vectors = []
        for i in range(len(angle_adjustments)):
            angle = car.angle + angle_adjustments[i]
            #print("angle:",angle)
            radians = angle / 180 * math.pi
            x_angle = math.cos(radians)
            y_angle = math.sin(radians)
            #print("x",x_angle)
            #print("y",y_angle)
            collision = False
            for j in range(0, line_length, 5):
                point = (car.x - x_angle * j + car.image.get_width()/2,car.y + y_angle * j + car.image.get_height()/2)
                for obstacle in obstacles:
                    obstacle_rect = obstacle.image.get_rect(center = (obstacle.x + obstacle.image.get_width()/2, obstacle.y + obstacle.image.get_height()/2))
                    #print("rect",obstacle_rect)
                    #print("point", point)
                    if obstacle_rect.collidepoint(point):
                        print("point", point, "in rect", obstacle_rect)
                        collision = True
                        break
                        
                if collision:
                    break

            end_pos = (car.x - x_angle * line_length + car.image.get_width()/2, car.y + y_angle * line_length + car.image.get_height()/2)
            color = (0, 255, 255) if not collision else (255, 0, 0)
            line = pygame.draw.line(window, color, start_pos, end_pos, 2)
            #pygame.draw.lines(window,(0,255,0),1,line)
            '''collision = True
            for obstacle in obstacles:
                obstacle_rect = obstacle.image.get_rect(center = (obstacle.x + obstacle.image.get_width()/2,obstacle.y + obstacle.image.get_height()/2))
                print(obstacle_rect.colliderect(line))
                if obstacle_rect.colliderect(line):
                    pygame.draw.line(window, (255,0,0), start_pos, end_pos, 4)
                    collision = False
                    break'''

            state_vectors.append(collision)
        game_agent = GameAgent()
        # train the model
        model = game_agent.create_model()
        model.predict()
        pygame.display.update()


def run():

    # feed the model with state vectors and car and onbstacles location
    

    while True:
        play_game()


def train_model(learning_rate):
    model = Sequential()
    model.add(Dense(120, activation="relu", input_shape=(11,)))
    model.add(Dropout(0.15))
    model.add(Dense(120, activation="relu"))
    model.add(Dropout(0.15))
    model.add(Dense(120, activation="relu"))
    model.add(Dropout(0.15))
    model.add(Dense(3, activation="softmax"))
    optimizer = Adam(learning_rate)
    model.compile(loss="mse", optimizer=optimizer)
    # if training_weights:
    #     model.load_weights(training_weights)
    
    return model

if __name__ == '__main__':
    run()
