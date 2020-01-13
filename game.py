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
        if self.speed > 10:
            self.speed = 10

    def reverse(self):

        self.speed -=1
        if self.speed < -10:
            self.speed = -10

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

    def next_action(self, arr):

        print(arr)
        if arr[0] == 1:
            print("car accelerate")
            self.accelerate()
        elif arr[1] == 1:
            print("car turn left")
            self.turn_left()
        elif arr[2] == 1:
            print("car turn right")
            self.turn_right()
        elif arr[3] == 1:
            print("car reverse")
            self.reverse()
        elif arr[4] == 1:
            print("car brake")
            self.brake()


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


def play_game(game_agent):
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
    reward = 0
    #game_agent = GameAgent(gamma, epsilon)


    car = Car(200, 510, 90)
    goal = Goal(700, 370)
    obstacles = []
    obstacles.append(Obstacle(800,550,90))
    for i in range(1, 3):

        obstacles.append(Obstacle(700,100 + i * 180,0))

    old_state = np.array(game_agent.get_game_states(car, goal, [False] * 12))
    next_action = [1,0,0,0,0]
    run = True
    while run:

        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break


        car.next_action(next_action)
        car.move()
        print("car x",car.x)
        print("car y", car.y)
        #print("car speed", car.speed)

        car_crash = False
        car_parked = False

        # check if car is out of bounds
        if car.x < 0 or car.x > 1200 or car.y < 0 or car.y > 1200:
            car_crash = True

        # check for car crash
        for obstacle in obstacles:
            collision = obstacle.collide(car)
            if(collision):
                print(collision)
                print("car crash")
                car_crash = True

        # check for parking
        collision = goal.collide(car)
        if(collision):
            print(collision)
            print("car parked")
            car_parked = True

        if car_parked:
            from datetime import datetime
            parked_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('sorted_source_text.txt', 'w') as file:
                file.write(parked_time)
            
            return 0

            

        draw_window(window,car,obstacles, goal)

        # draw sensor lines
        angle_adjustments = [0,20,-20,90,-90,180,160,200,60,-60,120,240]
        start_pos = (car.x + car.image.get_width()/2, car.y + car.image.get_height()/2)
        line_length = 150
        car_lines = []
        state_vectors = []
        for i in range(len(angle_adjustments)):
            angle = car.angle + angle_adjustments[i]
            radians = angle / 180 * math.pi
            x_angle = math.cos(radians)
            y_angle = math.sin(radians)
            collision = False
            for j in range(0, line_length, 5):
                point = (car.x - x_angle * j + car.image.get_width()/2,car.y + y_angle * j + car.image.get_height()/2)
                for obstacle in obstacles:
                    obstacle_rect = obstacle.image.get_rect(center = (obstacle.x + obstacle.image.get_width()/2, obstacle.y + obstacle.image.get_height()/2))
                    if obstacle_rect.collidepoint(point):
                        print("point", point, "in rect", obstacle_rect)
                        collision = True
                        break

                if collision:
                    break

            end_pos = (car.x - x_angle * line_length + car.image.get_width()/2, car.y + y_angle * line_length + car.image.get_height()/2)
            color = (0, 255, 255) if not collision else (255, 0, 0)
            line = pygame.draw.line(window, color, start_pos, end_pos, 2)
            state_vectors.append(collision)

        pygame.display.update()

        # get game state
        game_state = np.array(game_agent.get_game_states(car, goal, state_vectors))
        # update model
        next_action = game_agent.predict(game_state)
        # train model
        reward = game_agent.get_game_reward(car_crash, car_parked, old_state, game_state)
        game_agent.short_term_memory_trainer(old_state, next_action, reward, game_state, (car_crash or car_parked))
        game_agent.save_state_to_memory(old_state, next_action, reward, game_state, (car_crash or car_parked))

        # set old_state to current new_state
        old_state = game_state
        run = not (car_crash or car_parked)
        print("keep running",run)

    game_agent.train_from_replayed_memory()
    game_agent.model.save("model.h5")



def run(gamma=0.9, epsilon=0.2):

    game_agent = GameAgent(gamma, epsilon)
    iter = 0
    while True:
        print("iter", iter)
        play_game(game_agent)
        iter += 1

if __name__ == '__main__':
    run()
