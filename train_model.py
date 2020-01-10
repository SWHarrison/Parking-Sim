from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from random import sample
import numpy as np
import pandas as pd
from operator import add


class GameAgent():
    
    def __init__(self):
        """
        Setting up the RL model instances
        """
        # memory for the actions taken
        self.memory = list()
        # gamma is used for RL math behind the caculation
        self.gamma = 0.9
        self.epsilon = 1.0
        self.learning_rate = 0.005
        self.reward = 0
        self.agent_target = 1
        self.agent_prediction = 0
        self.model = self.create_model()
        

    def get_game_states(self, car_instance, goal):
        
        STATE_VECTOR = [] 


    def create_model(self):
        """ Method to create neural network architecture using optimized Keras models. """
        # input shape 
        model = Sequential()
        model.add(Dense(120, activation="relu", input_shape=(11,)))
        model.add(Dropout(0.15))
        model.add(Dense(120, activation="relu"))
        model.add(Dropout(0.15))
        model.add(Dense(120, activation="relu"))
        model.add(Dropout(0.15))
        model.add(Dense(3, activation="softmax"))
        optimizer = Adam(self.learning_rate)
        model.compile(loss="mse", optimizer=optimizer)

        return model

    def get_game_reward(self, collision):
        """Method to determine effective weights to reward or punish player activity."""
        self.reward = 0
        if collision:
            self.reward -= 10
            return self.reward
        else:
            self.reward = 10
        return self.reward
