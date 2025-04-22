# main.py
from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Optional

from db import database
from models import tasks

app = FastAPI()

class TaskIn(BaseModel):
    title: str
    description: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None

class Task(BaseModel):
    id: UUID
    title: str
    description: str
    position: float = Field(..., example=100.000000123)
    done: bool

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: UUID):
    task = await database.fetch_one(tasks.select().where(tasks.c.id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks", response_model=List[Task])
async def get_tasks(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    query = tasks.select().order_by(tasks.c.position).limit(limit).offset(offset)
    return await database.fetch_all(query)

@app.post("/tasks", response_model=Task)
async def create_task(task: TaskIn):
    new_id = uuid4()
    last_position = await database.fetch_val("SELECT COALESCE(MAX(position), 0) FROM tasks")
    position = (last_position or 0.0) + 100.0  # Safe spacing
    query = tasks.insert().values(
        id=new_id,
        title=task.title,
        description=task.description,
        done=False,
        position=position
    )
    await database.execute(query)
    return {**task.model_dump(), "id": new_id, "done": False, "position": position}

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: UUID, payload: TaskUpdate):
    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update.")

    query = tasks.update().where(tasks.c.id == task_id).values(**update_data)
    await database.execute(query)

    task = await database.fetch_one(tasks.select().where(tasks.c.id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: UUID):
    query = tasks.delete().where(tasks.c.id == task_id)
    result = await database.execute(query)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

@app.post("/tasks/reorder")
async def reorder_task(task_id: UUID = Body(...), before_id: UUID = Body(None), after_id: UUID = Body(None)):

    task = await database.fetch_one(tasks.select().where(tasks.c.id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    before_task = await database.fetch_one(tasks.select().where(tasks.c.id == before_id)) if before_id else None
    after_task = await database.fetch_one(tasks.select().where(tasks.c.id == after_id)) if after_id else None

    if before_task and after_task:
        new_position = (before_task["position"] + after_task["position"]) / 2.0
    elif before_task:
        new_position = before_task["position"] + 1.0
    elif after_task:
        new_position = after_task["position"] - 1.0
    else:
        new_position = 0.0

    await database.execute(
        tasks.update().where(tasks.c.id == task_id).values(position=new_position)
    )

    if before_task and after_task:
        gap = abs(before_task["position"] - after_task["position"])
        if gap < 1e-6:
            await rebalance_positions()

    return {"message": f"Task reordered to position {new_position}"}

async def rebalance_positions():
    all_tasks = await database.fetch_all(tasks.select().order_by(tasks.c.position))
    spacing = 100.0

    for index, task in enumerate(all_tasks):
        new_position = (index + 1) * spacing
        await database.execute(
            tasks.update().where(tasks.c.id == task["id"]).values(position=new_position)
        )
