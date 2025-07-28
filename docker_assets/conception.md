# Snake Game – Project Conception

## 🎯 Objective
A classic Snake game that runs in a Pygame window. Snake moves on a 2D grid, eats food, grows, and dies on self/wall collision.

## 🗂 Project Structure
```plaintext
/projects/snake/
│
├── main.py              # Entry point, Pygame loop
├── config.py            # Constants (colors, size, speed, etc.)
├── game.py              # Game loop logic and state management
├── snake.py             # Snake class definition
├── food.py              # Food class definition
│
├── assets/              # (Optional) Sounds, icons, sprites
│   ├── eat.wav
│   └── game_over.wav
│
├── workflow.md          # Build steps for the AI agent
└── conception.md        # Project structure and design
```

## 🧠 Module Summary

### `config.py`
```python
# Example content
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20
SPEED = 10
COLORS = {
    "background": (0, 0, 0),
    "snake": (0, 255, 0),
    "food": (255, 0, 0)
}
```

### `snake.py`
```python
class Snake:
    def __init__(self):
        self.body = [...]
        self.direction = ...
    
    def move(self):
        ...

    def grow(self):
        ...

    def check_collision(self):
        ...

    def draw(self, surface):
        ...
```

### `food.py`
```python
class Food:
    def __init__(self):
        self.position = self.random_position()
    
    def random_position(self):
        ...
    
    def draw(self, surface):
        ...
```

### `game.py`
```python
class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        ...

    def update(self):
        ...
    
    def draw(self):
        ...
    
    def reset(self):
        ...
```

### `main.py`
```python
# Initialize game window and loop
if __name__ == "__main__":
    pygame.init()
    ...
```

## ✅ Expected Behavior
- Arrow keys control the snake
- Snake grows after eating
- Game ends on collision
- Score displayed on screen
