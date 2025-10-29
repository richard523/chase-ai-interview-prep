import { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8001/api';

function App() {
  const [todos, setTodos] = useState([]);
  const [notes, setNotes] = useState({});
  const [newTodo, setNewTodo] = useState({ title: '', description: '' });
  const [newNote, setNewNote] = useState('');
  const [selectedTodo, setSelectedTodo] = useState(null);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch todos
  const fetchTodos = async () => {
    setLoading(true);
    setError(null);
    try {
      const filterParam = filter === 'all' ? '' : `?completed=${filter === 'completed'}`;
      const res = await fetch(`${API_URL}/todos${filterParam}`);
      if (!res.ok) throw new Error('Failed to fetch todos');
      const data = await res.json();
      setTodos(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch notes for a todo
  const fetchNotes = async (todoId) => {
    try {
      const res = await fetch(`${API_URL}/todos/${todoId}/notes`);
      if (!res.ok) throw new Error('Failed to fetch notes');
      const data = await res.json();
      setNotes(prev => ({ ...prev, [todoId]: data }));
    } catch (err) {
      setError(err.message);
    }
  };

  // Create todo
  const createTodo = async (e) => {
    e.preventDefault();
    if (!newTodo.title.trim()) return;
    
    try {
      const res = await fetch(`${API_URL}/todos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTodo)
      });
      if (!res.ok) throw new Error('Failed to create todo');
      
      setNewTodo({ title: '', description: '' });
      fetchTodos();
    } catch (err) {
      setError(err.message);
    }
  };

  // Toggle todo completion
  const toggleTodo = async (id, completed) => {
    try {
      const res = await fetch(`${API_URL}/todos/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !completed })
      });
      if (!res.ok) throw new Error('Failed to update todo');
      fetchTodos();
    } catch (err) {
      setError(err.message);
    }
  };

  // Delete todo
  const deleteTodo = async (id) => {
    if (!confirm('Delete this todo and all its notes?')) return;
    
    try {
      const res = await fetch(`${API_URL}/todos/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete todo');
      
      setTodos(todos.filter(t => t.id !== id));
      if (selectedTodo === id) setSelectedTodo(null);
    } catch (err) {
      setError(err.message);
    }
  };

  // Create note
  const createNote = async (todoId) => {
    if (!newNote.trim()) return;
    
    try {
      const res = await fetch(`${API_URL}/todos/${todoId}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newNote })
      });
      if (!res.ok) throw new Error('Failed to create note');
      
      setNewNote('');
      fetchNotes(todoId);
    } catch (err) {
      setError(err.message);
    }
  };

  // Delete note
  const deleteNote = async (todoId, noteId) => {
    try {
      const res = await fetch(`${API_URL}/todos/${todoId}/notes/${noteId}`, {
        method: 'DELETE'
      });
      if (!res.ok) throw new Error('Failed to delete note');
      fetchNotes(todoId);
    } catch (err) {
      setError(err.message);
    }
  };

  // Select todo and load notes
  const selectTodo = (todoId) => {
    setSelectedTodo(todoId);
    if (!notes[todoId]) {
      fetchNotes(todoId);
    }
  };

  useEffect(() => {
    fetchTodos();
  }, [filter]);

  const stats = {
    total: todos.length,
    completed: todos.filter(t => t.completed).length,
    pending: todos.filter(t => !t.completed).length
  };

  return (
    <div className="app">
      <header className="header">
        <h1>📝 Todo App with Notes</h1>
        <div className="stats">
          <span>Total: {stats.total}</span>
          <span>Completed: {stats.completed}</span>
          <span>Pending: {stats.pending}</span>
        </div>
      </header>

      {error && (
        <div className="error">
          ❌ {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="container">
        {/* Left Panel - Todos */}
        <div className="todos-panel">
          <form onSubmit={createTodo} className="todo-form">
            <input
              type="text"
              placeholder="Todo title..."
              value={newTodo.title}
              onChange={e => setNewTodo({ ...newTodo, title: e.target.value })}
              className="input"
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={newTodo.description}
              onChange={e => setNewTodo({ ...newTodo, description: e.target.value })}
              className="input"
            />
            <button type="submit" className="btn btn-primary">
              Add Todo
            </button>
          </form>

          <div className="filter-tabs">
            <button
              className={filter === 'all' ? 'active' : ''}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button
              className={filter === 'active' ? 'active' : ''}
              onClick={() => setFilter('active')}
            >
              Active
            </button>
            <button
              className={filter === 'completed' ? 'active' : ''}
              onClick={() => setFilter('completed')}
            >
              Completed
            </button>
          </div>

          <div className="todos-list">
            {loading ? (
              <div className="loading">Loading...</div>
            ) : todos.length === 0 ? (
              <div className="empty">No todos found. Create one above!</div>
            ) : (
              todos.map(todo => (
                <div
                  key={todo.id}
                  className={`todo-item ${todo.completed ? 'completed' : ''} ${
                    selectedTodo === todo.id ? 'selected' : ''
                  }`}
                  onClick={() => selectTodo(todo.id)}
                >
                  <div className="todo-content">
                    <input
                      type="checkbox"
                      checked={todo.completed}
                      onChange={(e) => {
                        e.stopPropagation();
                        toggleTodo(todo.id, todo.completed);
                      }}
                      className="checkbox"
                    />
                    <div className="todo-text">
                      <h3>{todo.title}</h3>
                      {todo.description && <p>{todo.description}</p>}
                      <small>
                        {new Date(todo.created_at).toLocaleDateString()}
                      </small>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteTodo(todo.id);
                    }}
                    className="btn-delete"
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Panel - Notes */}
        <div className="notes-panel">
          {selectedTodo ? (
            <>
              <h2>Notes</h2>
              <div className="note-form">
                <textarea
                  placeholder="Add a note..."
                  value={newNote}
                  onChange={e => setNewNote(e.target.value)}
                  className="textarea"
                  rows="3"
                />
                <button
                  onClick={() => createNote(selectedTodo)}
                  className="btn btn-primary"
                >
                  Add Note
                </button>
              </div>

              <div className="notes-list">
                {notes[selectedTodo]?.length === 0 ? (
                  <div className="empty">No notes yet. Add one above!</div>
                ) : (
                  notes[selectedTodo]?.map(note => (
                    <div key={note.id} className="note-item">
                      <p>{note.content}</p>
                      <div className="note-footer">
                        <small>
                          {new Date(note.created_at).toLocaleString()}
                        </small>
                        <button
                          onClick={() => deleteNote(selectedTodo, note.id)}
                          className="btn-delete-small"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h2>👈 Select a todo</h2>
              <p>Click on a todo to view and add notes</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
