# Full-Stack Todo App with Notes

A production-ready todo application with note-taking capability built with **FastAPI**, **PostgreSQL**, and **React**.

## 🏗️ Architecture

**Backend:**
- FastAPI (Python async framework)
- PostgreSQL (with asyncpg for async database operations)
- RESTful API design
- Connection pooling for performance
- CORS middleware for frontend integration

**Frontend:**
- React 18 with Hooks
- Vite (modern build tool)
- Vanilla CSS (no external UI libraries)
- Responsive design

**Database:**
- PostgreSQL 15
- Two tables: `todos` and `notes` (with foreign key relationship)
- Indexes for performance

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)
- PostgreSQL 15 (if not using Docker)

### Option 1: Docker (Recommended)

```bash
# Backend
cd backend
docker-compose up -d

# The API will be available at http://localhost:8000
# View API docs at http://localhost:8000/docs
```

```bash
# Frontend (in a new terminal)
cd frontend
npm install
npm run dev

# The app will be available at http://localhost:5173
```

### Option 2: Local Setup

**Backend:**

```bash
# 1. Start PostgreSQL (ensure it's running on port 5432)
# Default credentials: postgres/postgres

# 2. Create database
psql -U postgres -c "CREATE DATABASE todoapp;"

# 3. Install Python dependencies
cd backend
pip install -r requirements.txt

# 4. Run the API
uvicorn main:app --reload

# API available at http://localhost:8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev

# App available at http://localhost:5173
```

---

## 📁 Project Structure

```
project/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Docker configuration
│   └── docker-compose.yml  # Docker Compose setup
│
└── frontend/
    ├── src/
    │   ├── App.jsx         # Main React component
    │   └── App.css         # Styles
    ├── package.json        # Node dependencies
    ├── vite.config.js      # Vite configuration
    └── index.html          # HTML entry point
```

---

## 🔌 API Endpoints

### Todos

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos` | Get all todos (optional `?completed=true/false` filter) |
| GET | `/api/todos/{id}` | Get specific todo |
| POST | `/api/todos` | Create new todo |
| PATCH | `/api/todos/{id}` | Update todo (partial) |
| DELETE | `/api/todos/{id}` | Delete todo |

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos/{todo_id}/notes` | Get all notes for a todo |
| POST | `/api/todos/{todo_id}/notes` | Create new note |
| PATCH | `/api/todos/{todo_id}/notes/{note_id}` | Update note |
| DELETE | `/api/todos/{todo_id}/notes/{note_id}` | Delete note |

### Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Get statistics |
| GET | `/health` | Health check |

---

## 💡 Key Features for Interview Discussion

### Backend Features:
1. **Async/Await Pattern**: Uses `asyncpg` for non-blocking database operations
2. **Connection Pooling**: Efficient database connection management
3. **Dependency Injection**: FastAPI's `Depends()` for clean code
4. **Pydantic Models**: Type validation and serialization
5. **RESTful Design**: Proper HTTP methods and status codes
6. **Error Handling**: Appropriate HTTP exceptions
7. **Database Indexing**: Optimized queries with indexes
8. **Cascade Deletes**: Foreign key constraints maintain data integrity

### Frontend Features:
1. **React Hooks**: `useState`, `useEffect` for state management
2. **Component Design**: Single component with clear responsibilities
3. **API Integration**: Fetch API with error handling
4. **Loading States**: User feedback during async operations
5. **Filtering**: Client-side and server-side filtering
6. **Responsive Design**: Mobile-friendly layout
7. **UX Patterns**: Confirmation dialogs, empty states

### Database Schema:

```sql
-- Todos table
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes table
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    todo_id INTEGER REFERENCES todos(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX idx_notes_todo_id ON notes(todo_id);
```

---

## 🎯 Interview Discussion Points

### System Design:
- **Scalability**: Connection pooling, async operations, database indexes
- **Performance**: Efficient queries, pagination could be added
- **Security**: Input validation via Pydantic, SQL injection prevention via parameterized queries
- **Error Handling**: Graceful degradation, user-friendly error messages

### Potential Improvements:
1. **Authentication**: Add JWT tokens for user sessions
2. **Pagination**: Implement offset/limit for large datasets
3. **Search**: Full-text search on todos and notes
4. **Real-time**: WebSockets for live updates
5. **Caching**: Redis for frequently accessed data
6. **Testing**: Unit tests (pytest), integration tests
7. **CI/CD**: GitHub Actions pipeline
8. **Monitoring**: Application logs, metrics, health checks
9. **Rate Limiting**: Prevent API abuse
10. **Optimistic Updates**: Update UI before server confirmation

### Code Quality:
- Type hints in Python
- Proper error boundaries in React
- Consistent naming conventions
- Comments for complex logic
- Environment variable configuration

---

## 🧪 Testing the Application

### Manual Testing:

```bash
# Health check
curl http://localhost:8000/health

# Create a todo
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI","description":"Build awesome APIs"}'

# Get all todos
curl http://localhost:8000/api/todos

# Create a note
curl -X POST http://localhost:8000/api/todos/1/notes \
  -H "Content-Type: application/json" \
  -d '{"content":"This is my first note"}'

# Get statistics
curl http://localhost:8000/api/stats
```

### API Documentation:
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

---

## 🎨 UI Features

- **Filter tabs**: All, Active, Completed todos
- **Statistics**: Real-time counts in header
- **Checkbox toggle**: Quick completion status change
- **Selection highlighting**: Visual feedback for selected todo
- **Notes panel**: Context-aware note management
- **Empty states**: Helpful messages when no data
- **Responsive**: Works on desktop and mobile
- **Loading states**: Visual feedback during API calls
- **Error handling**: User-friendly error messages

---

## 🔧 Configuration

**Backend Environment Variables:**

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todoapp
```

**Frontend API URL:**

Update in `App.jsx`:
```javascript
const API_URL = 'http://localhost:8000/api';
```

---

## 📝 Additional Files Needed

### Frontend: `vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
```

### Frontend: `index.html`

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Todo App with Notes</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### Frontend: `src/main.jsx`

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

---

## 🚨 Common Issues

**CORS Error:**
- Ensure backend is running and CORS middleware is configured
- Check frontend is using correct API URL

**Database Connection:**
- Verify PostgreSQL is running
- Check DATABASE_URL is correct
- Ensure database `todoapp` exists

**Port Conflicts:**
- Backend: Change port in `uvicorn main:app --port 8001`
- Frontend: Change port in `vite.config.js`

---

## 📚 Technologies Used

- **FastAPI** - Modern, fast Python web framework
- **asyncpg** - Fast PostgreSQL client for Python
- **PostgreSQL** - Reliable relational database
- **React** - Popular JavaScript UI library
- **Vite** - Next-generation frontend tooling
- **Docker** - Containerization platform

---

