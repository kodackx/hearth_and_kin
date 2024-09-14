from fastapi import APIRouter, Response, status, Depends, HTTPException
from ..core.database import get_session
from ..models.enums import TextModel
from ..models.user import User
from sqlmodel import Session
from src.core.config import MODEL_CONFIGS
from ..core.config import logger

def get_text_models(model_name: str, party_lead_user_id: int, temperature: float = 0.5,  api_key: str = None, session: Session = Depends(get_session)):
    party_lead_user = session.get(User, party_lead_user_id)
    config = MODEL_CONFIGS[model_name]

    match model_name:
        case TextModel.gpt:
            logger.debug(f'[MESSAGE] Initializing chain using party lead API key {party_lead_user.openai_api_key}')
            text_model_api_key = party_lead_user.openai_api_key
        case TextModel.nvidia_llama:
            logger.debug(f'[MESSAGE] Initializing chain using party lead API key {party_lead_user.nvidia_api_key}')
            if party_lead_user.nvidia_api_key is None:
                raise HTTPException(400,'Party lead has no NVIDIA API key')
            text_model_api_key = party_lead_user.nvidia_api_key
        case TextModel.claude:
            logger.debug(f'[MESSAGE] Initializing chain using party lead API key {party_lead_user.anthropic_api_key}')
            if party_lead_user.anthropic_api_key is None:
                raise HTTPException(400,'Party lead has no Anthropic API key')
            text_model_api_key = party_lead_user.anthropic_api_key
        case _:
            text_model_api_key = ''
    
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model: {model_name}")
    
    return config['class'](model_name=config['model_name'], temperature=temperature, api_key=text_model_api_key)
