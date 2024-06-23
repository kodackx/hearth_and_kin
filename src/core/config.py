import logging
from dotenv import load_dotenv
DEBUG = True
GENERATE_IMAGE = True
GENERATE_AUDIO = True
GENERATE_REPLY = True
DEFAULT_TEXT_NARRATOR_MODEL = 'nvidia'
DEFAULT_AUDIO_NARRATOR_MODEL = 'elevenlabs'
DEFAULT_IMAGE_MODEL = 'dalle3'
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
