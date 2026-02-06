import pyxel

import modules.unit
import modules.model

SCREEN_WIDTH  = 480
SCREEN_HEIGHT = 240
TRANSPARENT_COLOR = 2

class App:
    def __init__(self) -> None:
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="BOARD")
        pyxel.load("assets/resource.pyxres")
        pyxel.mouse(True)

        self.model = modules.model.Model()

        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # TODO: シーンと操作可能判定

        # マウス追従
        unit = self.model.mouse_over(pyxel.mouse_x, pyxel.mouse_y)
        if unit is None:
            # 以降の処理不要
            return

        # ユニット上でクリックされた
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and unit.is_player_unit():
            destinations = self.model.get_destinations(unit.ix, unit.iy)
            if 0 == len(destinations):
                return
            # シーンを変更
            pass # TODO




        #if pyxel.frame_count % 60 == 0:
        #    self.units.append(Unit())

    def draw(self) -> None:
        pyxel.cls(1)
        for unit in self.model.units:
            unit.draw()

App()
