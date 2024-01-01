from fastapi import APIRouter, HTTPException
from ..core.database import engine
from sqlmodel import Session
from ..models.character import Character, CharacterCreate, CharacterRead

router = APIRouter()


@router.post('/character', status_code=201)
async def create_character(character: CharacterCreate):
    with Session(engine) as session:
        new_character = Character.from_orm(character)
        session.add(new_character)
        session.commit()
        session.refresh(new_character)
        return {'message': 'Character created successfully'}


@router.get('/character/{character_id}', response_model=CharacterRead)
async def get_character(character_id: int) -> CharacterRead:
    with Session(engine) as session:
        character = session.get(CharacterRead, character_id)
        if not character:
            raise HTTPException(404, 'Character not found')
        return character
