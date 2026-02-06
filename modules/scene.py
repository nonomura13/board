"""シーン定義
"""
from datclasses import dataclass

@dataclass
class Scene:
    name: str
    t_start: int = 0
    message: str = ''

    @classmethod
    def splash(cls) -> "Scene":
        return cls('SPLASH SCREEN')

    @classmethod
    def player(cls) -> "Scene":
        return cls('PLAYER', message='SELECT UNIT')

    @classmethod
    def player_command(cls) -> "Scene":
        return cls('PLAYER_COMMAND', message='SELECT DESTINATION')
