from fastapi import APIRouter, Depends, HTTPException
from ..core.database import get_session
from sqlmodel import Session
from ..models.character import Character, CharacterCreate, CharacterRead

router = APIRouter()


@router.post('/character', status_code=201)
async def create_character(*, character: CharacterCreate, session: Session = Depends(get_session)):
    new_character = Character.from_orm(character)
    session.add(new_character)
    session.commit()
    session.refresh(new_character)
    return {'message': 'Character created successfully'}


@router.get('/character/{character_id}', response_model=CharacterRead)
async def get_character(*, character_id: int, session: Session = Depends(get_session)) -> CharacterRead:
    character = session.get(CharacterRead, character_id)
    if not character:
        raise HTTPException(404, 'Character not found')
    return character
