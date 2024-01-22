from fastapi import APIRouter, Depends, HTTPException
from ..core.database import get_session
from sqlmodel import Session
from ..models.character import Character, CharacterCreate, CharacterRead, CharacterUpdate
from ..core.config import logger

router = APIRouter()


@router.post('/createcharacter', status_code=201, response_model=CharacterRead)
async def create_character(*, character_stats: CharacterCreate, session: Session = Depends(get_session)):
    try:
        new_character = Character.model_validate(character_stats)
        session.add(new_character)
        session.commit()
        session.refresh(new_character)
        logger.debug(f'[CREATECHARACTER] New character created with ID: {new_character.character_id}')
        response = {
            'character_id': new_character.character_id,
            'status': 'success'
        }
        return response
    except Exception as e:
        logger.error(f'[CREATECHARACTER] Failed to create character: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/character/{character_id}', response_model=CharacterRead)
async def get_character(*, character_id: int, session: Session = Depends(get_session)):
    character = session.get(Character, character_id)
    if not character:
        raise HTTPException(404, 'Character not found')
    logger.debug(f'[CHARACTER]: returned character {character}')
    return character


@router.patch('/character/{character_id}', status_code=201, response_model=CharacterRead)
async def update_character(*, character: CharacterUpdate, character_id: int, session: Session = Depends(get_session)):
    db_character = session.get(Character, character_id)
    if not db_character:
        raise HTTPException(404, 'Character not found')
    character_data = character.model_dump(exclude_unset=True)
    for key, value in character_data.items():
        setattr(db_character, key, value)
    session.add(db_character)
    session.commit()
    session.refresh(db_character)
    logger.debug(f'[CHARACTER]: updated character {db_character}')
    return db_character
