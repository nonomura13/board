from collections.abc import Callable
import pyxel

from modules.config import Config

class Unit:
    def __init__(self, loc_idx: int, group_idx: int, on_state_change: Callable[[int], None]) -> None:
        self.loc_idx = loc_idx
        self.group_idx = group_idx
        self.on_state_change = on_state_change

        self.x0, self.y0, _, _ = Config.get_xy(self.loc_idx)
        self.direction = 1 # 視線方向. 1 = 右, -1 = 左
        self.anim_idx  = 0
        self.t = pyxel.rndi(0, 7)

        self.parabola = []
        self.move_end_idx = None

        self.on_mouseover = False

        self.is_goaled = False
        self.is_source = False
        self.is_destination = False

    def copy(self):
        return type(self)(
            self.loc_idx,
            self.group_idx,
            self.on_state_change,
        )

    @classmethod
    def init_player(cls, loc_idx: int, on_state_change) -> "Unit":
        return cls(loc_idx, Config.GROUP_PLAYER, on_state_change)

    @classmethod
    def init_cpu(cls, loc_idx: int, on_state_change) -> "Unit":
        return cls(loc_idx, Config.GROUP_CPU, on_state_change)

    @classmethod
    def init_field(cls, loc_idx: int, on_state_change) -> "Unit":
        return cls(loc_idx, Config.GROUP_FIELD, on_state_change)

    @classmethod
    def init_wall(cls, loc_idx: int, on_state_change) -> "Unit":
        return cls(loc_idx, Config.GROUP_WALL, on_state_change)

    def is_movable_player(self) -> bool:
        return not(self.is_goaled) and self.group_idx == Config.GROUP_PLAYER

    def is_player(self) -> bool:
        return self.group_idx == Config.GROUP_PLAYER

    def is_movable_cpu(self) -> bool:
        return not(self.is_goaled) and self.group_idx == Config.GROUP_CPU

    def is_cpu(self) -> bool:
        return self.group_idx == Config.GROUP_CPU

    def is_field(self) -> bool:
        return self.group_idx == Config.GROUP_FIELD

    def is_wall(self) -> bool:
        return self.group_idx == Config.GROUP_WALL

    def move(self, parabola: list[tuple[int, int]], move_end_idx: int) -> None:
        self.parabola = parabola
        self.move_end_idx = move_end_idx
        print(f"set parabola. {len(self.parabola)=}")

    def update(self, is_operable: bool) -> None:
        # アニメーション
        if Config.is_animate(self.group_idx):
            self.anim_idx = ((pyxel.frame_count - self.t) % 40) // 5 # = {0,1,..,7}

        # 移動中:
        if 0 < len(self.parabola):
            self.x0, self.y0 = self.parabola.pop(0)
            if 0 < len(self.parabola):
                return

            # 到着した
            self.on_state_change(self.move_end_idx)
            self.move_end_idx = None
            return

        # 位置の取得
        x0, y0, x1, y1 = Config.get_xy(self.loc_idx)

        # 視線
        self.direction = 1 if x0 < pyxel.mouse_x else -1

        # interact不可時は処理続行しない
        if not is_operable:
            return

        # オンマウス
        if x0 <= pyxel.mouse_x < x1 and y0 <= pyxel.mouse_y < y1:
            # オンマウス状態の場合は、表示位置をブラす
            self.x0 = x0 + pyxel.rndf(-1, 1)
            self.y0 = y0 + pyxel.rndf(-1, 1)

            # オンマウス状態でクリックされた
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.on_state_change(self.loc_idx)


    def draw(self) -> None:
        # DEBUG
        #x, y, _, _ = Config.get_xy(self.loc_idx)
        #pyxel.text(x, y, f"{self.loc_idx}", 15)

        if self.is_destination:
            anim_idx = (pyxel.frame_count % 8) // 1
            x, y, _, _ = Config.get_xy(self.loc_idx)
            u, v = Config.get_uv(Config.GROUP_ONMOUSE, anim_idx)
            w, h = Config.CELL_SIZE, Config.CELL_SIZE
            pyxel.blt(x, y, 0, u, v, w, h, Config.TRANSPARENT_COLOR)

        if self.group_idx == Config.GROUP_FIELD:
            return

        u, v = Config.get_uv(self.group_idx, self.anim_idx, self.is_goaled)
        w, h = Config.get_wh(self.direction)
        pyxel.blt(self.x0, self.y0, 0, u, v, w, h, Config.TRANSPARENT_COLOR)
