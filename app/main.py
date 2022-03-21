from fastapi import FastAPI
from .routers import prof, subj

app = FastAPI()


app.include_router(prof.router)
app.include_router(subj.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
