from fastapi import APIRouter, HTTPException, Depends, WebSocket, Query
from sqlmodel import Session, select

from src.models.character import Character

from ..core.websocket import WebsocketManager
from ..models.message import Message, MessageRead
from ..models.user import UserRead
from ..core.database import get_session
from ..models.story import Story, StoryCreate, StoryJoin, StoryDelete, StoryRead, StoryTransferOwnership
from ..models.story import StoryModelsUpdate
from ..models.story import Invite
from ..core.config import logger

router = APIRouter()
socket_manager = WebsocketManager()

# Manages WebSocket connections for the dashboard.
@router.websocket('/ws/dashboard')
async def dashboard_websocket(websocket: WebSocket):
    await socket_manager.endpoint(websocket, 0)

# Manages WebSocket connections for a specific story lobby, handling actions like new player joining and starting the game.
@router.websocket('/ws/lobby/{story_id}')
async def story_websocket(websocket: WebSocket, story_id: int):
    await socket_manager.endpoint(websocket, story_id)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get('action')
            if action == 'new_player':
                # Handle new player joining
                await socket_manager.broadcast('new_player', data, story_id)
            elif action == 'start_game':
                # Handle starting the game
                await socket_manager.broadcast('start_game', {}, story_id)
            elif action == 'player_online':
                # Handle existing player joining
                await socket_manager.broadcast('player_online', data, story_id)
    except Exception as e:
        socket_manager.disconnect(websocket, story_id)
        print("Some error occurred in the lobby websocket: " + repr(e))

# POST /story: Creates a new story and generates an invite code.
@router.post('/story', status_code=201)
async def create_story(*, story: StoryCreate, session: Session = Depends(get_session)):
    logger.debug(f"Received story data: {story}")
    new_story = Story(party_lead=story.party_lead)

    session.add(new_story)
    session.commit()
    session.refresh(new_story)

    # Generate invite code
    invite = Invite(story_id=new_story.story_id)
    session.add(invite)
    session.commit()
    session.refresh(invite)

    return {"story": {"story_id": new_story.story_id, "party_lead": new_story.party_lead}, "invite_code": invite.invite_code}

# DELETE /story/{story_id}: Deletes a story if the requesting character is the party lead.
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


# GET /stories: Retrieves a list of stories, optionally filtered by character ID.
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

# GET /story/{story_id}: Retrieves details of a specific story by its ID.
@router.get('/story/{story_id}', response_model=StoryRead)
async def get_story(*, story_id: int, session: Session = Depends(get_session)) -> StoryRead:
    db_story = session.get(Story, story_id)
    if db_story is None:
        raise HTTPException(404, 'Story not found')
    return db_story

# GET /story/{story_id}/messages: Retrieves messages associated with a specific story.
@router.get('/story/{story_id}/messages')
async def get_story_messages(*, story_id: int, session: Session = Depends(get_session)) -> list[MessageRead]:
    messages = session.exec(select(Message).where(Message.story_id == story_id)).all()
    return messages

# GET /story/{story_id}/invite: Retrieves the invite code for a specific story.
@router.get('/story/{story_id}/invite', response_model=str)
async def get_invite_code(story_id: int, session: Session = Depends(get_session)) -> str:
    invite = session.exec(select(Invite).where(Invite.story_id == story_id)).first()
    if not invite:
        raise HTTPException(404, 'Invite code not found for the given story_id')
    print(f'Invite code found below for story ID {story_id}:')
    print(invite.invite_code)
    return invite.invite_code

# POST /join_by_invite: Joins a story using an invite code.
@router.post('/join_by_invite', status_code=200)
async def join_by_invite(*, invite_code: str, session: Session = Depends(get_session)) -> StoryRead:
    print("This is the invite_code the API received:")
    print(invite_code)
    invite = session.exec(select(Invite).where(Invite.invite_code == invite_code)).first()
    if not invite:
        raise HTTPException(404, 'Invalid invite code')
    db_story = session.get(Story, invite.story_id)
    if not db_story:
        raise HTTPException(404, 'Story not found')
    return db_story

# POST /story/{story_id}/add_player: Adds a player to a story.
@router.post('/story/{story_id}/add_player')
async def add_player_to_story(*, story_join_data: StoryJoin, session: Session = Depends(get_session)) -> StoryRead:
    db_story = session.get(Story, story_join_data.story_id)
    db_character = session.get(Character, story_join_data.character_id)
    logger.debug(f'[STORY ID]: {db_story}')
    logger.debug(f'[CHARACTER ID]: {db_character}')
    if not db_story or not db_character:
        raise HTTPException(404, 'Story or character does not exist')

    if db_story.party_lead == db_character.character_id:
        db_story.has_started = True
    elif db_story.party_member_1 == db_character.character_id or db_story.party_member_2 == db_character.character_id:
        raise HTTPException(400, 'Character is already part of this adventure!')
    else:
        if db_story.party_member_1 is None:
            db_story.party_member_1 = db_character.character_id
        elif db_story.party_member_2 is None:
            db_story.party_member_2 = db_character.character_id
        else:
            raise HTTPException(400, 'Party is full!')

    session.add(db_story)
    session.commit()
    session.refresh(db_story)
    # await socket_manager.broadcast('new_player', StoryRead.model_validate(db_story), story_join_data.story_id)
    return db_story

# COSTI: I don't think this should exist. We either add players to a story party OR we manage the lobby
# POST /story/{story_id}/play: Allows a character to join the story lobby if they are part of the story.
# @router.post('/story/{story_id}/play')
# async def play_story(*, story_join_data: StoryJoin, session: Session = Depends(get_session)) -> StoryRead:
#     db_story = session.get(Story, story_join_data.story_id)
#     db_character = session.get(Character, story_join_data.character_id)
#     logger.debug(f'[STORY ID]: {db_story}')
#     logger.debug(f'[CHARACTER ID]: {db_character}')
#     if not db_story or not db_character:
#         raise HTTPException(404, 'Story or character does not exist')

#     if db_story.party_lead == db_character.character_id or db_story.party_member_1 == db_character.character_id or db_story.party_member_2 == db_character.character_id:
#         # Character is part of the story, proceed to join the lobby
#         await socket_manager.broadcast('player_joined_lobby', {'character_name': db_character.name}, story_join_data.story_id)
#     else:
#         raise HTTPException(400, 'Character is not part of the story.')

#     return db_story

# POST /story/{story_id}/leave: Allows a character to leave a story, except the party lead.
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

# POST /story/{story_id}/transfer_ownership: Transfers story ownership from the current lead to another member.
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

# POST /story/{story_id}/update_models: Updates the generative models for a story.
@router.post('/story/{story_id}/update_models', status_code=200, response_model=StoryRead)
async def update_story_models(story_id: int, models_update: StoryModelsUpdate, session: Session = Depends(get_session)):
    logger.info("Received this payload to update story models:")
    logger.info(str(models_update))
    
    db_story = session.get(Story, story_id)
    if not db_story:
        raise HTTPException(404, 'Story not found')

    current_character_id = models_update.character_id 
    if db_story.party_lead != current_character_id:
        raise HTTPException(403, 'Only the party lead can update the models')

    db_story.genai_text_model = models_update.genai_text_model
    db_story.genai_audio_model = models_update.genai_audio_model
    db_story.genai_image_model = models_update.genai_image_model

    session.add(db_story)
    session.commit()
    session.refresh(db_story)

    await socket_manager.broadcast('update_models', StoryRead.model_validate(db_story), story_id)
    return db_story
