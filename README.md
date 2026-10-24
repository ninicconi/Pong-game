# Fuzzy Pong

A Pong game where the bottom paddle is controlled by a **fuzzy logic controller** instead of a human. The paddle sees how far the ball is (horizontally and vertically) and decides how fast to move left or right.

This is my solution for Task 4.1 (Fuzzy control) of the AI Fundamentals lab.

## The three controllers

| Mode | Method | What it does |
|---|---|---|
| `mamdani` | Mamdani inference | Follows the ball. Rules like "ball far left → move fast left"; the final speed is the centroid of the combined output shapes. |
| `tsk` | Takagi-Sugeno-Kang inference | Same behaviour, but each rule outputs a formula instead of a fuzzy set, and the speed is a weighted average. |
| `edge` | TSK with 15 rules | Aims to hit the ball with the **outer 25% of the paddle**. Each edge hit makes the ball 10% faster, until the opponent can't keep up. Uses the vertical distance to correct gently when the ball is far and firmly when it is close. |

The opponent (top paddle) is a simple "naive" player that always moves toward the ball.

## Requirements

- Python 3.13 or newer
- Libraries listed in `requirements.txt` (pygame-ce, scikit-fuzzy, numpy, scipy, networkx, matplotlib)

## Installation

```bash
pip install -r requirements.txt
```

## How to run

```bash
python Pong.py edge       
python Pong.py mamdani   
python Pong.py tsk       
```

Add `--plot` to see the membership functions before the game starts, for example `python Pong.py mamdani --plot`.
Press `Esc` to close the game.


## Files

| File | Description |
|---|---|
| `Pong.py` | The game and the three fuzzy controllers |
| `Benchmark.py` | Headless test that counts hits and misses |
| `requirements.txt` | Python libraries |

