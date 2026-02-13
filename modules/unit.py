from collections.abc import Callable
import math

import pyxel

from modules.config import Config

class Unit:
    def __init__(self, loc_idx: int, group_idx: int, on_state_change: Callable[[int], None]) -> None:
        self.loc_idx = loc_idx
        self.group_idx = group_idx
        self.on_state_change = on_state_change

        (self.x0, self.y0), _ = Config.get_xy(self.loc_idx)
        self.direction = 1 # 視線方向.1=右,-1=左

        self.anim_idx = 0
        self.t = pyxel.frame_count

        self.is_goaled = False
        self.is_source = False
        self.is_destination = False
        self._flight = []
        self._flight_end_idx = None


    @classmethod
    def init_player(cls, loc_idx: int, on_state_change: Callable[[int], None]) -> "Unit":
        return cls(loc_idx, Config.GROUP_PLAYER, on_state_change)

    @classmethod
    def init_cpu(cls, loc_idx: int, on_state_change: Callable[[int], None]) -> "Unit":
        return cls(loc_idx, Config.GROUP_CPU, on_state_change)

    @classmethod
    def init_field(cls, loc_idx: int, on_state_change: Callable[[int], None]) -> "Unit":
        return cls(loc_idx, Config.GROUP_FIELD, on_state_change)

    @classmethod
    def init_wall(cls, loc_idx: int, on_state_change: Callable[[int], None]) -> "Unit":
        return cls(loc_idx, Config.GROUP_WALL, on_state_change)

    def is_movable_player(self) -> bool:
        return not(self.is_goaled) and self.group_idx == Config.GROUP_PLAYER

    def is_player(self) -> bool:
        return self.group_idx == Config.GROUP_PLAYER

    def is_cpu(self) -> bool:
        return self.group_idx == Config.GROUP_CPU

    def is_field(self) -> bool:
        return self.group_idx == Config.GROUP_FIELD

    def is_wall(self) -> bool:
        return self.group_idx == Config.GROUP_WALL

    def move(self, parabola: list[tuple[int, int]], flight_end_idx: int) -> None:
        self._flight = parabola
        self._flight_end_idx = flight_end_idx

    def update(self, is_interact: bool) -> None:
        """
        戻り値: Trueのとき「選択された」
        """
        # 移動中
        if 0 < len(self._flight):
            self.x0, self.y0 = self._flight.pop(0)
            if 0 < len(self._flight):
                return

            # 到着した
            self.on_state_change(self._flight_end_idx)
            self._flight_end_idx = None
            return

        # interactに関わらないupdate処理
        if Config.is_animate(self.group_idx):
            self.anim_idx = ((pyxel.frame_count - self.t) % 40) // 5 # = {0,1,..,7}

        # 位置の初期化
        (x0, y0), (x1, y1) = Config.get_xy(self.loc_idx)
        self.x0, self.y0 = x0, y0

        # interact不可時は処理続行しない
        if not is_interact:
            return

        # 視線
        self.direction = 1 if x0 < pyxel.mouse_x else -1

        # 出発地の場合
        if self.is_source:
            self.x0 += pyxel.rndf(-2, 2)
            self.y0 += pyxel.rndf(-2, 2)

        # オンマウス
        if x0 <= pyxel.mouse_x < x1 and y0 <= pyxel.mouse_y < y1:
            # オンマウス状態の場合は、表示位置をブラす
            self.x0 += pyxel.rndf(-1, 1)
            self.y0 += pyxel.rndf(-1, 1)

            # オンマウス状態でクリックされた
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.on_state_change(self.loc_idx)

    def effect_update(self) -> bool:
        if 16 <= pyxel.frame_count - self.t:
            return True
        return False

    def draw(self) -> None:
        # DEBUG
        if Config.SHOW_NUMBER:
            (x, y), _ = Config.get_xy(self.loc_idx)
            pyxel.text(x, y, f"{self.loc_idx}", 15)

        if self.is_destination or self.is_source:
            (x, y), _ = Config.get_xy(self.loc_idx)
            c = Config.SELECTED_COLOR if self.is_source else Config.DESTINATION_COLOR
            pyxel.rectb(x, y, Config.CELL_SIZE, Config.CELL_SIZE, c)

        if self.group_idx == Config.GROUP_FIELD:
            return

        u, v = Config.get_uv(self.anim_idx, self.group_idx, self.is_goaled)
        w, h = Config.get_wh(self.direction)
        pyxel.blt(self.x0, self.y0, 0, u, v, w, h, Config.TRANSPARENT_COLOR)

    def effect_draw(self) -> None:
        bit = pyxel.frame_count - self.t
        (x, y), _ = Config.get_xy(self.loc_idx)
        u, v = Config.get_uv(self.anim_idx, self.group_idx, self.is_goaled)
        w, h = Config.get_wh(self.direction)
        pyxel.blt(x, y + bit, 0, u, v, w, h - bit, Config.TRANSPARENT_COLOR)
