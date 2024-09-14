import logging
from dotenv import load_dotenv
from ..models.enums import AudioModel, ImageModel, TextModel
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

DEBUG = True

DEFAULT_TEXT_NARRATOR_MODEL = TextModel.gpt
DEFAULT_AUDIO_NARRATOR_MODEL = AudioModel.elevenlabs
DEFAULT_IMAGE_MODEL = ImageModel.dalle3
SENTENCES_PER_SUBTITLE = 2
logger = logging.getLogger(__name__)

load_dotenv()
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

MODEL_CONFIGS = {
    'gpt': {'class': ChatOpenAI, 'model_name': 'gpt-4o', 'api_key_variable_name': 'openai_api_key'},
    'nvidia_llama': {'class': ChatNVIDIA, 'model_name': 'meta/llama3-8b-instruct', 'api_key_variable_name': 'nvidia_api_key'},
    'claude': {'class': ChatAnthropic, 'model_name': 'claude-3.5-sonnet', 'api_key_variable_name': 'anthropic_api_key'},
}