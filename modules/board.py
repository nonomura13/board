from collections.abc import Callable

from modules.config import Config
from modules.unit import Unit

class Board:
    def __init__(self, on_player_turn_end: Callable[[None], None]) -> None:
        self.on_player_turn_end = on_player_turn_end
        self.units = self._init_units()
        self.effects = [] # effect用
        self.is_interact = True
        self.source_idx = None
        self.dest_idx = None
        self.destination_ids = []

    def _init_units(self) -> list[Unit]:
        # prohibited area
        prohibited_ids = []
        for ix in range(Config.N_T + 1):
            for iy in range(Config.N_T + 1 - ix):
                prohibited_ids.extend([
                    iy * Config.N_X + ix,
                    (Config.N_Y - 1 - iy) * Config.N_X + ix,
                    iy * Config.N_X + Config.N_X - 1 - ix,
                    (Config.N_Y - 1 - iy) * Config.N_X + Config.N_X - 1 - ix,
                ])

        # player|cpu
        player_ids, cpu_ids = [], []
        for ix in range(Config.N_T):
            for iy in range(Config.N_Y):
                player_idx = iy * Config.N_X + ix
                if player_idx not in prohibited_ids:
                    player_ids.append(player_idx)

                cpu_idx = iy * Config.N_X + Config.N_X - 1 - ix
                if cpu_idx not in prohibited_ids:
                    cpu_ids.append(cpu_idx)

        # wall
        wall_ids = []
        if 0 < Config.N_T % 2:
            ix = Config.N_X // 2
            cy = Config.N_Y // 2
            for iy in range(cy - (Config.N_Y // 2) + 1, cy + Config.N_Y // 2):
                wall_idx = iy * Config.N_X + ix
                wall_ids.append(wall_idx)

        #
        units = []
        for loc_idx in range(Config.N_X * Config.N_Y):
            if loc_idx in player_ids:
                unit = Unit.init_player(loc_idx, self.on_state_change)
            elif loc_idx in cpu_ids:
                unit = Unit.init_cpu(loc_idx, self.on_state_change)
            elif loc_idx in wall_ids:
                unit = Unit.init_wall(loc_idx, self.on_state_change)
            else:
                unit = Unit.init_field(loc_idx, self.on_state_change)
            units.append(unit)

        return units

    def clear_destination_ids(self) -> None:
        if self.source_idx is not None:
            self.units[self.source_idx].is_source = False

        for idx in self.destination_ids:
            self.units[idx].is_destination = False

        self.destination_ids = []

    def set_destination_ids(self, loc_idx: int) -> None:
        self.units[loc_idx].is_source = True
        self.source_idx = loc_idx
        ix, iy = loc_idx % Config.N_X, loc_idx // Config.N_X

        self.destination_ids = []
        for vx, vy in Config.VECTORS:
            x1, y1 = ix + vx, iy + vy

            while Config.in_field(x1, y1):
                idx_1 = x1 + y1 * Config.N_X
                if self.units[idx_1].is_field():
                    self.units[idx_1].is_destination = True
                    self.destination_ids.append(idx_1)
                    break
                x1 += vx
                y1 += vy

    def swap(self, i: int, j: int) -> None:
        # 地点の交換
        self.units[i], self.units[j] = self.units[j], self.units[i]
        self.units[i].loc_idx = i
        self.units[j].loc_idx = j

        # 交換上にwallがあった場合は破壊する
        ids = Config.get_step_ids(i, j)
        for idx in ids:
            if self.units[idx].is_wall():
                self.units[idx] = Unit.init_field(idx, self.on_state_change)
                self.effects.append(Unit.init_wall(idx, None))

        # j(dest)が相手の領域に到着した
        if Config.in_opponent_territory(self.units[j].group_idx, j):
            self.units[j].is_goaled = True

    def is_finished(self) -> tuple[bool, str]:
        goaled_count = {'PLAYER': 0, 'CPU': 0}
        for unit in self.units:
            if unit.is_player() and unit.is_goaled:
                goaled_count['PLAYER'] += 1
            if unit.is_cpu() and unit.is_goaled:
                goaled_count['CPU'] += 1

        for winner, count in goaled_count.items():
            if count == Config.N_U:
                return True, winner

        return False, ''

    def on_state_change(self, loc_idx: int) -> None:
        # インタラクト禁止中にコールされた: 移動終了
        if not self.is_interact:
            # 置換
            self.swap(self.source_idx, self.dest_idx)
            self.clear_destination_ids()
            self.source_idx = None
            self.dest_idx = None

            # 終了を反映
            self.on_player_turn_end()

            self.is_interact = True
            return

        # loc_idxが操作できるplayerだ >> 移動先を決める
        if self.units[loc_idx].is_movable_player():
            if self.source_idx == loc_idx:
                self.clear_destination_ids()
                self.source_idx = None
                return

            self.clear_destination_ids()
            self.set_destination_ids(loc_idx)
            return

        # loc_idxが移動先
        if loc_idx in self.destination_ids:
            # unitの移動
            self.dest_idx = loc_idx
            parabola = Config.make_parabola(self.source_idx, loc_idx)
            self.units[self.source_idx].move(parabola, loc_idx)
            self.is_interact = False
            self.clear_destination_ids()


    def update(self, is_interact: bool) -> None:
        for unit in self.units:
            unit.update(is_interact & self.is_interact)

        # effect用の例外処理
        drop_ids = []
        for idx, unit in enumerate(self.effects):
            ret = unit.effect_update()
            if ret:
                drop_ids.append(idx)

        for idx in drop_ids[::-1]:
            self.effects.pop(idx)

    def draw(self) -> None:
        for unit in self.units:
            unit.draw()

        # effect用の例外処理
        for unit in self.effects:
            unit.effect_draw()
