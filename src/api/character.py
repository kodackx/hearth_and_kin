from fastapi import APIRouter, Depends, HTTPException
from ..core.database import get_session
from sqlmodel import Session, select
from ..models.character import Character, CharacterRead, CharacterUpdate
from ..models.character import CharacterDetails
from ..models.story import Story
from ..core.config import logger
from typing import List

router = APIRouter()


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

# need to add a listing of all characters that the user has created
# Dummy function for getting the current user based on the token
# You need to replace this with your actual logic for retrieving the user
# async def get_current_user() -> User:
#     # Your logic here to get the user from the token
#     user_id = decode_token(token)  # Assuming a function to decode token and get user_id
#     user = session.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

@router.get('/characters', response_model=List[CharacterRead])
async def list_characters_for_user(current_user_id: int, session: Session = Depends(get_session)):
    statement = select(Character).where(Character.user_id == current_user_id)
    characters = session.exec(statement).all()
    return characters

@router.get('/story/{story_id}/characters', response_model=List[CharacterDetails])
async def get_story_characters(story_id: int, session: Session = Depends(get_session)):
    db_story = session.get(Story, story_id)
    if not db_story:
        raise HTTPException(404, 'Story not found')

    character_ids = [db_story.party_lead, db_story.party_member_1, db_story.party_member_2]
    characters = session.exec(select(Character).where(Character.character_id.in_(character_ids))).all()

    character_details = [
        CharacterDetails(character_id=char.character_id, character_name=char.character_name, portrait_path=char.portrait_path)
        for char in characters if char is not None
    ]

    return character_details

