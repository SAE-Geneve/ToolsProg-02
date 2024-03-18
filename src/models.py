from enum import IntEnum, unique
from peewee import *


@unique
class GameState(IntEnum):
    UNPLAYED = 0
    FINISHED = 1
    ABORTED = 2
    PLAYING = 4


db = PostgresqlDatabase('postgres', user='postgres', password='postgres', host='localhost')


class BaseModel(Model):
    class Meta:
        database = db


class Player(BaseModel):
    name = CharField()
    elo = IntegerField(default=0)


class Game(BaseModel):
    state = IntegerField(default=GameState.UNPLAYED)


class PlayerGame(BaseModel):
    player = ForeignKeyField(Player, backref="games")
    game = ForeignKeyField(Game, backref="players")

    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('player', 'game'), True),
        )

