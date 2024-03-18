from fastapi import APIRouter, HTTPException, Depends, WebSocket
from sqlmodel import Session, select

from src.models.character import Character

from ..core.websocket import WebsocketManager
from ..models.message import Message, MessageRead
from ..models.user import UserRead
from ..core.database import get_session
from ..models.story import Story, StoryCreate, StoryJoin, StoryDelete, StoryRead
from ..core.config import logger

router = APIRouter()
socket_manager = WebsocketManager()

@router.websocket('/ws/dashboard')
async def dashboard_websocket(websocket: WebSocket):
    await socket_manager.endpoint(websocket, 0)


@router.post('/story', status_code=201)
async def create_story(*,story: StoryCreate, session: Session = Depends(get_session)) -> StoryCreate:
    db_story = session.get(Story, story.story_id)
    if db_story is not None:
        raise HTTPException(400, 'Story already exists')
    new_story = Story(creator=story.creator, story_id=story.story_id)

    session.add(new_story)
    session.commit()
    session.refresh(new_story)
    await socket_manager.broadcast('create_story', StoryCreate.model_validate(new_story), 0)
    return new_story


@router.delete('/story/{story_id}', status_code=200, response_model=StoryDelete)
async def delete_story(*, story: StoryDelete, session: Session = Depends(get_session)):
    statement = select(Story).where(Story.story_id == story.story_id).where(Story.creator == story.character_id)
    db_story = session.exec(statement).first()

    if not db_story:
        raise HTTPException(404, 'This character was not the creator, therefore they cannot delete.')

    users = session.exec(select(Character).where(Character.story_id == story.story_id)).all()
    # Kick out any users in story
    for user in users:
        user.story_id = None
        session.add(user)

    session.delete(db_story)
    session.commit()
    # TODO: Story has no username field so cant implicitly cast to StoryDelete
    deleted_story = StoryDelete(story_id=story.story_id, character_id=story.character_id)
    await socket_manager.broadcast('delete_story', deleted_story, 0)
    return deleted_story



@router.get('/stories', response_model=list[StoryRead])
async def get_stories(session: Session = Depends(get_session)):
    return session.exec(select(Story)).all()


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


@router.get('/story/{story_id}/users', response_model=list[UserRead])
async def get_story_users(*, session: Session = Depends(get_session), story_id: int):
    story = session.get(Story, story_id)
    if story:
        statement = select(Character).where(Character.story_id == story_id)
        return session.exec(statement).all()
    raise HTTPException(status_code=404, detail='Story not found')


@router.post('/story/{story_id}/join')
async def join_story(*, story: StoryJoin, session: Session = Depends(get_session)) -> StoryJoin:
    db_story = session.get(Story, story.story_id)
    db_character = session.get(Character, story.character_id)

    if not db_story or not db_character:
        raise HTTPException(404, 'Story or character does not exist')
    if db_story.active:
        raise HTTPException(400, 'Story is already in play.')

    db_character.story_id = db_story.story_id
    session.add(db_character)
    session.add(db_story)  # Make sure to add the updated story to the session
    session.commit()
    session.refresh(db_character)
    await socket_manager.broadcast('join_story', story, 0)
    return story


@router.post('/story/{story_id}/play')
async def play_story(*, story: StoryJoin, session: Session = Depends(get_session)) -> StoryRead:
    db_story = session.get(Story, story.story_id)
    db_character = session.get(Character, story.character_id)
    logger.debug(f'[STORY]: {db_story}')
    logger.debug(f'[CHARACTER]: {db_character}')
    if not db_story or not db_character:
        raise HTTPException(404, 'Story or character does not exist')
    if db_character.story_id != db_story.story_id:
        raise HTTPException(400, 'Character in different story.')
    # if db_story.active:
    #    raise HTTPException(400, 'Story is already in play.')

    if not db_story.creator == db_character.character_id:
        raise HTTPException(400, 'Only story creator can play story.')
    db_story.active = True
    db_character.story_id = db_story.story_id
    session.add(db_story)
    session.add(db_character)
    session.commit()
    session.refresh(db_story)
    session.refresh(db_character)
    await socket_manager.broadcast('play_story', StoryRead.model_validate(db_story), 0)
    return db_story


@router.post('/story/{story_id}/leave')
async def leave_story(*, story: StoryJoin, session: Session = Depends(get_session)) -> StoryJoin:
    statement = select(Character).where(Character.character_id == story.character_id).where(Character.character_id == story.character_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(404, 'User does not exist in that story, or story does not exist')

    user.story_id = None
    session.add(user)
    session.commit()
    session.refresh(user)
    await socket_manager.broadcast('leave_story', StoryJoin.model_validate(story), 0)
    return story
