from fastapi import FastAPI, Request, HTTPException
from peewee import *
from models import db, Player, Game, PlayerGame, GameState
from pydantic import BaseModel
from fastapi.testclient import TestClient

secret_token = "clown"

app = FastAPI()

with db:
    db.create_tables([Player, Game, PlayerGame])

class PlayerAPI(BaseModel):
    id: int
    name: str
    elo: int

class PlayerSearchAPI(BaseModel):
    id: int  | None = None
    name: str  | None = None

class GameAPI(BaseModel):
    id: int
    state: str

class GameSearchAPI(BaseModel):
    id: int | None = None

state = {GameState.UNPLAYED: "Unplayed", GameState.FINISHED: "Finished", GameState.ABORTED: "Aborted",
         GameState.PLAYING: "Playing"}


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

    return {"message": "Hello darkness, my old friend..."}

@app.post("/p/")
async def get_player(player: PlayerSearchAPI) -> PlayerAPI:
    if player.id is None and player.name is None:
        raise HTTPException(status_code=404, detail="Neither player id nor name was provided")
    if player.id is None:
        selected_player = Player.get(Player.name == player.name)
        return PlayerAPI(id=selected_player.get_id(), name=selected_player.name, elo=selected_player.elo)
    else:
        selected_player = Player.get_by_id(player.id)
        return PlayerAPI(id=selected_player.get_id(), name=selected_player.name, elo=selected_player.elo)

@app.get("/p/all")
async def get_players() -> list[PlayerAPI]:
    return [PlayerAPI(id=player.get_id(), name=player.name, elo=player.elo) for player in Player.select()]

@app.get("/p/get/{player_name}")
async def get_or_create_player(player_name: str) -> PlayerAPI:
    # get_or_create returns a tuple of (item, bool), [-2] to access the item, [-1] to access the bool
    potential_player = Player.get_or_create(name=player_name)[-2]
    return PlayerAPI(id=potential_player.get_id(), name=potential_player.name, elo=potential_player.elo)

@app.post("/g/")
async def get_game(game: GameSearchAPI) -> GameAPI:
    if game.id is None:
        raise HTTPException(status_code=404, detail="Game id was not provided")
    else:
        selected_game = Game.get_by_id(game.id)
        return GameAPI(id=selected_game.id, state=state[selected_game.state])

@app.get("/g/all")
async def get_games() -> list[GameAPI]:
    return [GameAPI(id=game.get_id(), state=state[game.state]) for game in Game.select()]

@app.get("/g/get/{game_id}")
async def get_or_create_game(game_id: int) -> GameAPI:
    # get_or_create returns a tuple of (item, bool), [-2] to access the item, [-1] to access the bool
    potential_game = Game.get_or_create(id=game_id)[-2]
    return GameAPI(id=potential_game.id, state=state[potential_game.state])

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/g/{game}")
async def get_input_from_game(game: str):
    pass

@app.get("/g/{game}/p/{player}")
async def get_input_from_game_and_player(game: str, player: str):
    pass

@app.get("/g/{game}/f/{frame}")
async def get_input_from_game_and_frame(game: str, frame: str):
    pass

client = TestClient(app)
def test_get_game():
    response = client.post(
        "/g/",
        headers={"X-Token": secret_token},
        json={"id": "1", "state": GameState.FINISHED.value}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "state": state[GameState.FINISHED.value]
    }