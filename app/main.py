from fastapi import FastAPI
from .routers import prof, subj, login, register, search

app = FastAPI()


app.include_router(prof.router)
app.include_router(subj.router)
app.include_router(login.router)
app.include_router(register.router)
app.include_router(search.router)


@app.get("/")
async def root():
    return {"message": "MTAA Project by Adrian Szacsko and Marko Stahovec"}

