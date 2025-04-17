from fastapi import FastAPI, Request
from peewee import *
from models import db, Player, Game, PlayerGame, GameState
from os import environ


app = FastAPI()



with db:
    db.create_tables([Player, Game, PlayerGame])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    db.connect()
    response = await call_next(request)
    db.close()
    return response


@app.get("/populate")
async def populate():
    player1 = Player(name="Player1")
    player2 = Player(name="Player2", elo=1000)
    player3 = Player(name="Player3", elo=2000)
    game1 = Game(state=GameState.FINISHED.value)
    game2 = Game(state=GameState.FINISHED.value)
    game3 = Game(state=GameState.FINISHED.value)
    game4 = Game(state=GameState.ABORTED.value)
    game5 = Game(state=GameState.PLAYING.value)

    entities = [player1, player2, player3, game1, game2, game3, game4, game5]
    [e.save() for e in entities]

    PlayerGame.create(player=player1, game=game1)
    PlayerGame.create(player=player2, game=game1)

    PlayerGame.create(player=player1, game=game2)
    PlayerGame.create(player=player2, game=game2)

    PlayerGame.create(player=player1, game=game3)
    PlayerGame.create(player=player3, game=game3)

    PlayerGame.create(player=player1, game=game4)
    PlayerGame.create(player=player3, game=game4)

    PlayerGame.create(player=player2, game=game5)
    PlayerGame.create(player=player3, game=game5)

    return {"message": "Done"}


@app.get("/")
async def root():
    for player in Player.select():
        print(player.name)

    query = Player.select().where(Player.elo > 500)
    for player in query:
        print(player.name, player.elo)

    query = (Player.select(Player.name)
             .join(PlayerGame, JOIN.LEFT_OUTER)
             .join(Game, JOIN.LEFT_OUTER)
             .where(Game.state == GameState.ABORTED.value)
             .group_by(Player.name)
             )
    for player in query:
        print(player.name)

    return {"message": "Hello Antoine"} 


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/g={game}")
async def get_input_from_game(game: str):
    pass
    

@app.get("/g={game}/p={player}")
async def get_input_from_game_and_player(game: str, player: str):
    pass

@app.get("/g={game}/f={frame}")
async def get_input_from_game_and_frame(game: str, frame: str):
    pass

@app.get("/p={player}")
async def get_input_from_game(player: str):
    pass
    

   