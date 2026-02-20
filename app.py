import pyxel

from modules.config import Config
from modules.scene import Scene
from modules.board import Board
from modules.cpu import CPU

class App:
    def __init__(self) -> None:
        pyxel.init(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT, title=Config.APP_TITLE)
        pyxel.load(Config.RESOURCE_PATH)
        pyxel.mouse(True)

        self.scene = Scene.player_splash()
        self.board = Board(self.on_turn_end)
        self.cpu = CPU()

        pyxel.run(self.update, self.draw)

    def on_turn_end(self) -> None:
        # 勝敗判定
        is_finished, winner = self.board.judge()
        #print('ON TURN END', is_finished, winner)

        if is_finished:
            self.scene = Scene.gameover_splash(winner)

        elif self.scene.is_player():
            self.scene = Scene.cpu_splash()

        else:
            self.scene = Scene.player_splash()

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_1):
            self.scene = Scene.player_splash()

        if pyxel.btnp(pyxel.KEY_2):
            self.scene = Scene.cpu_splash()

        if pyxel.btnp(pyxel.KEY_3):
            self.scene = Scene.gameover_splash('PLAYER')

        self.scene = self.scene.update()
        if self.scene.is_cputhink(): # splash直後
            # 移動ユニット, 移動先を決める
            source_idx, dest_idx = self.cpu.command(self.board)

            # 放物線
            parabola = Config.make_parabola(source_idx, dest_idx)

            # 放物線の設定
            self.board.source_idx = source_idx
            self.board.dest_idx = dest_idx
            self.board.units[source_idx].move(parabola, dest_idx)
            self.scene = Scene.cpu() # cpu状態にしてアニメーション終了を待つ

        self.board.update(self.scene)

        if self.scene.is_gameover() and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.board = Board(self.on_turn_end)
            self.scene = Scene.player_splash()

    def draw(self) -> None:
        pyxel.cls(1)

        self.board.draw()
        self.scene.draw()

App()
