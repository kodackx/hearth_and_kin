import os
from pathlib import Path

# read OPENAI_API_KEY from .env file
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from .api import character, message, story, user
from .core.database import create_db_and_tables, get_session
from .core.mongodb import setup_mongodb

load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

app = FastAPI()
app.mount('/static', StaticFiles(directory=Path('src/www/static')), name='static')
mongo_db = setup_mongodb()

@app.router.on_startup.append
async def on_startup():
    create_db_and_tables()
    


@app.get('/')
async def home(request: Request):
    return Response(content=open('src/www/templates/index.html', 'r').read(), media_type='text/html')


app.include_router(user.router, prefix='', tags=['user'], dependencies=[Depends(get_session)])
app.include_router(story.router, prefix='', tags=['story'], dependencies=[Depends(get_session)])
app.include_router(character.router, prefix='', tags=['character'], dependencies=[Depends(get_session)])
app.include_router(message.router, prefix='', tags=['message'], dependencies=[Depends(get_session)])


@app.get('/dashboard')
async def dashboard_page(request: Request) -> Response:
    return Response(content=open('src/www/templates/dashboard.html', 'r').read(), media_type='text/html')


@app.get('/story')
async def story_page(request: Request):
    return Response(content=open('src/www/templates/story.html', 'r').read(), media_type='text/html')


# TODO: figure out how this works in fastapi
"""
@socketio.on('join_game')
def handle_join_game(data):
    story_id = data.get('story_id')
    username = session.get('username')
    
    if story_id not in game_storys:
        return {'error': 'Story does not exist'}
    
    game_storys[story_id]['players'].append(username)
    socketio.emit('player_joined', {'username': username}, story=story_id)
"""
if __name__ == '__main__':
    pass
