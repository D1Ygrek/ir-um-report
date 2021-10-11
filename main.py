from fastapi import FastAPI
from fastapi.param_functions import Depends
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseSettings

from sqlalchemy.ext.asyncio import engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from common.read_db import read_active_sessions
from endpoints.session_report import report_sessions

class Settings(BaseSettings):
    token_key: str
    pg_config: str
    class Config:
        env_file = ".env"


settings = Settings()

engine = engine.create_async_engine(settings.pg_config, echo = True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/active_sessions")
async def active_sessions(session: AsyncSession = Depends(get_session)):
    return await read_active_sessions(session)

@app.get("/session_report")
async def session_report(session: AsyncSession = Depends(get_session)):
    return await report_sessions(session)
