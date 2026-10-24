#!/usr/bin/env python3
# Based on https://python101.readthedocs.io/pl/latest/pygame/pong/#
import pygame
from typing import Type
import skfuzzy as fuzz
import skfuzzy.control as fuzzcontrol

FPS = 30


class Board:
    def __init__(self, width: int, height: int):
        self.surface = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption("AIFundamentals - PongGame")

    def draw(self, *args):
        background = (0, 0, 0)
        self.surface.fill(background)
        for drawable in args:
            drawable.draw_on(self.surface)

        pygame.display.update()


class Drawable:
    def __init__(self, x: int, y: int, width: int, height: int, color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.color = color
        self.surface = pygame.Surface(
            [width, height], pygame.SRCALPHA, 32
        ).convert_alpha()
        self.rect = self.surface.get_rect(x=x, y=y)

    def draw_on(self, surface):
        surface.blit(self.surface, self.rect)


class Ball(Drawable):
    def __init__(
        self,
        x: int,
        y: int,
        radius: int = 20,
        color=(255, 10, 0),
        speed: int = 3,
    ):
        super(Ball, self).__init__(x, y, radius, radius, color)
        pygame.draw.ellipse(self.surface, self.color, [0, 0, self.width, self.height])
        self.x_speed = speed
        self.y_speed = speed
        self.start_speed = speed
        self.start_x = x
        self.start_y = y
        self.start_color = color
        self.last_collision = 0

    def bounce_y(self):
        self.y_speed *= -1

    def bounce_x(self):
        self.x_speed *= -1

    def bounce_y_power(self):
        self.color = (
            self.color[0],
            self.color[1] + 10 if self.color[1] < 255 else self.color[1],
            self.color[2],
        )
        pygame.draw.ellipse(self.surface, self.color, [0, 0, self.width, self.height])
        self.x_speed *= 1.1
        self.y_speed *= 1.1
        self.bounce_y()

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.x_speed = self.start_speed
        self.y_speed = self.start_speed
        self.color = self.start_color
        self.bounce_y()

    def move(self, board: Board, *args):
        self.rect.x += round(self.x_speed)
        self.rect.y += round(self.y_speed)

        if self.rect.x < 0 or self.rect.x > (
            board.surface.get_width() - self.rect.width
        ):
            self.bounce_x()

        if self.rect.y < 0 or self.rect.y > (
            board.surface.get_height() - self.rect.height
        ):
            self.reset()

        timestamp = pygame.time.get_ticks()
        if timestamp - self.last_collision < FPS * 4:
            return

        for racket in args:
            if self.rect.colliderect(racket.rect):
                self.last_collision = pygame.time.get_ticks()
                if (self.rect.right < racket.rect.left + racket.rect.width // 4) or (
                    self.rect.left > racket.rect.right - racket.rect.width // 4
                ):
                    self.bounce_y_power()
                else:
                    self.bounce_y()


class Racket(Drawable):
    def __init__(
        self,
        x: int,
        y: int,
        width: int = 80,
        height: int = 20,
        color=(255, 255, 255),
        max_speed: int = 10,
    ):
        super(Racket, self).__init__(x, y, width, height, color)
        self.max_speed = max_speed
        self.surface.fill(color)

    def move(self, x: int, board: Board):
        delta = x - self.rect.x
        delta = self.max_speed if delta > self.max_speed else delta
        delta = -self.max_speed if delta < -self.max_speed else delta
        delta = 0 if (self.rect.x + delta) < 0 else delta
        delta = (
            0
            if (self.rect.x + self.width + delta) > board.surface.get_width()
            else delta
        )
        self.rect.x += delta


class Player:
    def __init__(self, racket: Racket, ball: Ball, board: Board) -> None:
        self.ball = ball
        self.racket = racket
        self.board = board

    def move(self, x: int):
        self.racket.move(x, self.board)

    def move_manual(self, x: int):
        """
        Do nothing, control is defined in derived classes
        """
        pass

    def act(self, x_diff: int, y_diff: int):
        """
        Do nothing, control is defined in derived classes
        """
        pass


class PongGame:
    def __init__(
        self, width: int, height: int, player1: Type[Player], player2: Type[Player]
    ):
        pygame.init()
        self.board = Board(width, height)
        self.fps_clock = pygame.time.Clock()
        self.ball = Ball(width // 2, height // 2)

        self.opponent_paddle = Racket(x=width // 2, y=0)
        self.oponent = player1(self.opponent_paddle, self.ball, self.board)

        self.player_paddle = Racket(x=width // 2, y=height - 20)
        self.player = player2(self.player_paddle, self.ball, self.board)

    def run(self):
        while not self.handle_events():
            self.ball.move(self.board, self.player_paddle, self.opponent_paddle)
            self.board.draw(
                self.ball,
                self.player_paddle,
                self.opponent_paddle,
            )
            self.oponent.act(
                self.oponent.racket.rect.centerx - self.ball.rect.centerx,
                self.oponent.racket.rect.centery - self.ball.rect.centery,
            )
            self.player.act(
                self.player.racket.rect.centerx - self.ball.rect.centerx,
                self.player.racket.rect.centery - self.ball.rect.centery,
            )
            self.fps_clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                return True
        keys = pygame.key.get_pressed()
        if keys[pygame.constants.K_LEFT]:
            self.player.move_manual(0)
        elif keys[pygame.constants.K_RIGHT]:
            self.player.move_manual(self.board.surface.get_width())
        return False


class NaiveOponent(Player):
    def __init__(self, racket: Racket, ball: Ball, board: Board):
        super(NaiveOponent, self).__init__(racket, ball, board)

    def act(self, x_diff: int, y_diff: int):
        x_cent = self.ball.rect.centerx
        self.move(x_cent)


class HumanPlayer(Player):
    def __init__(self, racket: Racket, ball: Ball, board: Board):
        super(HumanPlayer, self).__init__(racket, ball, board)

    def move_manual(self, x: int):
        self.move(x)


# ----------------------------------
# DO NOT MODIFY CODE ABOVE THIS LINE
# ----------------------------------

import sys
import numpy as np
import matplotlib.pyplot as plt

MAX_SPEED = 10



# Mamdani
class MamdaniPlayer(Player):
    """Follows the ball. Only x_diff is used. Fuzzy sets on both input and output."""

    def __init__(self, racket: Racket, ball: Ball, board: Board):
        super(MamdaniPlayer, self).__init__(racket, ball, board)

        # Antecedent (input) and Consequent (output) variables
        self.x_dist = fuzzcontrol.Antecedent(np.arange(-400, 401, 1), "x_dist")
        # NOTE: the output universe is deliberately WIDER than the paddle limit (+-10).
        # The centroid of a clipped "fast" set can never reach the edge of the universe,
        # so with a +-10 universe the paddle would only reach ~8 px/frame and fall behind
        # a fast ball. The Racket clips the final value to +-10 anyway.
        self.velocity = fuzzcontrol.Consequent(
            np.linspace(-15, 15, 301), "velocity", defuzzify_method="centroid"
        )

        # Input membership functions (named by where the BALL is relative to the paddle)
        self.x_dist["ball_far_left"] = fuzz.trapmf(self.x_dist.universe, [8, 20, 400, 400])
        self.x_dist["ball_left"] = fuzz.trimf(self.x_dist.universe, [0, 8, 20])
        self.x_dist["centered"] = fuzz.trimf(self.x_dist.universe, [-6, 0, 6])
        self.x_dist["ball_right"] = fuzz.trimf(self.x_dist.universe, [-20, -8, 0])
        self.x_dist["ball_far_right"] = fuzz.trapmf(self.x_dist.universe, [-400, -400, -20, -8])

        # Output membership functions
        v = self.velocity.universe
        self.velocity["fast_left"] = fuzz.trapmf(v, [-15, -15, -12, -8])
        self.velocity["slow_left"] = fuzz.trimf(v, [-10, -5, 0])
        self.velocity["stop"] = fuzz.trimf(v, [-2, 0, 2])
        self.velocity["slow_right"] = fuzz.trimf(v, [0, 5, 10])
        self.velocity["fast_right"] = fuzz.trapmf(v, [8, 12, 15, 15])

        # Rule base (Mamdani: the consequent is a fuzzy set)
        rules = [
            fuzzcontrol.Rule(self.x_dist["ball_far_left"], self.velocity["fast_left"]),
            fuzzcontrol.Rule(self.x_dist["ball_left"], self.velocity["slow_left"]),
            fuzzcontrol.Rule(self.x_dist["centered"], self.velocity["stop"]),
            fuzzcontrol.Rule(self.x_dist["ball_right"], self.velocity["slow_right"]),
            fuzzcontrol.Rule(self.x_dist["ball_far_right"], self.velocity["fast_right"]),
        ]
        self.racket_controller = fuzzcontrol.ControlSystem(rules)
        self.sim = fuzzcontrol.ControlSystemSimulation(self.racket_controller)

    def act(self, x_diff: int, y_diff: int):
        velocity = self.make_decision(x_diff, y_diff)
        self.move(round(self.racket.rect.x + velocity))

    def make_decision(self, x_diff: int, _y_diff: int):
        self.sim.input["x_dist"] = float(np.clip(x_diff, -400, 400))
        self.sim.compute()
        return float(np.clip(self.sim.output["velocity"], -MAX_SPEED, MAX_SPEED))

    def plot_membership_functions(self):
        self.x_dist.view()
        self.velocity.view()
        plt.show()


#  TSK (Takagi-Sugeno-Kang)

class TSKPlayer(Player):
    """Same behaviour as above, but the consequents are functions, not fuzzy sets."""

    def __init__(self, racket: Racket, ball: Ball, board: Board):
        super(TSKPlayer, self).__init__(racket, ball, board)

        self.x_universe = np.arange(-800, 801, 1)
        u = self.x_universe
        self.x_mf = {
            "ball_far_left": fuzz.trapmf(u, [8, 20, 800, 800]),
            "ball_left": fuzz.trimf(u, [0, 8, 20]),
            "centered": fuzz.trimf(u, [-6, 0, 6]),
            "ball_right": fuzz.trimf(u, [-20, -8, 0]),
            "ball_far_right": fuzz.trapmf(u, [-800, -800, -20, -8]),
        }

        # TSK consequents: crisp functions of the inputs
        self.velocity_fx = {
            "fast_left": lambda x_diff, y_diff: -MAX_SPEED,
            "slow_left": lambda x_diff, y_diff: -1.0 * x_diff,
            "stop": lambda x_diff, y_diff: 0.0,
            "slow_right": lambda x_diff, y_diff: -1.0 * x_diff,
            "fast_right": lambda x_diff, y_diff: MAX_SPEED,
        }
        # which fuzzy set of the input activates which consequent
        self.rule_map = {
            "ball_far_left": "fast_left",
            "ball_left": "slow_left",
            "centered": "stop",
            "ball_right": "slow_right",
            "ball_far_right": "fast_right",
        }

    def act(self, x_diff: int, y_diff: int):
        velocity = self.make_decision(x_diff, y_diff)
        self.move(round(self.racket.rect.x + velocity))

    def make_decision(self, x_diff: int, y_diff: int):
        x = float(np.clip(x_diff, -800, 800))
        activations = {
            name: float(fuzz.interp_membership(self.x_universe, mf, x))
            for name, mf in self.x_mf.items()
        }
        total = sum(activations.values())
        if total == 0:
            return 0.0
        # weighted average of the rule outputs
        out = sum(
            activations[s] * self.velocity_fx[self.rule_map[s]](x_diff, y_diff)
            for s in activations
        )
        return float(np.clip(out / total, -MAX_SPEED, MAX_SPEED))

    def plot_membership_functions(self):
        plt.figure()
        for name, mf in self.x_mf.items():
            plt.plot(self.x_universe, mf, label=name)
        plt.xlim(-100, 100)
        plt.xlabel("x_diff = racket_cx - ball_cx [px]")
        plt.legend()
        plt.show()


#  TSK, hits the ball with the EDGE of the paddle

class FuzzyPlayer(Player):

    AIM = 36

    def __init__(self, racket: Racket, ball: Ball, board: Board):
        super(FuzzyPlayer, self).__init__(racket, ball, board)

        # input 1: aiming error  e = x_diff - AIM  (e > 0: paddle is too far right)
        self.e_universe = np.arange(-800, 801, 1)
        e = self.e_universe
        self.e_mf = {
            "far_pos": fuzz.trapmf(e, [20, 60, 800, 800]),
            "pos": fuzz.trimf(e, [0, 10, 60]),
            "zero": fuzz.trimf(e, [-4, 0, 4]),
            "neg": fuzz.trimf(e, [-60, -10, 0]),
            "far_neg": fuzz.trapmf(e, [-800, -800, -60, -20]),
        }

        # input 2: vertical distance to the ball
        self.y_universe = np.arange(0, 801, 1)
        y = self.y_universe
        self.y_mf = {
            "near": fuzz.trapmf(y, [0, 0, 60, 140]),
            "mid": fuzz.trimf(y, [60, 140, 260]),
            "far": fuzz.trapmf(y, [140, 260, 800, 800]),
        }

        # TSK consequents: velocity = -gain * e  (gain depends on y), or saturated
        gain = {"near": 1.4, "mid": 1.0, "far": 0.8}

        def proportional(factor):
            # returns a function  velocity = -factor * e
            return lambda ex, ey: -factor * ex

        self.velocity_fx = {}
        for ys, k in gain.items():
            self.velocity_fx[("pos", ys)] = proportional(k)
            self.velocity_fx[("neg", ys)] = proportional(k)
            self.velocity_fx[("zero", ys)] = lambda ex, ey: 0.0
            self.velocity_fx[("far_pos", ys)] = lambda ex, ey: -MAX_SPEED
            self.velocity_fx[("far_neg", ys)] = lambda ex, ey: MAX_SPEED

    def act(self, x_diff: int, y_diff: int):
        velocity = self.make_decision(x_diff, y_diff)
        self.move(round(self.racket.rect.x + velocity))

    def make_decision(self, x_diff: int, y_diff: int):
        e_val = float(np.clip(x_diff - self.AIM, -800, 800))
        y_val = float(np.clip(y_diff, 0, 800))

        e_deg = {
            n: float(fuzz.interp_membership(self.e_universe, mf, e_val))
            for n, mf in self.e_mf.items()
        }
        y_deg = {
            n: float(fuzz.interp_membership(self.y_universe, mf, y_val))
            for n, mf in self.y_mf.items()
        }

        # rule activation with Zadeh norms: AND = min
        num = 0.0
        den = 0.0
        for (es, ys), fx in self.velocity_fx.items():
            w = min(e_deg[es], y_deg[ys])
            if w > 0.0:
                num += w * fx(e_val, y_val)
                den += w
        if den == 0.0:
            return 0.0
        return float(np.clip(num / den, -MAX_SPEED, MAX_SPEED))

    def plot_membership_functions(self):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        for name, mf in self.e_mf.items():
            axes[0].plot(self.e_universe, mf, label=name)
        axes[0].set_xlim(-100, 100)
        axes[0].set_title(f"aiming error e = x_diff - {self.AIM}  [px]")
        axes[0].legend()
        for name, mf in self.y_mf.items():
            axes[1].plot(self.y_universe, mf, label=name)
        axes[1].set_xlim(0, 400)
        axes[1].set_title("y_diff [px]")
        axes[1].legend()
        plt.tight_layout()
        plt.show()


PLAYERS = {"mamdani": MamdaniPlayer, "tsk": TSKPlayer, "edge": FuzzyPlayer}

if __name__ == "__main__":
    choice = next((a for a in sys.argv[1:] if a in PLAYERS), "edge")
    player_cls = PLAYERS[choice]
    game = PongGame(800, 400, NaiveOponent, player_cls)
    if "--plot" in sys.argv and hasattr(game.player, "plot_membership_functions"):
        game.player.plot_membership_functions()
    game.run()