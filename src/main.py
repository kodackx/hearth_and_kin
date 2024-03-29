import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .api import character, message, story, user, newcharacter
from .core.database import create_db_and_tables, get_session

load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
AZURE_CDN_URL = os.getenv('AZURE_CDN_URL')
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

app = FastAPI()
app.mount('/js', StaticFiles(directory=Path('src/www/static/js')), name='js')

@app.router.on_startup.append
async def on_startup():
    create_db_and_tables()

@app.get("/azure/{file_path:path}")
async def get_azure_file(file_path: str):
    return RedirectResponse(url=f"{AZURE_CDN_URL}/{file_path}")

@app.get('/')
async def home(request: Request):
    return Response(content=open('src/www/templates/index.html', 'r').read(), media_type='text/html')


app.include_router(user.router, prefix='', tags=['user'], dependencies=[Depends(get_session)])
app.include_router(story.router, prefix='', tags=['story'], dependencies=[Depends(get_session)])
app.include_router(character.router, prefix='', tags=['character'], dependencies=[Depends(get_session)])
app.include_router(message.router, prefix='', tags=['message'], dependencies=[Depends(get_session)])
app.include_router(newcharacter.router, prefix='', tags=['message'])


@app.get('/dashboard')
async def dashboard_page(request: Request) -> Response:
    return Response(content=open('src/www/templates/dashboard.html', 'r').read(), media_type='text/html')


@app.get('/story')
async def story_page(request: Request):
    return Response(content=open('src/www/templates/story.html', 'r').read(), media_type='text/html')

@app.get('/newcharacter')
async def characterflow(request: Request):
    return Response(content=open('src/www/templates/newcharacter.html', 'r').read(), media_type='text/html')

if __name__ == '__main__':
    pass
