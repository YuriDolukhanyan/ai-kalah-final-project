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
2. Install dependencies:
```bash
pip install -r requirements.txt
```

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
   - Minimax depth (1-8)
   - MCTS iterations (100-2000)
   - Board size (pits per row: 3-10)
   - Starting counters per pit (1-10)
3. **Single Game**: Play one game with visualization
4. **Batch Simulation**: Run multiple games (1-10000) and see statistics
5. **Statistics Display**: View win rates, average moves, score differences

### Example Configurations

- **Quick Test**: Random vs Random, 10 games
- **Algorithm Comparison**: Minimax (depth 4) vs MCTS (500 iterations), 1000 games
- **Strong Play**: Minimax (depth 5) vs MCTS (1000 iterations), 100 games

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
├── main.py            # Entry point
└── requirements.txt   # Dependencies
```

## Algorithms

### Minimax with Alpha-Beta Pruning
- Optimal play within search depth
- Configurable depth (recommended: 3-5)
- Uses heuristic evaluation function

### Monte Carlo Tree Search (MCTS)
- Good balance of strength and speed
- Configurable iterations (recommended: 200-1000)
- Uses UCT (Upper Confidence Bounds for Trees)

## Statistics

The application tracks:
- Win rates for each player
- Average game length (moves)
- Score differences
- Min/max statistics

## Development

To extend the project:
1. Add new agents in `src/agents/`
2. Implement `BaseAgent` interface
3. Register in `AgentFactory`
4. Add to GUI dropdown

## License

Educational project for AI course.


