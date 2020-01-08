import pygame
import random
import os
import time
import math

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

    def __init__(self,x,y,angle = 0):

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

    def __init__(self,x,y,angle = 0):

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

        return car_mask.overlap(obstacle_mask,offset)

class Goal:

    def __init__(self,x,y,angle = 0):

        self.x = x
        self.y = y
        self.angle = angle
        self.image = pygame.transform.rotate(goal_img, self.angle)

    def draw(self, window):

        blitRotateCenter(window, self.image, (self.x, self.y), self.angle)

    def get_mask(self):

        return pygame.mask.from_surface(self.image)

    def collide(self, car, win):

        car_mask = car.get_mask()
        goal_mask = self.get_mask()

        offset = (int(self.x - car.x), int(self.y - car.y))

        return car_mask.overlap_area(car_mask,offset)


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    new_rect = image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(image, new_rect.topleft)

def draw_window(window, car, obstacles):

    window.blit(bg_img, (0,0))
    car.draw(window)

    olist = car.get_mask().outline()
    offset_list = []
    for value in olist:
        offset_list.append((int(value[0] + car.x),int(value[1] + car.y)))
    pygame.draw.lines(window,(0,0,255),1,offset_list)

    for obstacle in obstacles:
        olist = obstacle.get_mask().outline()
        offset_list = []
        for value in olist:
            offset_list.append((int(value[0] + obstacle.x),int(value[1] + obstacle.y)))
        obstacle.draw(window)
        pygame.draw.lines(window,(0,255,0),1,offset_list)

    pygame.display.update()

def play_game():
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global WIN
    window = WIN

    car = Car(400,400)
    car.accelerate()
    car.accelerate()
    #car.accelerate()
    clock = pygame.time.Clock()

    obstacles = []
    for i in range(1,4):

        obstacles.append(Obstacle(300*i,200*i,90))

    run = True
    while run:

        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        car.turn_left()

        car.move()

        for obstacle in obstacles:
            collision = obstacle.collide(car)
            if(collision):
                print(collision)
                print("car crash")
                return 0

        draw_window(window,car,obstacles)


def run():

    while True:
        play_game()

if __name__ == '__main__':
    run()
