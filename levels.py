from settings import (
    LEVEL_SPEED_SCALE, GOAL_WANDER_SLOW_SPEED, GOAL_WANDER_MEDIUM_SPEED,
)
from goal import Goal
from obstacles import Capsicum, NannyObstacle, MomObstacle, RandomObstacle

# Each level: goal movement type + list of obstacle specs (type, count).
#
# 1-7: only two obstacle types (capsicum + nanny), just growing in count as
# the maze (see maze.py) gets a bit more spacious level to level - still a
# corridor shape, never a full rectangle.
# 8-10: mom joins in force (2-3 of her chasing at once) inside a fully open
# rectangular arena - this is the hard tier.
LEVELS = {
    1: {
        "goal_movement": "static",
        "obstacles": [
            {"type": "capsicum", "count": 1},
        ],
    },
    2: {
        "goal_movement": "static",
        "obstacles": [
            {"type": "capsicum", "count": 1},
            {"type": "nanny", "count": 1},
        ],
    },
    3: {
        "goal_movement": "static",
        "obstacles": [
            {"type": "capsicum", "count": 2},
            {"type": "nanny", "count": 2},
        ],
    },
    4: {
        "goal_movement": "static",
        "obstacles": [
            {"type": "capsicum", "count": 2},
            {"type": "nanny", "count": 3},
        ],
    },
    5: {
        "goal_movement": "wander_slow",
        "obstacles": [
            {"type": "capsicum", "count": 3},
            {"type": "nanny", "count": 3},
        ],
    },
    6: {
        "goal_movement": "wander_slow",
        "obstacles": [
            {"type": "capsicum", "count": 3},
            {"type": "nanny", "count": 4},
        ],
    },
    7: {
        "goal_movement": "wander_medium",
        "obstacles": [
            {"type": "capsicum", "count": 4},
            {"type": "nanny", "count": 4},
        ],
    },
    8: {
        "goal_movement": "wander_medium",
        "obstacles": [
            {"type": "capsicum", "count": 3},
            {"type": "nanny", "count": 3},
            {"type": "mom", "count": 2},
        ],
    },
    9: {
        "goal_movement": "wander_medium",
        "obstacles": [
            {"type": "capsicum", "count": 3},
            {"type": "nanny", "count": 3},
            {"type": "mom", "count": 3},
        ],
    },
    10: {
        "goal_movement": "wander_medium",
        "obstacles": [
            {"type": "capsicum", "count": 4},
            {"type": "nanny", "count": 4},
            {"type": "mom", "count": 3},
            {"type": "random", "count": 2},
        ],
    },
}

TOTAL_LEVELS = len(LEVELS)


def build_goal(level_number):
    config = LEVELS[level_number]
    movement_key = config["goal_movement"]
    if movement_key == "wander_slow":
        return Goal(movement="wander", speed=GOAL_WANDER_SLOW_SPEED)
    elif movement_key == "wander_medium":
        return Goal(movement="wander", speed=GOAL_WANDER_MEDIUM_SPEED)
    return Goal(movement="static")


def build_obstacles(level_number):
    config = LEVELS[level_number]
    speed_mult = LEVEL_SPEED_SCALE.get(level_number, 1.0)
    obstacles = []
    for spec in config["obstacles"]:
        for _ in range(spec["count"]):
            if spec["type"] == "capsicum":
                obstacles.append(Capsicum(speed_mult))
            elif spec["type"] == "nanny":
                obstacles.append(NannyObstacle(speed_mult))
            elif spec["type"] == "mom":
                obstacles.append(MomObstacle(speed_mult))
            elif spec["type"] == "random":
                obstacles.append(RandomObstacle(speed_mult))
    return obstacles
