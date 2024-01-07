from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .core.database import create_db_and_tables
import os
from .api import user, room, game, character, message

# read OPENAI_API_KEY from .env file
from dotenv import load_dotenv

load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

app = FastAPI()
app.mount('/static', StaticFiles(directory=Path('src/www/static')), name='static')


@app.router.on_startup.append
async def on_startup():
    create_db_and_tables()
    


@app.get('/')
async def home(request: Request):
    return Response(content=open('src/www/templates/index.html', 'r').read(), media_type='text/html')


app.include_router(user.router, prefix='', tags=['user'])
app.include_router(room.router, prefix='', tags=['room'])
app.include_router(game.router, prefix='', tags=['game'])
app.include_router(character.router, prefix='', tags=['character'])
app.include_router(message.router, prefix='', tags=['message'])


@app.get('/dashboard')
async def dashboard(request: Request) -> Response:
    return Response(content=open('src/www/templates/dashboard.html', 'r').read(), media_type='text/html')


@app.get('/story')
async def story(request: Request):
    return Response(content=open('src/www/templates/story.html', 'r').read(), media_type='text/html')


# TODO: figure out how this works in fastapi
"""
@socketio.on('join_game')
def handle_join_game(data):
    room_id = data.get('room_id')
    username = session.get('username')
    
    if room_id not in game_rooms:
        return {'error': 'Room does not exist'}
    
    game_rooms[room_id]['players'].append(username)
    socketio.emit('player_joined', {'username': username}, room=room_id)
"""
