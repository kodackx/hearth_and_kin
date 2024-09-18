from pathlib import Path
from sqlmodel import Session, select
from fastapi import Depends, FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse
from fastapi import APIRouter
from contextlib import asynccontextmanager
from .api import character, message, story, user, newcharacter
from .core.database import create_db_and_tables, get_session, engine
from .models.story import Counter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    create_db_and_tables()
    # manage the story counter
    with Session(engine) as session:
        counter = session.get(Counter, 1)
        if not counter:
            counter = Counter(next_story_id=1)
            session.add(counter)
            session.commit()
    yield
    # Shutdown event
    # Add any shutdown logic here if needed

app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=Path('src/www/static')), name='static')
app.mount('/data', StaticFiles(directory=Path('data')), name='data')
app.mount('/js', StaticFiles(directory=Path('src/www/static/js')), name='js')

# router = APIRouter(prefix="/favicon.ico")
favicon_path = 'src/www/static/img/favicon.ico'
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(favicon_path)

# this will be taken care of by the lifespan handler
# @app.router.on_startup.append
# async def on_startup():
#     create_db_and_tables()

@app.get('/')
async def home(request: Request):
    return Response(content=open('src/www/templates/index.html', 'r').read(), media_type='text/html')


app.include_router(user.router, prefix='', tags=['user'], dependencies=[Depends(get_session)])
app.include_router(story.router, prefix='', tags=['story'], dependencies=[Depends(get_session)])
app.include_router(character.router, prefix='', tags=['character'], dependencies=[Depends(get_session)])
app.include_router(message.router, prefix='', tags=['message'], dependencies=[Depends(get_session)])
app.include_router(newcharacter.router, prefix='', tags=['message'])

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
async def characterflow(request: Request):
    return Response(content=open('src/www/templates/register.html', 'r').read(), media_type='text/html')

if __name__ == '__main__':
    pass
