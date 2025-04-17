from os import environ
from enum import IntEnum, unique
from peewee import *
from dotenv import load_dotenv

load_dotenv()


@unique
class GameState(IntEnum):
    UNPLAYED = 0
    FINISHED = 1
    ABORTED = 2
    PLAYING = 4


db = PostgresqlDatabase(environ.get("DB_NAME","localhost"), user=environ.get("DB_USER"), password=environ.get("DB_PASS"), host=environ.get("DB_HOST"))


class BaseModel(Model):
    class Meta:
        database = db


class Player(BaseModel):
    name = CharField(unique=True)
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

class Input(BaseModel):
    frame = IntegerField(default=0)
    input = IntegerField(default=0)
    player_game = ForeignKeyField(PlayerGame, backref="inputs")

