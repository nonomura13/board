
from modules.config import Config
from modules.unit import Unit
from modules.board import Board

class CPU:
    def __init__(self) -> None:
        pass

    def _make_choices(self, board) -> list[tuple[int, int]]:
        # 移動可能なユニット
        movable_unit_ids = []
        for idx, unit in enumerate(board.units):
            if unit.is_movable_cpu():
                movable_unit_ids.append(idx)

        # 移動先の選定
        choices = []
        for idx in movable_unit_ids:
            destination_ids = board.get_destination_ids(idx)
            choices.extend([
                (idx, destination_idx)
                for destination_idx in destination_ids
            ])

        return choices

    def evaluate(self, units: list[Unit], i: int, j: int) -> tuple[int, int]:
        # 交換
        units[i], units[j] = units[j], units[i]

        # 評価
        dists = [0, 0] # Player, CPU
        for loc_idx, unit in enumerate(units):
            if unit.is_movable_cpu():
                # distance to territory
                ix = loc_idx % Config.N_X
                dist = ix - Config.N_T
                dists[1] += dist

            if unit.is_movable_player():
                ix = loc_idx % Config.N_X
                dist = Config.N_X - ix
                dists[0] += dist

        # 戻す
        units[i], units[j] = units[j], units[i]

        return tuple(dists)

    def command(self, board: Board) -> tuple[int, int]:
        choices = self._make_choices(board)

        # unitsの複写
        units = [unit.copy() for unit in board.units]

        # cpu
        dists = []
        for i, choice in enumerate(choices):
            d_p, d_c = self.evaluate(units, *choice)
            dists.append(d_c)
        min_dist = min(dists)
        min_ids = [idx for idx, d_c in enumerate(dists) if d_c == min_dist]


        return choices[min_ids[0]]
