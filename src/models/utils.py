from fastapi import APIRouter, Response, status, Depends, HTTPException
from ..core.database import get_session
from ..models.story import Story
from ..models.character import Character
from ..models.user import User
from ..models.enums import TextModel, AudioModel, ImageModel
from sqlmodel import Session
from src.core.config import MODEL_CONFIGS
from ..core.config import logger
from typing import Dict, Tuple, Optional
from sqlmodel import select
from uuid import uuid4

def get_model_configs(story_id: int, session: Session) -> Dict[str, Dict[str, Optional[str]]]:
    """
    Get model configurations for a given story.

    Args:
    story_id (int): The ID of the story.
    session (Session): The database session.

    Returns:
    Dict[str, Dict[str, Optional[str]]]: A dictionary with keys 'text', 'audio', and 'image'.
    Each value is a dictionary containing 'model', 'api_key', and other relevant information.

    Raises:
    HTTPException: If the story is not found, or if a required API key is missing.
    """

    if not isinstance(session, Session):
        raise HTTPException(status_code=400, detail="[UTILS - get_model_configs] Session is not a valid SQLModel Session")
    
    story = session.get(Story, story_id)
    if not story:
        raise HTTPException(status_code=404, detail='Story not found')

    party_lead_character = session.get(Character, story.party_lead)
    if not party_lead_character:
        raise HTTPException(status_code=404, detail='Party lead character not found')

    party_lead_user = session.get(User, party_lead_character.user_id)
    if not party_lead_user:
        raise HTTPException(status_code=404, detail='Party lead user not found')

    configs = {
        'text': {'model': story.genai_text_model, 'api_key': None},
        'audio': {'model': story.genai_audio_model, 'api_key': None, 'voice_id': party_lead_user.elevenlabs_voice_id},
        'image': {'model': story.genai_image_model, 'api_key': None}
    }

    # Text model configuration
    if story.genai_text_model in [TextModel.gpto1, TextModel.gpt4o, TextModel.gpt]:
        if not party_lead_user.openai_api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is missing for the text model")
        configs['text']['api_key'] = party_lead_user.openai_api_key
    elif story.genai_text_model == TextModel.claude:
        if not party_lead_user.anthropic_api_key:
            raise HTTPException(status_code=400, detail="Anthropic API key is missing for the text model")
        configs['text']['api_key'] = party_lead_user.anthropic_api_key
    elif story.genai_text_model == TextModel.groq:
        if not party_lead_user.groq_api_key:
            raise HTTPException(status_code=400, detail="Groq API key is missing for the text model")
        configs['text']['api_key'] = party_lead_user.groq_api_key

    # Audio model configuration
    if story.genai_audio_model == AudioModel.elevenlabs:
        if not party_lead_user.elevenlabs_api_key:
            raise HTTPException(status_code=400, detail="ElevenLabs API key is missing for the audio model")
        configs['audio']['api_key'] = party_lead_user.elevenlabs_api_key

    # Image model configuration
    if story.genai_image_model == ImageModel.dalle3:
        if not party_lead_user.openai_api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is missing for the image model")
        configs['image']['api_key'] = party_lead_user.openai_api_key
    elif story.genai_image_model == ImageModel.stablediffusion:
        if not party_lead_user.stability_api_key:
            raise HTTPException(status_code=400, detail="Stability API key is missing for the image model")
        configs['image']['api_key'] = party_lead_user.stability_api_key

    return configs

def get_characters_for_story(story_id: int, session: Session = Depends(get_session)):
    if not isinstance(session, Session):
        raise HTTPException(status_code=400, detail="[UTILS - get_characters_for_story] Session is not a valid SQLModel Session")

    # First, retrieve the story
    story = session.get(Story, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Collect all character IDs associated with the story
    character_ids = [story.party_lead]
    if story.party_member_1:
        character_ids.append(story.party_member_1)
    if story.party_member_2:
        character_ids.append(story.party_member_2)

    # Query for all these characters
    characters = session.exec(
        select(Character).where(Character.character_id.in_(character_ids))
    ).all()

    return characters

def get_or_create_uuid(story_id: str, session: Session = Depends(get_session)) -> str:
    # If session is a Depends object, resolve it to get the actual session
    if not isinstance(session, Session):
        raise HTTPException(status_code=400, detail="[UTILS - get_or_create_uuid] Session is not a valid SQLModel Session")

    # Check if a UUID already exists for this story_id
    stmt = select(Story).where(Story.story_id == story_id)
    story = session.exec(stmt).first()
    
    if story and story.story_uuid:
        logger.debug(f'[UTILS - get_or_create_uuid] Found existing runnable UUID for story {story_id}: {story.story_uuid}')
        return story.story_uuid
    
    # If not, create a new UUID
    logger.debug(f'[UTILS - get_or_create_uuid] Creating new runnable UUID for story {story_id}')
    new_uuid = str(uuid4())
    
    if story:
        story.story_uuid = new_uuid
        session.add(story)
        session.commit()
    else:
        # Handle the case where the story doesn't exist
        logger.error(f"[UTILS - get_or_create_uuid] Story with id {story_id} not found")
        raise HTTPException(status_code=404, detail="Story not found")
    
    return new_uuid
