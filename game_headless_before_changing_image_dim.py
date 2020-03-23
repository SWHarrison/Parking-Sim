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
# custom dot product to detect if point is in rectangle and rectangle collision
from dot_product import point_in_rectangle, rectangle_collison

pygame.font.init()  # init font

WIN_WIDTH = 1200
WIN_HEIGHT = 1200

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Parking Game")

car_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","4x4_white.png")).convert_alpha(), (100,50))
goal_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","Goal_space.png")).convert_alpha(), (130,100))
parked_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","pickup_red.png")).convert_alpha(), (100,50))
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","Solid_black.png")).convert_alpha(), (1200, 1200))


class Car:

    step = 0

    def __init__(self, x, y, angle=0):

        self.x = x
        self.y = y
        self.speed = 0
        self.steer = 0 # angle from -30 to 30 to model tires
        self.angle = angle
        self.image = pygame.transform.rotate(car_img, self.angle)
        self.time = 0

    # return list of tuples of 4 points for corners of car
    def get_corners(self):

        radians = self.angle * math.pi / 180
        car_center = (self.x + self.image.get_width()/2,self.y + self.image.get_height()/2)
        # car_center = (car.x, car.y) # for use later when headless
        left_center = (car_center[0] + (math.cos((radians + math.pi/2)) * 25), car_center[1] - (math.sin((radians + math.pi/2)) * 25))
        right_center = (car_center[0] + math.cos(radians - math.pi/2) * 25, car_center[1] - math.sin(radians - math.pi/2) * 25)

        top_right = (right_center[0] + math.cos(radians) * 50, right_center[1] - math.sin(radians) * 50)
        bottom_right = (right_center[0] - math.cos(radians) * 50, right_center[1] + math.sin(radians) * 50)

        top_left = (left_center[0] + math.cos(radians) * 50, left_center[1] - math.sin(radians) * 50)
        bottom_left = (left_center[0] - math.cos(radians) * 50, left_center[1] + math.sin(radians) * 50)

        return [top_left, bottom_left, bottom_right, top_right]

    def turn_left(self):

        self.steer += 5
        if(self.steer > 30):
            self.steer = 30

    def turn_right(self):

        self.steer -= 5
        if(self.steer < -30):
            self.steer = -30

    def accelerate(self):

        self.speed += 1
        if self.speed > 10:
            self.speed = 10

    def reverse(self):

        self.speed -=1
        if self.speed < -10:
            self.speed = -10

    def brake(self):

        self.speed *= 0.5
        if self.speed <= 1 and self.speed >= -1:
            self.speed = 0

    def fix_angle(self):

        if self.angle < 0:
            self.angle += 360
        elif self.angle > 360:
            self.angle -= 360

    def move(self):

        self.fix_angle()
        if self.steer != 0:
            self.vector_math()
        else:
            radians = self.angle / 180 * math.pi # direction car is facing
            x_angle = math.cos(radians)
            y_angle = math.sin(radians)
            self.x += x_angle * self.speed
            self.y -= y_angle * self.speed
        self.image = pygame.transform.rotate(car_img, self.angle)
        self.time += 1

    # purpose of function is to determine car's ending speed, angle and acceleration
    def vector_math(self):

        """
        important information
        rough average turning radius of car: 35'
        rough average length of car: 14'
        rough average length between two sets of tires (W): 8'
        turning radius should be achieved with maximum steer angle of 45 degrees
        r = infinity when steer = 0
        r = ~12' when steer = +-45
        r = 35' when steer = ~ +-13
        R = W / sin(steer_angle)
        centripetal accel: v^2 / r
        above formula in car class terms: self.speed^2 / (W / sin(self.steer))"""

        W = 50 # approximate length in pixels of W
        time_step = 1/30 # based on clock tick rate
        steer_rads = self.steer / 180 * math.pi
        R = (W / math.sin(steer_rads)) # turning angle based on formula
        r = (W / math.tan(steer_rads))
        print("small r turning", r)
        print("turning radius", R)
        cent_accel = (self.speed**2) / R # centripetal acceleration based on formula
        print("C force",cent_accel)
        delta_v = cent_accel * time_step # change in velocity during time step
        print("delta V", delta_v)

        radians = self.angle / 180 * math.pi # direction car is facing
        perp_radians = 0
        if(self.steer < 0):
            perp_radians = (self.angle - 90) / 180 * math.pi
        elif(self.steer > 0):
            perp_radians = (self.angle + 90) / 180 * math.pi

        x_angle = math.cos(radians)
        y_angle = math.sin(radians)

        x_speed = math.cos(radians) * self.speed + math.cos(perp_radians) * delta_v
        y_speed = math.sin(radians) * self.speed + math.sin(perp_radians) * delta_v

        old_x = self.x
        old_y = self.y
        self.x += x_speed
        self.y -= y_speed
        #print("angle after calcs 2", self.angle)
        distance = math.sqrt((self.x - old_x)**2 + (self.y - old_y)**2)
        #print("distancdistance)
        self.angle += (math.asin((distance / 2) / R)) / math.pi * 360
        print("frame",self.time)
        print("steer", self.steer)
        print("delta x", self.x - old_x)
        print("delta y", self.y - old_y)
        print("x pos", self.x)
        print("y pos", self.y)
        print("angle", self.angle)

    def draw(self, window):

        blitRotateCenter(window, self.image, (self.x, self.y), self.angle)

    def get_mask(self):

        return pygame.mask.from_surface(self.image)

    def next_action(self, arr):

        #print(arr)
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

    def get_corners(self):

        radians = self.angle * math.pi / 180
        car_center = (self.x + self.image.get_width()/2,self.y + self.image.get_height()/2)
        # car_center = (car.x, car.y) # for use later when headless
        left_center = (car_center[0] + (math.cos((radians + math.pi/2)) * 25), car_center[1] - (math.sin((radians + math.pi/2)) * 25))
        right_center = (car_center[0] + math.cos(radians - math.pi/2) * 25, car_center[1] - math.sin(radians - math.pi/2) * 25)

        top_right = (right_center[0] + math.cos(radians) * 50, right_center[1] - math.sin(radians) * 50)
        bottom_right = (right_center[0] - math.cos(radians) * 50, right_center[1] + math.sin(radians) * 50)

        top_left = (left_center[0] + math.cos(radians) * 50, left_center[1] - math.sin(radians) * 50)
        bottom_left = (left_center[0] - math.cos(radians) * 50, left_center[1] + math.sin(radians) * 50)

        return [top_left,bottom_left,bottom_right,top_right]

    def collide(self, car):

        '''car_mask = car.get_mask()
        obstacle_mask = self.get_mask()

        offset = (int(self.x - car.x), int(self.y - car.y))

        return car_mask.overlap(obstacle_mask, offset)'''

        car_corners = car.get_corners()
        obstacle_corners = self.get_corners()

        print("car",car_corners)
        print("obs",obstacle_corners)

        return rectangle_collison(car_corners, obstacle_corners)

        # D = (x2 - x1) * (yp - y1) - (xp - x1) * (y2 - y1)

        '''car_corners = car.get_corners()
        obstacle_corners = self.get_corners()

        # get dot products of all obstacle's points with car edges
        point_counters = 0
        for point in obstacle_corners:

            for i in range(0,4):

                corner_1 = car_corners[i%4]
                corner_2 = car_corners[(i+1)%4]

                dot = (corner_2[0] - corner_1[0]) * (point[1] - corner_1[1]) - (point[0] - corner_1[0]) * (corner_2[1] - corner_1[1])

                if dot <= 0:
                    break
                else:
                    point_counters += 1

        if point_counters == 4:
            return True

        # get dot products of all car's points with obstacle edges
        point_counters = 0

        for point in car_corners:

            for i in range(0,4):

                corner_1 = obstacle_corners[i%4]
                corner_2 = obstacle_corners[(i+1)%4]

                dot = (corner_2[0] - corner_1[0]) * (point[1] - corner_1[1]) - (point[0] - corner_1[0]) * (corner_2[1] - corner_1[1])

                if dot <= 0:
                    return False
                else:
                    point_counters += 1

        if point_counters == 4:
            return True
        else:
            return False'''


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

        car_center = (car.x + car.image.get_width()/2,car.y + car.image.get_height()/2)
        goal_center = (self.x + self.image.get_width()/2, self.y + self.image.get_height()/2)

        print(car_center,goal_center)

        x_distance = abs(car_center[0] - goal_center[0])
        y_distance = abs(car_center[1] - goal_center[1])
        distance = math.sqrt((car_center[0] - goal_center[0])**2 + (car_center[1] - goal_center[1])**2)
        print("distance:", distance)
        print("x_distnace", x_distance)

        return distance < 30 and x_distance < 20


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


