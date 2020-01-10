from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from random import sample
import numpy as np
import pandas as pd
from operator import add
import math


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

    def get_game_reward(self, collision, old_state, new_state):
        """Method to determine effective weights to reward or punish player activity."""
        self.reward = 0
        
        distance = math.sqrt(((old_state.x**2)-(new_state**2)) - (()))
        if collision:
            self.reward -= 10
            return self.reward
        else:
            self.reward = 10
        return self.reward

    def save_state_to_memory(self, current_state, current_action, current_reward, next_state, stop):
        """ Method to save current detailed state to object's memory. """
        self.memory.append((current_state, current_action,
                            current_reward, next_state, stop))

    def short_term_memory_trainer(self, current_state, current_action, current_reward, next_state, stop):
        """ Method to train short-term memory bank using detailed saved state info. """
        target_ = current_reward
        if not stop:
            target_ = current_reward + \
                (self.gamma *
                 np.amax(self.model.predict(next_state.reshape((1, 11)))[0]))
        target_final = self.model.predict(current_state.reshape((1, 11)))
        target_final[0][np.argmax(current_action)] = target_
        self.model.fit(current_state.reshape((1, 11)),
                       target_final, epochs=1, verbose=0)

    def replay_from_memory(self, memory_bank):
        """ Method to retrieve state details from object's memory bank. """
        if len(memory_bank) > 1000:
            batch = sample(memory_bank, 1000)
        else:
            batch = memory_bank
        for current_state, current_action, current_reward, next_state, stop in batch:
            target_ = current_reward
            if not stop:
                target_ = current_reward + \
                    (self.gamma *
                     np.amax(self.model.predict(np.array([next_state]))[0]))
            target_final = self.model.predict(np.array([current_state]))
            target_final[0][np.argmax(current_action)] = target_
            self.model.fit(np.array([current_state]),
                           target_final, epochs=1, verbose=0)
