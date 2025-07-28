# Snake Game – Development Workflow

## 1. Setup Environment
- Create the directory `/projects/snake`
- Initialize a new Python project:
  - `$ cd /projects/snake`
  - `$ python -m venv .venv`
  - `$ source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
  - `$ pip install pygame`

## 2. Create Base Game Files
- Create entry point file: `main.py`
- Create supporting files: `game.py`, `snake.py`, `food.py`, `config.py`
- Create `assets/` folder for visuals/sound (optional)

## 3. Implement Core Modules
### 3.1 `config.py`
- Define screen dimensions, colors, speed, grid size, etc.

### 3.2 `snake.py`
- Define Snake class
  - `body`: list of positions
  - `direction`: movement vector
  - `move()`, `grow()`, `check_collision()`, `reset()`

### 3.3 `food.py`
- Define Food class
  - Random position generator
  - `draw()`

### 3.4 `game.py`
- Main game class
  - Handles state: snake, food, score, game over logic

## 4. Implement `main.py`
- Initialize Pygame
- Create game loop
  - Event handling (keyboard input)
  - Update state
  - Render everything
  - Handle game over

## 5. Test Functionality
- Run the game
- Confirm:
  - Snake moves and grows
  - Food respawns
  - Game ends on wall/self collision

## 6. Polish and Finalize
- Add sounds and/or basic sprites (optional)
- Add score display
- Add restart-on-death feature
- Clean up code with comments

## 7. Save and Exit
- Final check-in to version control (if used)
- Leave `.venv` out of any commits
