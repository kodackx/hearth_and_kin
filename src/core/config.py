import logging
from dotenv import load_dotenv
from ..models.enums import AudioModel, ImageModel, TextModel
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI

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