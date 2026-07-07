# Niskala - Reinforcement Learning Trading Agent
# DQN-based trading agent

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import random
import logging

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


@dataclass
class TradeAction:
    """Trading action"""
    action: int  # 0: hold, 1: buy, 2: sell
    confidence: float
    q_values: List[float]


if HAS_TORCH:
    class DQNetwork(nn.Module):
        """Deep Q-Network"""
        
        def __init__(self, state_size: int, action_size: int = 3):
            super().__init__()
            self.fc1 = nn.Linear(state_size, 128)
            self.fc2 = nn.Linear(128, 128)
            self.fc3 = nn.Linear(128, 64)
            self.fc4 = nn.Linear(64, action_size)
            self.relu = nn.ReLU()
        
        def forward(self, x):
            x = self.relu(self.fc1(x))
            x = self.relu(self.fc2(x))
            x = self.relu(self.fc3(x))
            return self.fc4(x)


class ReplayBuffer:
    """Experience replay buffer"""
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return np.array(states), actions, rewards, np.array(next_states), dones
    
    def __len__(self):
        return len(self.buffer)


class TradingEnvironment:
    """Trading environment for RL"""
    
    def __init__(self, data: np.ndarray, initial_capital: float = 100_000_000):
        self.data = data
        self.initial_capital = initial_capital
        self.reset()
    
    def reset(self):
        self.current_step = 0
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []
        self.total_reward = 0
        return self._get_state()
    
    def _get_state(self) -> np.ndarray:
        """Get current state"""
        if self.current_step >= len(self.data):
            return np.zeros(10)
        
        window = self.data[max(0, self.current_step-10):self.current_step+1]
        state = []
        
        # Price features
        if len(window) > 1:
            returns = np.diff(window[:, 3]) / window[:-1, 3]
            state.extend([np.mean(returns), np.std(returns)])
        else:
            state.extend([0, 0])
        
        # Current position
        state.append(self.position / 1000)
        
        # Capital ratio
        state.append(self.capital / self.initial_capital)
        
        # Technical indicators (simplified)
        if len(window) >= 20:
            close = window[:, 3]
            sma20 = np.mean(close[-20:])
            sma50 = np.mean(close[-50:]) if len(close) >= 50 else sma20
            state.extend([
                close[-1] / sma20 - 1,
                close[-1] / sma50 - 1,
                np.std(close[-20:]) / np.mean(close[-20:]),
            ])
        else:
            state.extend([0, 0, 0])
        
        # Pad to fixed size
        while len(state) < 10:
            state.append(0)
        
        return np.array(state[:10])
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """Execute action"""
        current_price = self.data[self.current_step, 3]
        reward = 0
        
        if action == 1 and self.position == 0:  # Buy
            shares = int(self.capital * 0.95 / current_price)
            self.position = shares
            self.capital -= shares * current_price
            reward = -0.001  # Small transaction cost
        
        elif action == 2 and self.position > 0:  # Sell
            self.capital += self.position * current_price
            pnl = (current_price - self.data[max(0, self.current_step-10), 3]) / self.data[max(0, self.current_step-10), 3]
            reward = pnl
            self.trades.append({'pnl': pnl, 'price': current_price})
            self.position = 0
        
        else:  # Hold
            if self.position > 0:
                price_change = (current_price - self.data[self.current_step-1, 3]) / self.data[self.current_step-1, 3]
                reward = price_change * 0.1  # Small reward for holding profitable position
        
        self.total_reward += reward
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1
        
        next_state = self._get_state()
        info = {
            'capital': self.capital,
            'position': self.position,
            'total_reward': self.total_reward,
            'trades': len(self.trades)
        }
        
        return next_state, reward, done, info


class TradingAgent:
    """DQN Trading Agent"""
    
    def __init__(self, state_size: int = 10, action_size: int = 3):
        self.state_size = state_size
        self.action_size = action_size
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.gamma = 0.99
        self.batch_size = 32
        self.memory = ReplayBuffer(10000)
        self.model = None
        self.target_model = None
        
        if HAS_TORCH:
            self.model = DQNetwork(state_size, action_size)
            self.target_model = DQNetwork(state_size, action_size)
            self.target_model.load_state_dict(self.model.state_dict())
            self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            self.criterion = nn.MSELoss()
        
        logger.info(f"TradingAgent initialized (state={state_size}, actions={action_size})")
    
    def act(self, state: np.ndarray) -> TradeAction:
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            action = random.randint(0, self.action_size - 1)
            return TradeAction(action=action, confidence=1.0 - self.epsilon, q_values=[0]*self.action_size)
        
        if not HAS_TORCH or self.model is None:
            action = random.randint(0, self.action_size - 1)
            return TradeAction(action=action, confidence=0.5, q_values=[0]*self.action_size)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.model(state_tensor).numpy()[0]
        
        action = np.argmax(q_values)
        confidence = float(np.max(q_values) - np.min(q_values)) / (abs(np.max(q_values)) + 1e-6)
        
        return TradeAction(
            action=int(action),
            confidence=min(confidence, 1.0),
            q_values=q_values.tolist()
        )
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
    
    def replay(self):
        """Train on replay buffer"""
        if len(self.memory) < self.batch_size or not HAS_TORCH or self.model is None:
            return
        
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)
        
        current_q = self.model(states).gather(1, actions.unsqueeze(1))
        next_q = self.target_model(next_states).max(1)[0].detach()
        target_q = rewards + (1 - dones) * self.gamma * next_q
        
        loss = self.criterion(current_q.squeeze(), target_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def update_target(self):
        """Update target network"""
        if self.model and self.target_model:
            self.target_model.load_state_dict(self.model.state_dict())
    
    def train(self, data: np.ndarray, episodes: int = 100) -> Dict:
        """Train agent on historical data"""
        env = TradingEnvironment(data)
        episode_rewards = []
        
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            
            while True:
                action = self.act(state)
                next_state, reward, done, info = env.step(action.action)
                
                self.remember(state, action.action, reward, next_state, done)
                self.replay()
                
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            episode_rewards.append(total_reward)
            
            if episode % 10 == 0:
                self.update_target()
                logger.info(f"Episode {episode}/{episodes} - Reward: {total_reward:.4f}, Epsilon: {self.epsilon:.4f}")
        
        return {
            'episode_rewards': episode_rewards,
            'final_reward': episode_rewards[-1] if episode_rewards else 0,
            'avg_reward': np.mean(episode_rewards[-10:]) if episode_rewards else 0,
            'trades': len(env.trades)
        }
    
    def save(self, path: str):
        """Save model"""
        if self.model and HAS_TORCH:
            torch.save({
                'model_state': self.model.state_dict(),
                'epsilon': self.epsilon,
            }, path)
    
    def load(self, path: str):
        """Load model"""
        if HAS_TORCH:
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['model_state'])
            self.epsilon = checkpoint['epsilon']
            self.update_target()
