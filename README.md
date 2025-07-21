# Real-Time Robotic Arm with Hand Tracking

Built a fully programmable 3-axis robotic arm that responds in real time to live hand tracking data.

## Features
- Node.js hand tracking server (custom)
- Python + Socket.IO integration
- Dual ODrive BLDC motor control (X, Y, Z)
- Current-sensing soft-limit homing (no endstops)
- Dynamic PID tuning (stored in JSON)
- Pygame GUI overlay for debugging and metrics
- Zero AI-generated code – every line built, tested, and optimized manually

## Project Structure
- `main.py`: Launches everything – GUI, ODrive, socket connection
- `Callibration.py`: PID tuning, soft-limit logic, movement scaling
- `Support.py`: GUI utilities
- `pid_tuning.json`: Modular PID configuration per axis
- `SocketSupport.py`: Optional stand-alone socket listener
- `node_hand_server/`: External Node.js project for 3D hand tracking

## How to Run
1. Start the hand tracking server:
   ```bash
   node node_hand_server/index.js

