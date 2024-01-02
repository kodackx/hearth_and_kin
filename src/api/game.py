from fastapi import APIRouter, Depends
from ..core.database import get_session
from sqlmodel import Session
from ..models.game import Game, GameCreate, GameRead

router = APIRouter()


@router.post('/game', status_code=201)
async def create_game(*, game: GameCreate, session: Session = Depends(get_session)) -> Game:
    new_game = Game.from_orm(game)
    session.add(new_game)
    session.commit()
    session.refresh(new_game)
    return new_game


@router.get('/game/{game_id}', response_model=GameRead)
async def get_game(*, game_id: int, session: Session = Depends(get_session)):
    return session.get(Game, game_id)
