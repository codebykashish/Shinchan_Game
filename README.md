# Shinchan Arena Runner

A simple 2D maze game made with Python and pygame. You control Shinchan and
must reach Nanako while avoiding obstacles, across 10 levels.

## What you need

- Python 3.10 or newer installed on your computer
- The packages listed in `requirements.txt` (pygame, opencv-python, numpy,
  imageio-ffmpeg)

## Setup

1. Download or clone this project folder.
2. Open a terminal in the project folder.
3. (Optional but recommended) create a virtual environment:
   ```
   python -m venv venv
   ```
   Then activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## How to run the game

```
python main.py
```

## Controls

- Arrow keys or WASD: move Shinchan
- ENTER: start the game / continue after a meme screen / advance a level
- R: restart after game over or after winning
- ESC: quit the game

## How to play

- Move Shinchan through the maze to reach Nanako (the goal).
- Avoid the obstacles (capsicum, nanny, mom). Touching one shows a meme
  screen and costs you a life.
- You have 4 lives. If you run out, it's game over and you can press R to
  restart.
- Reach Nanako to complete a level and move to the next one.
- There are 10 levels in total. Beat all of them to win.
