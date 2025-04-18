import eventlet
eventlet.monkey_patch()

# Then import other modules
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import numpy as np
import random
import time
import os
import collections
import json
from collections import deque

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'traffic-simulation-secret'
socketio = SocketIO(app, async_mode='eventlet')

# Traffic Environment
class TrafficEnvironment:
    def __init__(self):
        # Traffic directions: North, South, East, West
        self.directions = ['North', 'South', 'East', 'West']
        
        # Traffic light states (0: Red, 1: Green)
        self.light_states = {direction: 0 for direction in self.directions}
        
        # Queue of cars in each direction (max 10 cars per direction)
        self.queues = {direction: 0 for direction in self.directions}
        
        # Stats
        self.total_waiting_time = 0
        self.cars_passed = 0
        self.step_count = 0
        self.episode_count = 0
        
        # Initial light state (North-South green, East-West red)
        self.light_states['North'] = 1
        self.light_states['South'] = 1
        
        # History
        self.action_history = []
        self.reward_history = []
        
        # Initial state
        self.update_queues()
    
    def get_state(self):
        # State is a tuple of queue lengths and light states
        queue_state = tuple(self.queues[direction] for direction in self.directions)
        light_state = tuple(self.light_states[direction] for direction in self.directions)
        return queue_state + light_state
    
    def get_state_for_nn(self):
        # Convert state to array for neural network
        queue_state = [self.queues[direction] for direction in self.directions]
        light_state = [self.light_states[direction] for direction in self.directions]
        return np.array(queue_state + light_state)
    
    def update_queues(self):
        # Randomly add cars to queues
        for direction in self.directions:
            if self.queues[direction] < 10:  # Max 10 cars per direction
                new_cars = random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0]
                self.queues[direction] = min(10, self.queues[direction] + new_cars)
        
        # Cars pass through green lights
        for direction in self.directions:
            if self.light_states[direction] == 1 and self.queues[direction] > 0:
                cars_passing = min(self.queues[direction], 2)  # Up to 2 cars can pass per step
                self.queues[direction] -= cars_passing
                self.cars_passed += cars_passing
    
    def calculate_waiting_time(self):
        # Calculate total waiting time (1 unit per car per time step)
        waiting_time = sum(self.queues.values())
        self.total_waiting_time += waiting_time
        return waiting_time
    
    def reset(self):
        # Reset environment
        self.light_states = {direction: 0 for direction in self.directions}
        self.queues = {direction: 0 for direction in self.directions}
        self.total_waiting_time = 0
        self.cars_passed = 0
        self.step_count = 0
        self.episode_count += 1
        
        # Initial light state (North-South green, East-West red)
        self.light_states['North'] = 1
        self.light_states['South'] = 1
        
        # Action history
        self.action_history = []
        self.reward_history = []
        
        # Initial state
        self.update_queues()
        return self.get_state_for_nn()
    
    def step(self, action):
        self.step_count += 1
        
        # Action: 0 - Keep current light state, 1 - Switch North-South/East-West
        if action == 1:
            for direction in self.directions:
                self.light_states[direction] = 1 - self.light_states[direction]
        
        # Record action
        action_str = "Keep" if action == 0 else "Switch"
        self.action_history.append(action_str)
        
        # Update queues
        self.update_queues()
        
        # Calculate reward (negative waiting time)
        waiting_time = self.calculate_waiting_time()
        reward = -waiting_time
        
        # Record reward
        self.reward_history.append(reward)
        
        # Check if episode is done (fixed length episodes)
        done = self.step_count >= 50
        
        return self.get_state_for_nn(), reward, done, {
            'waiting_time': waiting_time,
            'cars_passed': self.cars_passed,
            'queues': self.queues,
            'lights': self.light_states
        }

