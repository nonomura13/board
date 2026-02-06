"""pyxelでイメージバンクが読み込まれている前提
"""

import pyxel

class Unit:
    PADDING_X: int = 0
    PADDING_Y: int = 0
    SIZE: int = 16
    TRANSPARENT_COLOR: int = 2

    GROUP_NULL: int = -1
    GROUP_PLANE: int = 0
    GROUP_PLAYER: int = 10
    GROUP_CPU: int = 20
    GROUP_WALL: int = 30

    SCENE_DEFAULT: int = 0
    SCENE_ONMOUSE: int = 1
    SCENE_SELECTED: int = 2
    SCENE_MOVING: int = 3
    SCENE_MOVEEND: int = 4

    VECTORS: list[tuple[int, int]] = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(-1,-1),(1,-1)]

    def __init__(self,
                 ix: int, iy: int, group_idx: int,
                 vectors: list[tuple[int, int]] = []) -> None:
        #self.t_start = pyxel.frame_count
        self.ix = ix
        self.iy = iy
        self.group_idx = group_idx
        self.on_mouse = False
        self.scene = self.SCENE_DEFAULT
        self.vectors = vectors

    def get_xy0(self) -> tuple[int, int]:
        x = self.PADDING_X + self.ix * self.SIZE
        y = self.PADDING_Y + self.iy * self.SIZE
        return x, y

    def get_xy01(self) -> list[tuple[int, int]]:
        x0, y0 = self.get_xy0()
        return [(x0, y0), (x0+self.SIZE, y0+self.SIZE)]

    @classmethod
    def init_null(cls, ix: int, iy: int) -> "Unit":
        return cls(ix, iy, cls.GROUP_NULL)

    @classmethod
    def init_player(cls, ix: int, iy: int) -> "Unit":
        return cls(ix, iy, cls.GROUP_PLAYER, cls.VECTORS)

    @classmethod
    def init_cpu(cls, ix: int, iy: int) -> "Unit":
        return cls(ix, iy, cls.GROUP_CPU, cls.VECTORS)

    @classmethod
    def init_wall(cls, ix: int, iy: int) -> "Unit":
        return cls(ix, iy, cls.GROUP_WALL)

    @classmethod
    def init_plane(cls, ix: int, iy: int) -> "Unit":
        return cls(ix, iy, cls.GROUP_PLANE)

    def is_player_unit(self) -> bool:
        return self.group_idx == self.GROUP_PLAYER

    def is_plane(self) -> bool:
        return self.group_idx == self.GROUP_PLANE

    def is_null(self) -> bool:
        return self.group_idx == self.GROUP_NULL

    def mouse_over(self, mouse_x: int, mouse_y: int) -> bool:
        (x0, y0), (x1, y1) = self.get_xy01()
        self.on_mouse = x0 <= mouse_x < x1 and y0 <= mouse_y < y1
        if self.on_mouse:
            self.scene = self.SCENE_ONMOUSE
        else:
            self.scene = self.SCENE_DEFAULT

    def draw(self) -> None:
        #i = ((pyxel.frame_count - self.t_start) % 16) // 2
        #pyxel.blt(self.x, self.y, 0, i * 16, 16, 16, 16, self.TRANSPARENT_COLOR)
        pyxel.rect(*self.get_xy0(), self.SIZE, self.SIZE, 1 + self.group_idx)

        if self.scene == self.SCENE_ONMOUSE:
            pyxel.rectb(*self.get_xy0(), self.SIZE, self.SIZE, 12)
