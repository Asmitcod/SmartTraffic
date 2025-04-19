Deployment link -->https://smarttraffic3-mhr6.onrender.com
Smart Traffic Management System-STOPLESS
A real-time, AI-powered smart traffic light control system that dynamically optimizes traffic flow based on vehicle density using reinforcement learning.

💡 Overview
Stopless is a web-based simulation of a Smart Traffic Management System built using:

Frontend: HTML, CSS, JavaScript

Backend: Python (Flask), Flask-SocketIO for real-time updates

AI Model: Deep Q-Learning (DQN) agent

Use Case: Efficient traffic light control at a 4-way intersection

The goal is to reduce congestion, waiting time, and improve traffic flow using intelligent decision-making.

🔧 Features
✅ Real-time traffic light simulation

🚗 Vehicle density detection (simulated)

🧠 Deep Reinforcement Learning for signal optimization

🔄 Adaptive signal control based on learned policies

📊 Live updates via WebSockets (Flask-SocketIO)

🌐 Accessible via browser (web-based interface)

🛠️ Technologies Used

Layer	Stack
Frontend	HTML, CSS, JavaScript
Backend	Python (Flask)
Realtime	Flask-SocketIO
AI Engine	TensorFlow/Keras + DQN algorithm
Simulation	Custom vehicle & signal simulation
🧠 How It Works
Vehicles are randomly generated at each lane.

The RL agent observes the environment (vehicle counts per lane).

It selects the best traffic light phase to minimize total waiting time.

Over time, it learns optimal patterns via rewards.

Updates are pushed to the frontend in real-time.
