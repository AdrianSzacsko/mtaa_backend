import socketio as socketio
from fastapi import FastAPI
from .routers import prof, subj, login, register, search, profile
from fastapi.middleware.cors import CORSMiddleware

# SOURCE: https://fastapi.tiangolo.com/tutorial/metadata/
from app.metadata import *


app = FastAPI(openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)

app.include_router(prof.router)
app.include_router(subj.router)
app.include_router(login.router)
app.include_router(register.router)
app.include_router(search.router)
app.include_router(profile.router)


@app.get("/")
async def root():
    return {"message": "MTAA Project by Adrian Szacsko and Marko Stahovec"}

