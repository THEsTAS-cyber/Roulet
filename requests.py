from sqlalchemy import select, update, delete, func
from models import async_session, User, Task, Wallet
from pydantic import BaseModel, ConfigDict
from typing import List

class TaskSchema(BaseModel):
    id: int
    title: str
    completed: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class UserSchema(BaseModel):
    id: int
    tg_id: int
    age: int

    model_config = ConfigDict(from_attributes=True)
    
async def add_user(tg_id: int, serialized=False):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user
        
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        if serialized:
            return UserSchema.model_validate(new_user).model_dump()
        return new_user
    
async def get_tasks(user_id):
    async with async_session() as session:
        tasks = await session.scalars(select(Task).where(Task.user_id == user_id, Task.completed == False))
        
        serialized_tasks = [
            TaskSchema.model_validate(t).model_dump() for t in tasks
        ]
        
        return serialized_tasks
    
async def get_completed_tasks_count(user_id):
    async with async_session() as session:
        return await session.scalar(select(func.count(Task.id)).where(Task.user_id == user_id).where(Task.completed == True))

async def add_task(user_id: int, title: str):
    async with async_session() as session:
        new_task = Task(title=title, user_id=user_id)
        session.add(new_task)
        await session.commit()
        return new_task

async def update_task(task_id: int):
    async with async_session() as session:
        await session.execute(update(Task).where(Task.id == task_id).values(completed=True))
        await session.commit()

async def change_age(user_id: int, newage: int):
    async with async_session() as session:
        await session.execute(update(User).where(User.id == user_id).values(age=newage))
        await session.commit()

async def add_wallet(user_id: int, title: str):
    async with async_session() as session:
        new_wallet = Wallet(title=title, user_id=user_id)
        session.add(new_wallet)
        await session.commit()
        return new_wallet