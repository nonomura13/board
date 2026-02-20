import pyxel

class Config:
    SCREEN_WIDTH: int = 256
    SCREEN_HEIGHT: int = 256
    APP_TITLE: str = "PYONG"
    RESOURCE_PATH: str = "assets/resource.pyxres"

    CELL_SIZE: int = 16
    TRANSPARENT_COLOR: int = 2
    SELECTED_COLOR: int = 12
    DESTINATION_COLOR: int = 4

    N_X: int = 15
    N_Y: int =  9
    N_T: int =  5 # for territory x
    N_U: int =  9

    GROUP_FIELD: int = 0
    GROUP_PLAYER: int = 10
    GROUP_CPU: int = 20
    GROUP_WALL: int = 30
    GROUP_ONMOUSE: int = 90

    BANK_PLAYER_V: int =  0
    BANK_CPU_V: int    = 16
    BANK_WALL_V: int   = 32
    BANK_ONMOUSE_V: int = 96

    VECTORS = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(-1,-1),(1,-1)]

    @classmethod
    def get_xy(cls, loc_idx: int) -> tuple[int, int, int, int]:
        # 盤面の中心と盤面の端点
        cx = pyxel.floor(cls.SCREEN_WIDTH / 2)
        cy = pyxel.floor(cls.SCREEN_HEIGHT / 2)
        bx = pyxel.floor(cx - (cls.N_X * cls.CELL_SIZE / 2))
        by = pyxel.floor(cy - (cls.N_Y * cls.CELL_SIZE / 2))

        # 座標の計算
        ix, iy = loc_idx % cls.N_X, loc_idx // cls.N_X
        x = bx + ix * cls.CELL_SIZE
        y = by + iy * cls.CELL_SIZE

        return int(x), int(y), int(x + cls.CELL_SIZE), int(y + cls.CELL_SIZE)

    @classmethod
    def is_animate(cls, group_idx: int) -> bool:
        return group_idx in [cls.GROUP_PLAYER, cls.GROUP_CPU, cls.GROUP_WALL]

    @classmethod
    def get_uv(cls, group_idx: int, anim_idx: int, is_goaled: bool = False) -> tuple[int, int]:
        u = anim_idx * cls.CELL_SIZE
        if group_idx == cls.GROUP_ONMOUSE:
            v = cls.BANK_ONMOUSE_V
        elif group_idx == cls.GROUP_PLAYER:
            v = cls.BANK_PLAYER_V
        elif group_idx == cls.GROUP_CPU:
            v = cls.BANK_CPU_V
        else:
            v = cls.BANK_WALL_V

        if is_goaled:
            v += 16 * 4

        return u, v

    @classmethod
    def get_wh(cls, direction: int) -> tuple[int, int]:
        return direction * cls.CELL_SIZE, cls.CELL_SIZE

    @classmethod
    def in_field(cls, ix: int, iy: int) -> bool:
        return (0 <= ix < cls.N_X) and (0 <= iy < cls.N_Y)

    @classmethod
    def in_opponent_territory(cls, group_idx: int, loc_idx: int):
        is_player = group_idx == cls.GROUP_PLAYER
        is_cpu    = group_idx == cls.GROUP_CPU

        ix, iy = loc_idx % cls.N_X, loc_idx // cls.N_X

        if (is_player and cls.N_X - cls.N_T <= ix) \
        or (is_cpu and ix < cls.N_T):
            return True

        return False

    @classmethod
    def make_parabola(cls,
                      source_idx: int,
                      dest_idx: int,
                      n_parabolas: int = 30,
                      n_delays: int = 10) -> list[tuple[int, int]]:
        x0, y0, _, _ = cls.get_xy(source_idx)
        x1, y1_, _, _ = cls.get_xy(dest_idx)
        y1 = y0 - (y1_ - y0) # y座標の反転
        y_peak = max(y0, y1) + 30.0
        g = 9.8

        t_peak = pyxel.sqrt(2 * (y_peak - y0) / g)
        vy0 = g * t_peak
        a_quad = 0.5 * g
        b_quad = -vy0
        c_quad = y1 - y0
        T = (-b_quad + pyxel.sqrt(b_quad ** 2 - 4 * a_quad * c_quad)) / (2 * a_quad)
        vx0 = (x1 - x0) / T

        parabola = []
        for ti in range(n_parabolas):
            t = T * (ti / n_parabolas)
            x = x0 + vx0 * t
            y = y0 - vy0 * t + 0.5 * g * t ** 2
            parabola.append((x, y))
        parabola[-1] = (x1, y1_)

        # delay
        for _ in range(n_delays):
            parabola.append((x1, y1_))

        return parabola

    @classmethod
    def get_step_ids(cls, source_idx: int, dest_idx: int) -> list[int]:
        """source_idxとdest_idxをつなぐidx"""
        ix0, iy0 = source_idx % cls.N_X, source_idx // cls.N_X
        ix1, iy1 = dest_idx % cls.N_X, dest_idx // cls.N_X

        if ix0 == ix1: # 垂直方向
            return [
                iy * cls.N_X + ix0
                for iy in range(min(iy0, iy1), max(iy0, iy1))
            ]

        if iy0 == iy1: # 水平方向
            return [
                iy0 * cls.N_X + ix
                for ix in range(min(ix0, ix1), max(ix0, ix1))
            ]

        # ナナメ
        ids = []
        n = max(ix0, ix1) - min(ix0, ix1)
        vx = 1 if ix0 < ix1 else -1
        vy = 1 if iy0 < iy1 else -1
        for i in range(1,n):
            x = ix0 + i * vx
            y = iy0 + i * vy
            ids.append(y * cls.N_X + x)

        return ids
