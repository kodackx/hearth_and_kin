from fastapi import APIRouter, HTTPException, Depends, WebSocket, Query
from sqlmodel import Session, select

from src.models.character import Character

from ..core.websocket import WebsocketManager
from ..models.message import Message, MessageRead
from ..models.user import UserRead
from ..core.database import get_session
from ..models.story import Story, StoryCreate, StoryJoin, StoryDelete, StoryRead, StoryTransferOwnership
from ..core.config import logger

router = APIRouter()
socket_manager = WebsocketManager()

@router.websocket('/ws/dashboard')
async def dashboard_websocket(websocket: WebSocket):
    await socket_manager.endpoint(websocket, 0)


@router.post('/story', status_code=201)
async def create_story(*, story: StoryCreate, session: Session = Depends(get_session)) -> StoryCreate:
    logger.debug(f"Received story data: {story}")
    # db_story = session.get(Story, story.story_id)
    # if db_story is not None:
    #     raise HTTPException(400, 'Story already exists')
    new_story = Story(party_lead=story.party_lead)

    session.add(new_story)
    session.commit()
    session.refresh(new_story)
    return new_story


@router.delete('/story/{story_id}', status_code=200, response_model=StoryDelete)
async def delete_story(story_id: int, story: StoryDelete, session: Session = Depends(get_session)):
    statement = select(Story).where(Story.story_id == story_id).where(Story.party_lead == story.character_id)
    db_story = session.exec(statement).first()
    if not db_story:
        raise HTTPException(404, 'This character is not the party lead, therefore they cannot delete.')

    # Remove the story
    session.delete(db_story)
    session.commit()
    
    await socket_manager.broadcast('delete_story', story, story_id)
    return story



@router.get('/stories', response_model=list[StoryRead])
async def get_stories(character_id: int = Query(None), session: Session = Depends(get_session)):
    if character_id is not None:
        statement = select(Story).where(
            (Story.party_lead == character_id) |
            (Story.party_member_1 == character_id) |
            (Story.party_member_2 == character_id)
        )
        stories = session.exec(statement).all()
    else:
        stories = session.exec(select(Story)).all()
    
    # Log the results
    logger.debug(f'Returning stories for character_id={character_id}: {stories}')
    
    return stories


@router.get('/story/{story_id}', response_model=StoryRead)
async def get_story(*, story_id: int, session: Session = Depends(get_session)) -> StoryRead:
    db_story = session.get(Story, story_id)
    if db_story is None:
        raise HTTPException(404, 'Story not found')
    return db_story


@router.get('/story/{story_id}/messages')
async def get_story_messages(*, story_id: int, session: Session = Depends(get_session)) -> list[MessageRead]:
    messages = session.exec(select(Message).where(Message.story_id == story_id)).all()

    return messages


@router.post('/story/{story_id}/join')
async def join_story(*, story: StoryJoin, session: Session = Depends(get_session)) -> StoryJoin:
    db_story = session.get(Story, story.story_id)
    db_character = session.get(Character, story.character_id)

    if not db_story or not db_character:
        raise HTTPException(404, 'Story or character does not exist.')

    # Check for available member slots
    if db_story.party_member_1 is None:
        db_story.party_member_1 = db_character.character_id
    elif db_story.party_member_2 is None:
        db_story.party_member_2 = db_character.character_id
    else:
        raise HTTPException(400, 'No available slots in the story.')

    session.add(db_story)  # Make sure to add the updated story to the session
    session.commit()
    session.refresh(db_story)
    await socket_manager.broadcast('join_story', story, story.story_id)
    return story


@router.post('/story/{story_id}/play')
async def play_story(*, story_join_data: StoryJoin, session: Session = Depends(get_session)) -> StoryRead:
    db_story = session.get(Story, story_join_data.story_id)
    db_character = session.get(Character, story_join_data.character_id)
    logger.debug(f'[STORY ID]: {db_story}')
    logger.debug(f'[CHARACTER ID]: {db_character}')
    if not db_story or not db_character:
        raise HTTPException(404, 'Story or character does not exist')

    if db_story.party_lead != db_character.character_id:
        raise HTTPException(400, 'Only the party lead can initiate play.')

    db_story.has_started = True
    session.add(db_story)
    session.commit()
    session.refresh(db_story)
    await socket_manager.broadcast('play_story', StoryRead.model_validate(db_story), story_join_data.story_id)
    return db_story


@router.post('/story/{story_id}/leave')
async def leave_story(*, story: StoryJoin, session: Session = Depends(get_session)) -> StoryJoin:
    db_story = session.get(Story, story.story_id)
    db_character = session.get(Character, story.character_id)

    if not db_story or not db_character:
        raise HTTPException(404, 'Story or character does not exist')

    # Prevent the party lead from leaving the story
    if db_story.party_lead == db_character.character_id:
        raise HTTPException(400, 'Party lead cannot leave the story. They must delete it.')

    # Check if the character is part of the story and remove them
    if db_story.member_1 == db_character.character_id:
        db_story.member_1 = None
    elif db_story.member_2 == db_character.character_id:
        db_story.member_2 = None
    else:
        raise HTTPException(400, 'Character is not part of the story.')

    session.add(db_story)
    session.commit()
    session.refresh(db_story)
    await socket_manager.broadcast('leave_story', story, story.story_id)
    return story

@router.post('/story/{story_id}/transfer_ownership')
async def transfer_ownership(*, story: StoryTransferOwnership, session: Session = Depends(get_session)) -> StoryRead:
    db_story = session.get(Story, story.story_id)
    current_lead = session.get(Character, story.current_lead_id)
    new_lead = session.get(Character, story.new_lead_id)

    if not db_story or not current_lead or not new_lead:
        raise HTTPException(404, 'Story or character does not exist')

    if db_story.party_lead != current_lead.character_id:
        raise HTTPException(400, 'Only the current party lead can transfer ownership.')

    if new_lead.character_id not in [db_story.member_1, db_story.member_2]:
        raise HTTPException(400, 'The new lead must be a member of the story.')

    db_story.party_lead = new_lead.character_id
    session.add(db_story)
    session.commit()
    session.refresh(db_story)
    await socket_manager.broadcast('transfer_ownership', StoryRead.model_validate(db_story), story.story_id)
    return db_story
