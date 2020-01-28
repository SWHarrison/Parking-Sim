from keras.optimizers import Adam
from keras.models import Sequential
from keras.models import load_model
from keras.layers.core import Dense, Dropout
import random
from random import sample
import numpy as np
import pandas as pd
from operator import add
import math


class GameAgent():

    def __init__(self, gamma, epsilon):
        """
        Setting up the RL model instances
        """
        # memory for the actions taken
        self.memory = list()
        # gamma is used for RL math behind the caculation
        self.gamma = gamma
        self.epsilon = epsilon
        self.learning_rate = 0.005
        self.reward = 0
        self.agent_target = 1
        self.agent_prediction = 0
        # self.model = self.create_model()
        self.model = load_model('model_2.h5')
        self.state = None


    def get_game_states(self, car, goal, sensors):

        STATE_VECTOR = sensors
        STATE_VECTOR.append(car.x)
        STATE_VECTOR.append(car.y)
        STATE_VECTOR.append(car.angle)
        STATE_VECTOR.append(car.speed)
        STATE_VECTOR.append(goal.x)
        STATE_VECTOR.append(goal.y)

        return STATE_VECTOR

    def predict(self, game_state, iter):

        rand_num = random.random()
        next_action = [0] * 6
        if(iter < 5):
            next_action[0] = 1
        elif rand_num < self.epsilon:
            next_action[random.randint(0,5)] = 1
        else:
            model_input = np.array([game_state.reshape(18,)])
            #print(model_input)
            #print("input shape:", model_input.shape)
            next_action = self.model.predict(model_input)[0]

        #print("next_action",next_action)
        return next_action


    def create_model(self):
        """ Method to create neural network architecture using optimized Keras models. """
        # input shape
        model = Sequential()
        model.add(Dense(120, activation="relu", input_shape=(18,)))
        model.add(Dropout(0.15))
        model.add(Dense(120, activation="relu"))
        model.add(Dropout(0.15))
        model.add(Dense(120, activation="relu"))
        model.add(Dropout(0.15))
        model.add(Dense(6, activation="softmax"))
        optimizer = Adam(self.learning_rate)
        model.compile(loss="mse", optimizer=optimizer)

        return model

    def get_game_reward(self, collision, parked, old_state, new_state):
        """Method to determine effective weights to reward or punish player activity."""
        self.reward = 0

        old_car_x = old_state[-3]
        old_car_y = old_state[-2]
        old_goal_x = old_state[-1]
        old_goal_y = old_state[-0]

        new_car_x = new_state[-3]
        new_car_y = new_state[-2]
        new_goal_x = new_state[-1]
        new_goal_y = new_state[-0]

        old_distance = math.sqrt((old_car_x - old_goal_x)**2 + (old_car_y - old_goal_y)**2)
        new_distance = math.sqrt((new_car_x - new_goal_x)**2 + (new_car_y - new_goal_y)**2)

        # reward if closer to goal than before
        if(old_distance > new_distance):
            self.reward += 1
            if new_distance < 200:
                self.reward * 20
            elif new_distance < 400:
                self.reward * 8
            elif new_distance < 800:
                self.reward * 2
        # else:
        #     self.reward -= 1

        # penalty if crashing
        if collision:
            self.reward -= 50
        # reward if parking
        elif parked:
            self.reward += 100

        return self.reward

    def save_state_to_memory(self, current_state, current_action, current_reward, next_state, stop):
        """ Method to save current detailed state to object's memory. """
        self.memory.append((current_state, current_action, current_reward, next_state, stop))

    def short_term_memory_trainer(self, current_state, current_action, current_reward, next_state, stop):
        """ Method to train short-term memory bank using detailed saved state info. """
        target_ = current_reward
        if not stop:
            target_ = current_reward + (self.gamma * np.amax(self.model.predict(next_state.reshape((1, 18)))[0]))
        target_final = self.model.predict(current_state.reshape((1, 18)))
        target_final[0][np.argmax(current_action)] = target_
        self.model.fit(current_state.reshape((1, 18)),target_final, epochs=1, verbose=0)

    def train_from_replayed_memory(self):
        """ Method to retrieve state details from object's memory bank. """

        memory_bank = self.memory
        if len(memory_bank) > 1000:
            batch = sample(memory_bank, 1000)
        else:
            batch = memory_bank
        for current_state, current_action, current_reward, next_state, stop in batch:
            target_ = current_reward
            if not stop:
                target_ = current_reward + (self.gamma * np.amax(self.model.predict(np.array([next_state]))[0]))
            target_final = self.model.predict(np.array([current_state]))
            target_final[0][np.argmax(current_action)] = target_
            self.model.fit(np.array([current_state]),
                           target_final, epochs=1, verbose=0)
