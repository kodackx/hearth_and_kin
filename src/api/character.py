from fastapi import APIRouter, Response, status
from ..core.database import Session, engine
from ..models.character import Character, CharacterCreate, CharacterRead

router = APIRouter()


@router.post('/character')
async def create_character(character: CharacterCreate, response: Response):
    with Session(engine) as session:
        new_character = Character.from_orm(character)
        session.add(new_character)
        session.commit()
        session.refresh(new_character)
        response.status_code = status.HTTP_201_CREATED
        return {'message': f'Character {character.character_id} created successfully'}


@router.get('/character/{character_id}', response_model=CharacterRead)
async def get_character(character_id: int):
    with Session(engine) as session:
        return session.get(Character, character_id)
