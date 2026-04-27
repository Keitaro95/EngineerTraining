# 2つのrouterを統制する

from fastapi import FastAPI

from backend.routers import task, done

app = FastAPI()
app.include_router(task.router)
app.include_router(done.router)