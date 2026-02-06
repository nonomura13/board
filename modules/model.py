import modules.unit as munit

class Model:
    def __init__(self) -> None:
        self.n_x, self.n_y = 9, 9
        self.n_t = 3
        self.units = self._init_units()

    def _init_units(self) -> list[munit.Unit]:
        """固定配置"""
        units = []

        # 非配置エリア
        null_ids = []
        for ix in range(self.n_t + 1):
            for iy in range(self.n_t + 1 - ix):
                null_ids.extend([
                    iy * self.n_x + ix,
                    (self.n_y - 1 - iy) * self.n_x + ix,
                    iy * self.n_x + self.n_x - 1 - ix,
                    (self.n_y - 1 - iy) * self.n_x + self.n_x - 1 - ix,
                ])

        # player/cpu
        player_ids, cpu_ids = [], []
        for ix in range(self.n_t):
            for iy in range(self.n_y):
                player_ids.append(iy * self.n_x + ix)
                cpu_ids.append(iy * self.n_x + self.n_x - 1 - ix)


        for loc_idx in range(self.n_x * self.n_y):
            ix = loc_idx %  self.n_x
            iy = loc_idx // self.n_x

            if loc_idx in null_ids:
                unit = munit.Unit.init_null(ix, iy)

            elif loc_idx in player_ids:
                unit = munit.Unit.init_player(ix, iy)

            elif loc_idx in cpu_ids:
                unit = munit.Unit.init_cpu(ix, iy)

            else:
                unit = munit.Unit.init_plane(ix, iy)
            units.append(unit)

        return units

    def mouse_over(self, mouse_x: int, mouse_y: int) -> None:
        ret_unit = None
        for unit in self.units:
            unit.mouse_over(mouse_x, mouse_y)
            if unit.on_mouse:
                ret_unit = unit
        return ret_unit

    def _in_field(self, ix: int, iy: int) -> bool:
        return (0 <= ix < self.n_x) and (0 <= iy < self.n_y)

    def get_destinations(self, ix: int, iy: int) -> list[int]:
        idx = ix + iy * self.n_x
        vectors = self.units[idx].vectors

        destinations = []
        for vx, vy in vectors:
            x1, y1 = ix + vx, iy + vy
            while self._in_field(x1, y1):
                idx_1 = x1 + y1 * self.n_x
                if self.units[idx_1].is_plane():
                    destinations.append(idx_1)
                    break
                if self.units[idx_1].is_null():
                    break
                x1 += vx
                y1 += vy

        return destinations
