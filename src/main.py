from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response, Security
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .api import character, message, story, user, newcharacter
from .core.database import create_db_and_tables, get_session

app = FastAPI()
app.mount('/static', StaticFiles(directory=Path('src/www/static')), name='static')
app.mount('/data', StaticFiles(directory=Path('data')), name='data')
app.mount('/js', StaticFiles(directory=Path('src/www/static/js')), name='js')

favicon_path = 'src/www/static/img/favicon.ico'
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(favicon_path)

@app.router.on_startup.append
async def on_startup():
    create_db_and_tables()


app.include_router(user.router, dependencies=[Depends(get_session)])
app.include_router(story.router, dependencies=[Depends(get_session), Security(user.validate_jwt_token)])
app.include_router(story.public_router)
app.include_router(character.router, dependencies=[Depends(get_session)])
app.include_router(message.router, dependencies=[Depends(get_session)])
app.include_router(newcharacter.router)

@app.get('/')
async def home(request: Request):
    return Response(content=open('src/www/templates/index.html', 'r').read(), media_type='text/html')


@app.get('/lobby')
async def lobby_page(request: Request):
    return Response(content=open('src/www/templates/lobby.html', 'r').read(), media_type='text/html')


@app.get('/dashboard')
async def dashboard_page(request: Request) -> Response:
    return Response(content=open('src/www/templates/dashboard.html', 'r').read(), media_type='text/html')


@app.get('/story')
async def story_page(request: Request):
    return Response(content=open('src/www/templates/story.html', 'r').read(), media_type='text/html')


@app.get('/newcharacter')
async def characterflow(request: Request):
    return Response(content=open('src/www/templates/newcharacter.html', 'r').read(), media_type='text/html')


@app.get('/register')
async def register(request: Request):
    return Response(content=open('src/www/templates/register.html', 'r').read(), media_type='text/html')

if __name__ == '__main__':
    pass
