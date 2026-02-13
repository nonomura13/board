import math

import pyxel
from modules.config import Config

class Scene:
    def __init__(self,
                 name: str,
                 belt_string: str,
                 is_interact: bool,
                 t_next: int = -1,
                 winner: str = "",
                 next_scene: "Scene" = None) -> None:
        self.name = name
        self.belt_string = belt_string
        self.is_interact = is_interact
        self.t_next = t_next
        self.winner = winner
        self.next_scene = next_scene

    @classmethod
    def player_splash(cls, t: int = 60) -> "Scene":
        return cls("SPLASH SCREEN", "PLAYER TURN", False,
                   t_next = pyxel.frame_count + t,
                   next_scene = cls.player)

    @classmethod
    def cpu_splash(cls, t: int = 60) -> "Scene":
        return cls("SPLASH SCREEN", "CPU TURN", False,
                   t_next = pyxel.frame_count + t,
                   next_scene = cls.cpu)

    @classmethod
    def player(cls) -> "Scene":
        return cls("PLAYER", "SELECT UNIT", True)

    @classmethod
    def cpu(cls) -> "Scene":
        return cls("CPU", "THINKING", False)

    @classmethod
    def gameover_splash(cls, winner: str, t: int = 60) -> "Scene":
        return cls("SPLASH SCREEN", f"GAME SET! {winner} WIN", False,
                   t_next = pyxel.frame_count + t,
                   next_scene = cls.gameover)

    @classmethod
    def gameover(cls) -> "Scene":
        return cls("GAMEOVER", "GAME SET", True)

    def is_splash(self) -> bool:
        return self.name == "SPLASH SCREEN"

    def update(self) -> "Scene":
        if self.t_next == pyxel.frame_count:
            return self.next_scene()
        return self

    def draw(self) -> None:
        def _belt_string(x: int, y: int, t: str, c0: int, c1: int) -> None:
            pyxel.rect(0, y, Config.SCREEN_WIDTH, 7, c0)
            pyxel.text(x + 1, y+1, t, c1)

        # splash screen
        if self.is_splash():
            t = (30 - (self.t_next - pyxel.frame_count)) / 10
            v = 10 * math.pow(0.5, t)
            _belt_string(v, 128, self.belt_string, 9, 10)
            return

        # 通常モード
        _belt_string(0, 0, self.belt_string, 9, 10)
