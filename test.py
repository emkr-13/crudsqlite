from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Define Pydantic model for request and response
class ProgressOnlineNews(BaseModel):
    name: str
    progress_time: str

# SQLite connection initialization
def get_db():
    db_connection = sqlite3.connect('online_news.db')
    try:
        yield db_connection
    finally:
        db_connection.close()

# Create progress_online_news table if not exists
def create_table():
    with sqlite3.connect('online_news.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_online_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                progress_time TEXT
            )
        ''')
        connection.commit()

# Create progress_online_news table on startup
create_table()

# CRUD operations

# Create progress
@app.post("/progress/", response_model=ProgressOnlineNews)
async def create_progress(progress: ProgressOnlineNews, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO progress_online_news (name, progress_time) VALUES (?, ?)",
        (progress.name, progress.progress_time)
    )
    db.commit()
    return progress

# Read progress
@app.get("/progress/{progress_id}", response_model=ProgressOnlineNews)
async def read_progress(progress_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT pg.name, pg.progress_time FROM progress_online_news  pg WHERE id = ?", (progress_id,))
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Progress not found")
    return {
        "name": result[1],
        "progress_time": result[2],
    }
    

# Update progress
@app.put("/progress/{progress_id}", response_model=ProgressOnlineNews)
async def update_progress(progress_id: int, progress: ProgressOnlineNews, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE progress_online_news SET name = ?, progress_time = ? WHERE id = ?",
        (progress.name, progress.progress_time, progress_id)
    )
    db.commit()
    return progress

# Delete progress
@app.delete("/progress/{progress_id}", response_model=ProgressOnlineNews)
async def delete_progress(progress_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM progress_online_news WHERE id = ?", (progress_id,))
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Progress not found")

    cursor.execute("DELETE FROM progress_online_news WHERE id = ?", (progress_id,))
    db.commit()

    return {
        "name": result[1],
        "progress_time": result[2],
    }
