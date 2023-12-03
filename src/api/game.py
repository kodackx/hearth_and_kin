from fastapi import APIRouter, Response, status
from ..core.database import Session, engine
from ..models.game import Game, GameCreate, GameRead

router = APIRouter()


@router.post('/game')
async def create_game(game: GameCreate, response: Response):
    with Session(engine) as session:
        new_game = Game.from_orm(game)
        session.add(new_game)
        session.commit()
        session.refresh(new_game)
        response.status_code = status.HTTP_201_CREATED
        return {'message': 'Game created successfully'}


@router.get('/game/{game_id}', response_model=GameRead)
async def get_game(game_id: int):
    with Session(engine) as session:
        return session.get(Game, game_id)
