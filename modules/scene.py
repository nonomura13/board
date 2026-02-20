import math

import pyxel
from modules.config import Config

class Scene:
    def __init__(self,
        name: str,
        belt_string: str,
        is_operable: bool,
        t_next: int = -1,
        next_scene: "Scene" = None,
    ) -> None:
        self.name = name
        self.belt_string = belt_string
        self.is_operable = is_operable
        self.t_next = t_next
        self.next_scene = next_scene

    @classmethod
    def player_splash(cls, t: int = 60) -> "Scene":
        return cls("SPLASH", "PLAYER TURN", False, pyxel.frame_count + t, cls.player)

    @classmethod
    def player(cls) -> "Scene":
        return cls("PLAYER", "PLAYTER TURN: SELECT UNIT", True)

    @classmethod
    def cpu_splash(cls, t: int = 60) -> "Scene":
        return cls("SPLASH", "CPU TURN", False, pyxel.frame_count + t, cls.cpu_think)

    @classmethod
    def cpu_think(cls) -> "Scene":
        return cls("CPUTHINK", "THINK", False)

    @classmethod
    def cpu(cls) -> "Scene":
        return cls("CPU", "CPU TURN", False)

    @classmethod
    def gameover_splash(cls, winner: str, t: int = 60) -> "Scene":
        return cls("SPLASH", f"GAME SET! {winner} WIN", False, pyxel.frame_count + t, cls.gameover)

    @classmethod
    def gameover(cls) -> "Scene":
        return cls("GAMEOVER", "GAME SET", False)

    def is_splash(self) -> bool:
        return self.name == "SPLASH"

    def is_cputhink(self) -> bool:
        return self.name == "CPUTHINK"

    def is_cpustep(self) -> bool:
        return self.name == "CPUSTEP"

    def is_cpuwait(self) -> bool:
        return self.name == "CPUWAIT"

    def is_cpu(self) -> bool:
        return self.name == "CPU"

    def is_player(self) -> bool:
        return self.name == "PLAYER"

    def is_gameover(self) -> bool:
        return self.name == "GAMEOVER"

    def update(self) -> "Scene":
        if self.t_next == pyxel.frame_count:
            return self.next_scene()
        return self

    def draw(self) -> None:
        def _belt_string(x: int, y: int, t: str, c0: int, c1: int) -> None:
            pyxel.rect(0, y, Config.SCREEN_WIDTH, 7, c0)
            pyxel.text(x + 1, y+1, t, c1)

        # DEBUG
        #pyxel.text(0, Config.SCREEN_HEIGHT - 7, f"{self.is_operable=}", 10)

        # splash screen
        if self.is_splash():
            t = (30 - (self.t_next - pyxel.frame_count)) / 10
            v = 10 * math.pow(0.5, t)
            _belt_string(v, 128, self.belt_string, 9, 10)
            return

        # 通常モード
        _belt_string(0, 0, self.belt_string, 9, 10)
