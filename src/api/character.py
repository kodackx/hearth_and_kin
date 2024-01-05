from fastapi import APIRouter, Depends, HTTPException
from ..core.database import get_session
from sqlmodel import Session
from ..models.character import Character, CharacterCreate, CharacterRead
from ..core.config import logger

router = APIRouter()


@router.post('/character', status_code=201, response_model=CharacterRead)
async def create_character(*, character: CharacterCreate, session: Session = Depends(get_session)):
    new_character = Character.from_orm(character)
    session.add(new_character)
    session.commit()
    session.refresh(new_character)
    return new_character


@router.get('/character/{character_id}', response_model=CharacterRead)
async def get_character(*, character_id: int, session: Session = Depends(get_session)):
    character = session.get(Character, character_id)
    if not character:
        raise HTTPException(404, 'Character not found')
    logger.debug(f'[CHARACTER]: returned character {character}')
    return character


@router.patch('/character/{character_id}', status_code=201, response_model=CharacterRead)
async def update_character(*, character: CharacterCreate, character_id: int, session: Session = Depends(get_session)):
    db_character = session.get(Character, character_id)
    if not db_character:
        raise HTTPException(404, 'Character not found')
    character_data = character.dict(exclude_unset=True)
    for key, value in character_data.items():
        setattr(db_character, key, value)
    session.add(db_character)
    session.commit()
    session.refresh(db_character)
    logger.debug(f'[CHARACTER]: updated character {db_character}')
    return db_character
