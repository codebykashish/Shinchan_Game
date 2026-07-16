# Shinchan Arena Runner

A simple 2D maze game made with Python and pygame. You control Shinchan and
must reach Nanako while avoiding obstacles, across 10 levels.

## What you need

- Python 3.10 or newer installed on your computer. Get it from
  https://www.python.org/downloads/ if you don't have it (on Windows, check
  "Add python.exe to PATH" during install).
- The packages listed in `requirements.txt` (pygame, opencv-python, numpy,
  imageio-ffmpeg). You install these yourself in the steps below — they
  don't come with Python.

## Setup

1. Download or clone this project folder onto your computer.
2. Open a terminal in the project folder:
   - Windows: open the folder in File Explorer, click the address bar,
     type `cmd`, press Enter.
   - Mac/Linux: right-click the folder and choose "Open in Terminal", or
     `cd` into it from a terminal.
3. Check Python is installed:
   ```
   python --version
   ```
   This should print something like `Python 3.11.5`. If it says the command
   is not found, reinstall Python and make sure to add it to PATH.
4. (Optional but recommended) create a virtual environment, so these
   packages install only inside this project instead of system-wide:
   ```
   python -m venv venv
   ```
   Then activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
   You'll know it worked because your terminal line now starts with `(venv)`.
5. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   If `pip` is not recognized, use this instead:
   ```
   python -m pip install -r requirements.txt
   ```
   Wait for it to finish — it downloads pygame, opencv-python, numpy, and
   imageio-ffmpeg automatically. You do not need to install them one by one.

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
