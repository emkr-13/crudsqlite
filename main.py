from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import databases
import datetime as dt

DATABASE_URL = "sqlite:///./online_news.db"

database = databases.Database(DATABASE_URL)

app = FastAPI()

class ProgressCreate(BaseModel):
    name: str
    progress_time: dt.date

class ProgressUpdate(BaseModel):
    name: str = None
    progress_time: dt.date = None

class ProgressOnlineNews(BaseModel):
    id: int
    name: str
    progress_time: dt.date

# Dependency to get the database connection
async def get_db():
    try:
        yield database
    finally:
        pass  # No need to close the database connection explicitly

# Create progress entry
@app.post("/progress", response_model=ProgressOnlineNews)
async def create_progress(progress: ProgressCreate, db: databases.Database = Depends(get_db)):
    query = "INSERT INTO progress_online_news (name, progress_time) VALUES (:name, :progress_time)"
    values = {"name": progress.name, "progress_time": progress.progress_time}
    result = await db.execute(query=query, values=values)
    return {"id": result, **progress.dict()}

# Read progress by ID
@app.get("/progress/{progress_id}", response_model=ProgressOnlineNews)
async def read_progress(progress_id: int, db: databases.Database = Depends(get_db)):
    query = "SELECT id, name, progress_time FROM progress_online_news WHERE id = :progress_id"
    values = {"progress_id": progress_id}
    result = await db.fetch_one(query=query, values=values)

    if result is None:
        raise HTTPException(status_code=404, detail="Progress not found")

    return {
        "id": result['id'],
        "name": result['name'],
        "progress_time": result['progress_time'],
    }

# Get all progress entries
@app.get("/progress", response_model=list[ProgressOnlineNews])
async def read_all_progress(db: databases.Database = Depends(get_db)):
    query = "SELECT id, name, progress_time FROM progress_online_news"
    results = await db.fetch_all(query)
    return results

# Update progress entry by ID
@app.put("/progress/{progress_id}", response_model=ProgressOnlineNews)
async def update_progress(progress_id: int, progress: ProgressUpdate, db: databases.Database = Depends(get_db)):
    # Fetch existing progress to get current values
    current_progress = await db.fetch_one("SELECT id, name, progress_time FROM progress_online_news WHERE id = :progress_id", {"progress_id": progress_id})

    if current_progress is None:
        raise HTTPException(status_code=404, detail="Progress not found")

    # Update only the provided fields
    updated_fields = {k: v for k, v in progress.dict().items() if v is not None}
    updated_progress = {**current_progress, **updated_fields}

    # Perform the update
    query = "UPDATE progress_online_news SET name = :name, progress_time = :progress_time WHERE id = :progress_id"
    await db.execute(query=query, values=updated_progress)
    
    return updated_progress

# Delete progress entry by ID
@app.delete("/progress/{progress_id}", response_model=dict)
async def delete_progress(progress_id: int, db: databases.Database = Depends(get_db)):
    query = "DELETE FROM progress_online_news WHERE id = :progress_id"
    values = {"progress_id": progress_id}
    await db.execute(query=query, values=values)
    return {"message": "Progress deleted successfully"}
