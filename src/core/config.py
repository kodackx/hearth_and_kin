import logging
import os
from dotenv import load_dotenv
from elevenlabs import set_api_key
DEBUG = True
GENERATE_IMAGE = True
GENERATE_AUDIO = True
GENERATE_REPLY = True
logger = logging.getLogger(__name__)

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
assert OPENAI_API_KEY is not None, 'Add OPENAI_API_KEY to .env file'
assert ELEVENLABS_API_KEY is not None, 'Add ELEVENLABS_API_KEY to .env file'
assert ELEVENLABS_VOICE_ID is not None, 'Add ELEVENLABS_VOICE_ID to .env file'
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
os.environ['ELEVENLABS_API_KEY'] = ELEVENLABS_API_KEY
os.environ['ELEVENLABS_VOICE_ID'] = ELEVENLABS_VOICE_ID
set_api_key(ELEVENLABS_API_KEY)
