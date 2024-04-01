import logging
import os
from dotenv import load_dotenv
from ..core.storage import get_secret
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
AZURE_KEYVAULT_URL = 'https://hearthandkin.vault.azure.net/'
AZURE_BLOB_URL = 'https://hearthandkin.blob.core.windows.net/'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or get_secret('OPENAI-API-KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY') or get_secret('ELEVENLABS-API-KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID') or get_secret('ELEVENLABS-VOICE-ID')
assert OPENAI_API_KEY is not None, 'Add OPENAI_API_KEY to .env file or add secret to Azure Key Vault'
assert ELEVENLABS_API_KEY is not None, 'Add ELEVENLABS_API_KEY to .env file or add secret to Azure Key Vault'
assert ELEVENLABS_VOICE_ID is not None, 'Add ELEVENLABS_VOICE_ID to .env file or add secret to Azure Key Vault'
set_api_key(ELEVENLABS_API_KEY)
