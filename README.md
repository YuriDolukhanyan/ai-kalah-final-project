# Kalah Game AI Project

A Python implementation of the Kalah game with AI agents using Minimax (with Alpha-Beta Pruning) and Monte Carlo Tree Search (MCTS) algorithms.

## Features

- **Complete Kalah Game Implementation**: Full game rules including extra turns and captures
- **Multiple AI Agents**:
  - Random Agent (baseline)
  - Minimax with Alpha-Beta Pruning
  - Monte Carlo Tree Search (MCTS)
- **GUI Visualization**: Interactive board display with real-time updates
- **Batch Simulations**: Run 1000-10000 games and collect statistics
- **Statistics Tracking**: Win rates, average game length, score differences

## Installation

1. Clone or download this repository

Note: `tkinter` is usually included with Python. If not available, install it separately:
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- macOS: Should be included with Python
- Windows: Should be included with Python

## Usage

### Run the GUI Application

```bash
python main.py
```

### GUI Features

1. **Algorithm Selection**: Choose algorithms for South and North players
2. **Parameter Configuration**:
3. **Single Game**: Play one game with visualization
4. **Batch Simulation**: Run multiple games and see statistics
5. **Statistics Display**: View win rates, average moves, score differences

## Project Structure

```
Kalah/
├── src/
│   ├── game/          # Core game logic
│   ├── agents/        # AI agents
│   ├── evaluation/    # Heuristic functions
│   ├── simulation/    # Game runner and statistics
│   ├── gui/           # GUI components
│   └── utils/         # Utilities and constants
└── main.py            # Entry point
```

## License

Educational project for AI course.


