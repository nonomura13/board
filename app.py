"""
cpu
"""
import pyxel

from modules.config import Config
from modules.scene import Scene
from modules.board import Board

class App:
    def __init__(self) -> None:
        pyxel.init(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT, title=Config.APP_TITLE)
        pyxel.load(Config.RESOURCE_PATH)
        pyxel.mouse(True)

        self.scene = Scene.player_splash()
        self.board = Board(self.on_player_turn_end)

        pyxel.run(self.update, self.draw)

    def on_player_turn_end(self) -> None:
        # 勝敗判定
        is_finished, winner = self.board.is_finished()

        #
        if is_finished:
            self.scene = Scene.gameover_splash(winner)
        else:
            self.scene = Scene.cpu_splash()

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_1):
            self.scene = Scene.cpu_splash()
            self.board.clear_destination_ids()

        if pyxel.btnp(pyxel.KEY_2):
            self.scene = Scene.player_splash()
            self.board.clear_destination_ids()

        if pyxel.btnp(pyxel.KEY_3):
            self.scene = Scene.gameover_splash("PLAYER")
            self.board.clear_destination_ids()

        self.scene = self.scene.update()
        # self.scene.is_interact
        self.board.update(self.scene.is_interact)

    def draw(self) -> None:
        pyxel.cls(1)

        vlines = Config.get_vlines()
        for x0, y0, x1, y1 in vlines:
            pyxel.line(x0, y0, x1, y1, 15)

        self.board.draw()
        self.scene.draw()

App()
