from contextlib import asynccontextmanager

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import init_db
import requests as rq

class AddTask(BaseModel):
    tg_id: int 
    title: str

class CompleteTask(BaseModel):
    task_id: int

@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Bot is ready')
    yield

app = FastAPI(title='To Do App', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/tasks/{tg_id}")
async def tasks(tg_id: int):
    user = await rq.add_user(tg_id)
    return await rq.get_tasks(user.id)
    
@app.get("/api/main/{tg_id}")
async def profile(tg_id: int):
    user = await rq.add_user(tg_id)
    completed_tasks_count = await rq.get_completed_tasks_count(user.id)
    return {'completedTasks': completed_tasks_count}

@app.post("/api/add")
async def add_task(data: AddTask):
    user = await rq.add_user(data.tg_id)
    await rq.add_task(user_id=user.id, title=data.title)
    return {"status": 200}

@app.patch("/api/completed")
async def complete_task(data: CompleteTask):
    await rq.complete_task(data.task_id)
    return {"status": 200}