# DQN Agent
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
    
    def _build_model(self):
        # Simplified Q-table (No neural network)
        return np.zeros((1000, self.action_size))  # Q-table size (simplified)
    
    def update_target_model(self):
        # Update target model with weights from model
        self.target_model = np.copy(self.model)
    
    def remember(self, state, action, reward, next_state, done):
        state_idx = hash(tuple(state)) % 1000
        next_state_idx = hash(tuple(next_state)) % 1000
        self.memory.append((state_idx, action, reward, next_state_idx, done))
    
    def act(self, state):
        state_idx = hash(tuple(state)) % 1000
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        return np.argmax(self.model[state_idx])
    
    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        for state_idx, action, reward, next_state_idx, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.target_model[next_state_idx])
            
            self.model[state_idx, action] = target
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def load(self, filename):
                try:
                    self.model = np.load(filename)
                    print(f"Model loaded from {filename}")
                except FileNotFoundError:
                    print(f"No model found at {filename}. Initializing a new model.")
                    self.model = self._build_model()  # Initialize a new model if the file is not found
                except Exception as e:
                    print(f"Error loading model from {filename}: {e}")

    def save(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        np.save(filename, self.model)
        print(f"Model saved to {filename}")

# Initialize environment and agent
env = TrafficEnvironment()
state_size = 8  # 4 queue lengths + 4 light states
action_size = 2  # Keep or switch
agent = DQNAgent(state_size, action_size)

# Try to load saved model
filename = "models/q_table.npy"
if not os.path.exists('models'):
    os.makedirs('models')

# Check if the model file exists before loading
if os.path.exists(filename):
    agent.load(filename)
else:
    print(f"No model found at {filename}. A new model will be created.")

# Global variables
is_training = False
simulation_running = False
 
@app.after_request
def set_permissions_policy(response):
    # You can remove this line if not needed
    response.headers['Permissions-Policy'] = 'interest-cohort=()'
    return response


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
@socketio.on('disconnect')
def handle_disconnect():
    global simulation_running
    simulation_running = False
    print('Client disconnected')

@socketio.on('start_simulation')
def start_simulation(data):
    global simulation_running
    simulation_running = True
    global is_training
    is_training = data.get('training', False)
    socketio.start_background_task(simulate_traffic)

@socketio.on('stop_simulation')
def stop_simulation():
    global simulation_running
    simulation_running = False

@socketio.on('reset_simulation')
def reset_simulation():
    global env, simulation_running
    simulation_running = False
    env = TrafficEnvironment()
    socketio.emit('simulation_reset')

@socketio.on('toggle_training')
def toggle_training(data):
    global is_training
    is_training = data.get('training', False)
    socketio.emit('training_status', {'training': is_training})

def simulate_traffic():
    global simulation_running, is_training
    state = env.reset()
    done = False
    batch_size = 32
    episode_rewards = []
    
    while simulation_running:
        action = agent.act(state)
        next_state, reward, done, info = env.step(action)
        episode_rewards.append(reward)
        
        if is_training:
            agent.remember(state, action, reward, next_state, done)
        
        socketio.emit('update_ui', {
            'episode': env.episode_count,
            'step': env.step_count,
            'action': "Keep" if action == 0 else "Switch",
            'reward': round(reward, 2),
            'waiting_time': info['waiting_time'],
            'cars_passed': info['cars_passed'],
            'queues': info['queues'],
            'lights': info['lights'],
            'epsilon': round(agent.epsilon, 4),
            'training': is_training
        })
        
        state = next_state
        
        if done:
            avg_reward = sum(episode_rewards) / len(episode_rewards)
            socketio.emit('episode_summary', {
                'episode': env.episode_count,
                'avg_reward': round(avg_reward, 2),
                'total_waiting_time': env.total_waiting_time,
                'cars_passed': env.cars_passed,
                'action_history': env.action_history
            })
            
            if is_training:
                agent.replay(min(batch_size, len(agent.memory)))
                agent.update_target_model()
                agent.save("models/q_table.npy")
            
            state = env.reset()
            episode_rewards = []
        
        eventlet.sleep(0.5)
    
    print("Simulation stopped")
if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('models'):
            os.makedirs('models')
        socketio.run(app, debug=True, host='127.0.0.1', port=5000)