def play_game(game_agent, iter):
    """
    runs the simulation of the a car parking
    Args:
        game_agent: model that trains and predicts next action
        iter: number of times car has run
    """
    global WIN
    window = WIN
    clock = pygame.time.Clock()
    reward = 0

    car = Car(200, random.randint(300,600), random.randint(0,90))
    goal = Goal(700, 350)
    obstacles = []
    obstacles.append(Obstacle(800,550,90))
    for i in range(1, 3):

        obstacles.append(Obstacle(700,100 + i * 180,0))

    old_state = np.array(game_agent.get_game_states(car, goal, [150] * 12))
    #next_action = [1,0,0,0,0,0]
    next_action = [1,0,0,0,0,0]
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
        #print("car x",car.x)
        #print("car y", car.y)
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
        car_parked = goal.collide(car)
        num_park = 0

        if car_parked:
            print("num_park: ", num_park)
            from datetime import datetime
            parked_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('sorted_source_text_iter' + str(iter) + '.txt', 'w') as file:
                file.write(parked_time)

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
            collision = line_length
            for j in range(0, line_length, 5):
                # car points
                point = (car.x - x_angle * j + car.image.get_width()/2,car.y + y_angle * j + car.image.get_height()/2)
                for obstacle in obstacles:
                    # get the corners of obstacle
                    obstacle_corners = obstacle.get_corners()
                    # check if car point in the obstacle rect
                    if point_in_rectangle(point, obstacle_corners):
                        collision = j
                        break
                    '''
                    # # old code before for collide point
                    # obstacle_rect = obstacle.image.get_rect(center = (obstacle.x + obstacle.image.get_width()/2, obstacle.y + obstacle.image.get_height()/2))
                    if obstacle_rect.collidepoint(point):
                        print("point", point, "in rect", obstacle_rect)
                        collision = j
                        break
                    '''

                if collision != 150:
                    break

            end_pos = (car.x - x_angle * line_length + car.image.get_width()/2, car.y + y_angle * line_length + car.image.get_height()/2)
            color = (0, 255, 255) if collision == 150 else (255, 0, 0)
            line = pygame.draw.line(window, color, start_pos, end_pos, 2)
            state_vectors.append(collision)


        car_center = (car.x + car.image.get_width()/2,car.y + car.image.get_height()/2)
        goal_center = (goal.x + goal.image.get_width()/2, goal.y + goal.image.get_height()/2)

        line = pygame.draw.line(window, (255,255,255), car_center, goal_center, 2)

        radians = car.angle / 180 * math.pi # direction car is facing
        x_angle = math.cos(radians)
        y_angle = math.sin(radians)

        # print("x_angle",x_angle)
        # print("y_angle",y_angle)
        #
        radians = car.angle * math.pi / 180
        # print("angle",car.angle)
        # print("right side angle",car.angle + 90)
        # print("left side angle",car.angle - 90)
        # print("radians",radians)
        #
        # print("right side radian",radians + math.pi/2)
        # print("left side radian",radians - math.pi/2)

        left_center = (car_center[0] + (math.cos((radians + math.pi/2)) * 25), car_center[1] - (math.sin((radians + math.pi/2)) * 25))
        right_center = (car_center[0] + math.cos(radians - math.pi/2) * 25, car_center[1] - math.sin(radians - math.pi/2) * 25)

        top_right = (right_center[0] + math.cos(radians) * 50, right_center[1] - math.sin(radians) * 50)
        bottom_right = (right_center[0] - math.cos(radians) * 50, right_center[1] + math.sin(radians) * 50)

        top_left = (left_center[0] + math.cos(radians) * 50, left_center[1] - math.sin(radians) * 50)
        bottom_left = (left_center[0] - math.cos(radians) * 50, left_center[1] + math.sin(radians) * 50)

        # x_angle = math.cos(radians)
        # y_angle = math.sin(radians)
        # bottom_right = (car.x + x_angle * 111.803, car.y + y_angle * 111.803)

        line = pygame.draw.line(window, (0,0,255), car_center, left_center, 5)
        line = pygame.draw.line(window, (255,0,0), car_center, right_center, 5)
        line = pygame.draw.line(window, (255,0,0), right_center, bottom_right, 5)
        line = pygame.draw.line(window, (255,0,0), right_center, top_right, 5)
        line = pygame.draw.line(window, (0,0,255), left_center, bottom_left, 5)
        line = pygame.draw.line(window, (0,0,255), left_center, top_left, 5)

        draw_colors = [(0,255,255),(255,0,255),(255,255,255)]
        i = 0
        for obstacle in obstacles:

            obstacle_rect = obstacle.get_corners()
            line = pygame.draw.line(window, draw_colors[i], obstacle_rect[0], obstacle_rect[2], 5)
            line = pygame.draw.line(window, draw_colors[i], obstacle_rect[1], obstacle_rect[3], 5)
            i+= 1

        pygame.display.update()

        # get game state
        game_state = np.array(game_agent.get_game_states(car, goal, state_vectors))
        # update model
        next_action = game_agent.predict(game_state, iter)
        # train model
        reward = game_agent.get_game_reward(car_crash, car_parked, old_state, game_state)
        game_agent.short_term_memory_trainer(old_state, next_action, reward, game_state, (car_crash or car_parked))
        game_agent.save_state_to_memory(old_state, next_action, reward, game_state, (car_crash or car_parked))

        # set old_state to current new_state
        old_state = game_state
        run = not(car_crash or car_parked)
        print("keep running",run)

    game_agent.train_from_replayed_memory()
    game_agent.model.save("model_4.h5")


def run(gamma=0.9, epsilon=0.2):

    game_agent = GameAgent(gamma, epsilon)

    iter = 0
    while True:
        print("iter", iter)
        result = play_game(game_agent, iter)
        iter += 1

if __name__ == '__main__':
    run()
