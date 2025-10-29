from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import asyncpg
import os

app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
db_pool = None

# Pydantic models
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class NoteCreate(BaseModel):
    content: str

class NoteUpdate(BaseModel):
    content: str

class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

class Note(BaseModel):
    id: int
    todo_id: int
    content: str
    created_at: datetime

# Database dependency
async def get_db():
    return db_pool

# Startup/Shutdown events
@app.on_event("startup")
async def startup():
    global db_pool
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/todoapp"
    )
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    
    # Create tables if they don't exist
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                todo_id INTEGER REFERENCES todos(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notes_todo_id ON notes(todo_id)
        """)

@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Todo endpoints
@app.get("/api/todos", response_model=List[Todo])
async def get_todos(
    completed: Optional[bool] = None,
    db=Depends(get_db)
):
    """Get all todos, optionally filtered by completion status"""
    query = "SELECT * FROM todos"
    params = []
    
    if completed is not None:
        query += " WHERE completed = $1"
        params.append(completed)
    
    query += " ORDER BY created_at DESC"
    
    async with db.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

@app.get("/api/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int, db=Depends(get_db)):
    """Get a specific todo by ID"""
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM todos WHERE id = $1", todo_id)
        if not row:
            raise HTTPException(status_code=404, detail="Todo not found")
        return dict(row)

@app.post("/api/todos", response_model=Todo, status_code=201)
async def create_todo(todo: TodoCreate, db=Depends(get_db)):
    """Create a new todo"""
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO todos (title, description)
            VALUES ($1, $2)
            RETURNING *
            """,
            todo.title,
            todo.description
        )
        return dict(row)

@app.patch("/api/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: TodoUpdate, db=Depends(get_db)):
    """Update a todo (partial update)"""
    async with db.acquire() as conn:
        # Check if todo exists
        existing = await conn.fetchrow("SELECT * FROM todos WHERE id = $1", todo_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        # Build dynamic update query
        updates = []
        params = []
        param_count = 1
        
        if todo.title is not None:
            updates.append(f"title = ${param_count}")
            params.append(todo.title)
            param_count += 1
        
        if todo.description is not None:
            updates.append(f"description = ${param_count}")
            params.append(todo.description)
            param_count += 1
        
        if todo.completed is not None:
            updates.append(f"completed = ${param_count}")
            params.append(todo.completed)
            param_count += 1
        
        if not updates:
            return dict(existing)
        
        updates.append(f"updated_at = CURRENT_TIMESTAMP")
        params.append(todo_id)
        
        query = f"""
            UPDATE todos
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING *
        """
        
        row = await conn.fetchrow(query, *params)
        return dict(row)

@app.delete("/api/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: int, db=Depends(get_db)):
    """Delete a todo and all its notes"""
    async with db.acquire() as conn:
        result = await conn.execute("DELETE FROM todos WHERE id = $1", todo_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Todo not found")
        return None

# Note endpoints
@app.get("/api/todos/{todo_id}/notes", response_model=List[Note])
async def get_notes(todo_id: int, db=Depends(get_db)):
    """Get all notes for a specific todo"""
    async with db.acquire() as conn:
        # Verify todo exists
        todo = await conn.fetchrow("SELECT id FROM todos WHERE id = $1", todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        rows = await conn.fetch(
            "SELECT * FROM notes WHERE todo_id = $1 ORDER BY created_at DESC",
            todo_id
        )
        return [dict(row) for row in rows]

@app.post("/api/todos/{todo_id}/notes", response_model=Note, status_code=201)
async def create_note(todo_id: int, note: NoteCreate, db=Depends(get_db)):
    """Create a new note for a todo"""
    async with db.acquire() as conn:
        # Verify todo exists
        todo = await conn.fetchrow("SELECT id FROM todos WHERE id = $1", todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        row = await conn.fetchrow(
            """
            INSERT INTO notes (todo_id, content)
            VALUES ($1, $2)
            RETURNING *
            """,
            todo_id,
            note.content
        )
        return dict(row)

@app.patch("/api/todos/{todo_id}/notes/{note_id}", response_model=Note)
async def update_note(
    todo_id: int,
    note_id: int,
    note: NoteUpdate,
    db=Depends(get_db)
):
    """Update a note"""
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE notes
            SET content = $1
            WHERE id = $2 AND todo_id = $3
            RETURNING *
            """,
            note.content,
            note_id,
            todo_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Note not found")
        return dict(row)

@app.delete("/api/todos/{todo_id}/notes/{note_id}", status_code=204)
async def delete_note(todo_id: int, note_id: int, db=Depends(get_db)):
    """Delete a note"""
    async with db.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM notes WHERE id = $1 AND todo_id = $2",
            note_id,
            todo_id
        )
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Note not found")
        return None

# Statistics endpoint (bonus for interview discussion)
@app.get("/api/stats")
async def get_stats(db=Depends(get_db)):
    """Get todo statistics"""
    async with db.acquire() as conn:
        stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_todos,
                SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_todos,
                SUM(CASE WHEN NOT completed THEN 1 ELSE 0 END) as pending_todos,
                (SELECT COUNT(*) FROM notes) as total_notes
            FROM todos
        """)
        return dict(stats)
