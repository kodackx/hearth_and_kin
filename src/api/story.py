from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from src.models.message import Message


from ..models.user import User, UserRead
from ..core.database import get_session
from ..models.story import Story, StoryCreate, StoryJoin, StoryDelete

router = APIRouter()


@router.post('/story', status_code=201)
async def create_story(*, story: StoryCreate, session: Session = Depends(get_session)):
    db_story = session.get(Story, story.story_id)
    if db_story is not None:
        raise HTTPException(400, 'Story already exists')
    new_story = Story(creator=story.creator, story_id=story.story_id)

    session.add(new_story)
    session.commit()
    session.refresh(new_story)
    return {'message': f'Story {story.story_id} created successfully'}


@router.delete('/story/{story_id}', status_code=200)
async def delete_story(*, story: StoryDelete, session: Session = Depends(get_session)):
    statement = select(Story).where(Story.story_id == story.story_id).where(Story.creator == story.username)
    db_story = session.exec(statement).first()

    if not db_story:
        raise HTTPException(404, 'Story created by user not found')

    users = session.exec(select(User).where(User.story_id == story.story_id)).all()
    # Kick out any users in story
    for user in users:
        user.story_id = None
        session.add(user)

    session.delete(db_story)
    session.commit()

    return {'message': 'Story deleted'}


@router.get('/stories')
async def get_stories(session: Session = Depends(get_session)):
    return session.exec(select(Story)).all()


@router.get('/story/{story_id}', response_model=Story)
async def get_story(*, story_id: int, session: Session = Depends(get_session)):
    return session.get(Story, story_id)


@router.get('/story/{story_id}/messages', response_model=list[Message])
async def get_story_messages(*, story_id: int, session: Session = Depends(get_session)):
    messages = session.exec(select(Message).where(Message.story_id == story_id)).all()

    return messages


@router.get('/story/{story_id}/users', response_model=list[UserRead])
async def get_story_users(*, session: Session = Depends(get_session), story_id: int):
    story = session.get(Story, story_id)
    if story:
        statement = select(User).where(User.story_id == story_id)
        return session.exec(statement).all()
    raise HTTPException(status_code=404, detail='Story not found')


@router.post('/story/{story_id}/join')
async def join_story(*, story: StoryJoin, session: Session = Depends(get_session)):
    db_story = session.get(Story, story.story_id)
    db_user = session.get(User, story.username)

    if not db_story or not db_user:
        raise HTTPException(404, 'Story or user does not exist')
    if db_user.story_id:
        raise HTTPException(400, 'User already in a story.')
    if db_story.active:
        raise HTTPException(400, 'Story is already in play.')

    db_user.story_id = db_story.story_id
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {'message': f'User {story.username} joined story {story.story_id}'}


@router.post('/story/{story_id}/play')
async def play_story(*, story: StoryJoin, session: Session = Depends(get_session)):
    db_story = session.get(Story, story.story_id)
    db_user = session.get(User, story.username)

    if not db_story or not db_user:
        raise HTTPException(404, 'Story or user does not exist')
    if db_user.story_id != db_story.story_id:
        raise HTTPException(400, 'User in different story.')
    if db_story.active:
        raise HTTPException(400, 'Story is already in play.')

    if not db_story.creator == db_user.username:
        raise HTTPException(400, 'Only story creator can play story.')
    db_story.active = True
    session.add(db_story)
    session.commit()
    session.refresh(db_story)
    return {'message': f'User {story.username} played story {story.story_id}'}


@router.post('/story/{story_id}/leave')
async def leave_story(*, story: StoryJoin, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == story.username).where(User.story_id == story.story_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(404, 'User does not exist in that story, or story does not exist')

    user.story_id = None
    session.add(user)
    session.commit()
    session.refresh(user)

    return {'message': f'User {story.username} left story {story.story_id}'}
