from collections.abc import Callable

from modules.config import Config
from modules.scene import Scene
from modules.unit import Unit

class Board:
    def __init__(self, on_turn_end: Callable[[None], None]) -> None:
        self.on_turn_end = on_turn_end
        self.units = self._init_units()
        self.current_scene = None

        self.source_idx = None
        self.dest_idx = None

    def _init_units(self) -> list[Unit]:
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


    def get_destination_ids(self, loc_idx: int) -> list[int]:
        ix, iy = loc_idx % Config.N_X, loc_idx // Config.N_X
        destination_ids = []
        for vx, vy in Config.VECTORS:
            x1, y1 = ix + vx, iy + vy
            while Config.in_field(x1, y1):
                idx_1 = x1 + y1 * Config.N_X
                if self.units[idx_1].is_field():
                    destination_ids.append(idx_1)
                    break
                x1 += vx
                y1 += vy

        return destination_ids

    def clear_destination_ids(self) -> None:
        for unit in self.units:
            unit.is_destination = False

    def judge(self) -> tuple[bool, str]:
        goaled_count = {'PLAYER': 0, 'CPU': 0}
        for unit in self.units:
            if unit.is_player() and unit.is_goaled:
                goaled_count['PLAYER'] += 1
            if unit.is_cpu() and unit.is_goaled:
                goaled_count['CPU'] += 1
        print(goaled_count)

        for winner, count in goaled_count.items():
            if count == Config.N_U:
                print('HERE. finished')
                return True, winner

        return False, ''

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
        #        self.effects.append(Unit.init_wall(idx, None))

        # j(dest)が相手の領域に到着した
        if Config.in_opponent_territory(self.units[j].group_idx, j):
            self.units[j].is_goaled = True

    def on_state_change(self, loc_idx: int) -> None:
        if self.current_scene.is_cpu():
            # CPUターン中のon state change == move end
            self.swap(self.source_idx, self.dest_idx)
            self.on_turn_end()
            return

        # CPUターンでない=プレイヤーターンである
        # 移動の終了を告げるモノ:
        if not self.current_scene.is_operable:
            self.swap(self.source_idx, self.dest_idx)
            self.source_idx = None
            self.dest_idx = None
            self.on_turn_end()
            return

        # 目的地を選択した
        if self.units[loc_idx].is_destination:
            # 移動処理
            self.dest_idx = loc_idx
            parabola = Config.make_parabola(self.source_idx, self.dest_idx)
            self.units[self.source_idx].move(parabola, self.dest_idx)

            # 選択中の描画を止める
            self.clear_destination_ids()

            # 操作を止める
            self.current_scene.is_operable = False
            return

        # 選択中でないプレイヤーユニットを選択した:
        if self.units[loc_idx].is_movable_player() \
        and loc_idx != self.source_idx:
            # 目的地の選択しなおし
            self.clear_destination_ids()
            destination_ids = self.get_destination_ids(loc_idx)
            self.source_idx = loc_idx
            for idx in destination_ids:
                self.units[idx].is_destination = True
            return

        # それ以外を選択した:
        self.source_idx = False
        self.clear_destination_ids()

    def update(self, scene: Scene) -> None:
        self.current_scene = scene
        for unit in self.units:
            unit.update(scene.is_operable)

    def draw(self) -> None:
        for unit in self.units:
            unit.draw()
