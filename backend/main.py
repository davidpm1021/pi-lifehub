from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import os
import logging
import logging.handlers
import psutil
import subprocess
from pathlib import Path
from contextlib import asynccontextmanager
import sys

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging with rotation
log_dir = Path("/var/log/pi-life-hub")
try:
    log_dir.mkdir(parents=True, exist_ok=True)
except PermissionError:
    # Fallback to local directory for development
    log_dir = Path("./logs")
    log_dir.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("pi_life_hub")
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    log_dir / "lifehub.log",
    maxBytes=100 * 1024 * 1024,  # 100MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Import Phase 2 modules
try:
    from modules.voice import voice_router, voice_service
    voice_available = True
except ImportError as e:
    logger.warning(f"Voice module not available: {e}")
    voice_available = False

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Pi Life Hub...")
    init_db()
    
    # Initialize modules
    if voice_available:
        logger.info("Voice module available")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pi Life Hub...")
    
    # Cleanup modules
    if voice_available:
        voice_service.cleanup()

app = FastAPI(
    title="Pi Life Hub",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware for local network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your local network
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Mount static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Configuration from environment
DB_PATH = os.getenv("LIFEHUB_DB_PATH", "lifehub.db")
MAX_CPU_TEMP = int(os.getenv("LIFEHUB_MAX_CPU_TEMP", "70"))
MAX_CPU_USAGE = int(os.getenv("LIFEHUB_MAX_CPU_USAGE", "50"))

def init_db():
    """Initialize SQLite database with basic tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        logger.info(f"Initializing database at {DB_PATH}")
        
        # Users table for NFC profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                nfc_tag_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Todo items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                task TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
    
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": app.version,
        "checks": {}
    }
    
    # Check CPU temperature
    try:
        temp_output = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if temp_output.returncode == 0:
            temp_str = temp_output.stdout.strip()
            temp_value = float(temp_str.split('=')[1].split("'")[0])
            health_status["checks"]["cpu_temperature"] = {
                "value": temp_value,
                "status": "ok" if temp_value < MAX_CPU_TEMP else "warning",
                "threshold": MAX_CPU_TEMP
            }
    except Exception as e:
        logger.error(f"Failed to get CPU temperature: {e}")
        health_status["checks"]["cpu_temperature"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check CPU and memory usage
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        health_status["checks"]["cpu_usage"] = {
            "value": cpu_percent,
            "status": "ok" if cpu_percent < MAX_CPU_USAGE else "warning",
            "threshold": MAX_CPU_USAGE
        }
        
        health_status["checks"]["memory"] = {
            "used_mb": memory.used // (1024 * 1024),
            "total_mb": memory.total // (1024 * 1024),
            "percent": memory.percent,
            "status": "ok" if memory.percent < 80 else "warning"
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        health_status["checks"]["system_metrics"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check database connectivity
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        health_status["checks"]["database"] = {
            "status": "ok",
            "user_count": user_count
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Overall status
    if any(check.get("status") == "error" for check in health_status["checks"].values()):
        health_status["status"] = "unhealthy"
    elif any(check.get("status") == "warning" for check in health_status["checks"].values()):
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard"""
    with open(FRONTEND_DIR / "index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/time")
async def get_time():
    """Get current time and date"""
    try:
        now = datetime.now()
        return {
            "time": now.strftime("%H:%M"),
            "date": now.strftime("%A, %B %d, %Y"),
            "timestamp": now.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting time: {e}")
        raise HTTPException(status_code=500, detail="Failed to get time")

@app.get("/api/users")
async def get_users():
    """Get all users"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, nfc_tag_id FROM users")
        users = [{"id": row[0], "name": row[1], "nfc_tag_id": row[2]} for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@app.post("/api/users")
async def create_user(user_data: Dict[str, str]):
    """Create a new user"""
    # Input validation
    if not user_data.get("name"):
        raise HTTPException(status_code=400, detail="Name is required")
    
    if len(user_data["name"]) > 50:
        raise HTTPException(status_code=400, detail="Name too long (max 50 chars)")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, nfc_tag_id) VALUES (?, ?)",
            (user_data["name"], user_data.get("nfc_tag_id"))
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Created user: {user_data['name']} (ID: {user_id})")
        return {"id": user_id, "name": user_data["name"]}
    except sqlite3.IntegrityError as e:
        logger.warning(f"User creation failed - duplicate NFC tag: {e}")
        raise HTTPException(status_code=409, detail="NFC tag already assigned")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/api/todos/{user_id}")
async def get_todos(user_id: int):
    """Get todos for a specific user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, task, completed FROM todos WHERE user_id = ?",
            (user_id,)
        )
        todos = [{"id": row[0], "task": row[1], "completed": bool(row[2])} for row in cursor.fetchall()]
        conn.close()
        return todos
    except Exception as e:
        logger.error(f"Error fetching todos for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch todos")

@app.post("/api/todos/{user_id}")
async def create_todo(user_id: int, todo_data: Dict[str, str]):
    """Create a new todo for a user"""
    # Input validation
    if not todo_data.get("task"):
        raise HTTPException(status_code=400, detail="Task is required")
    
    if len(todo_data["task"]) > 200:
        raise HTTPException(status_code=400, detail="Task too long (max 200 chars)")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        
        cursor.execute(
            "INSERT INTO todos (user_id, task) VALUES (?, ?)",
            (user_id, todo_data["task"])
        )
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Created todo for user {user_id}: {todo_data['task'][:50]}...")
        return {"id": todo_id, "task": todo_data["task"], "completed": False}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating todo: {e}")
        raise HTTPException(status_code=500, detail="Failed to create todo")

@app.put("/api/todos/{todo_id}")
async def update_todo(todo_id: int, todo_data: Dict[str, bool]):
    """Update todo completion status"""
    if "completed" not in todo_data:
        raise HTTPException(status_code=400, detail="Completed status required")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if todo exists
        cursor.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Todo not found")
        
        cursor.execute(
            "UPDATE todos SET completed = ? WHERE id = ?",
            (todo_data["completed"], todo_id)
        )
        conn.commit()
        conn.close()
        logger.info(f"Updated todo {todo_id}: completed={todo_data['completed']}")
        return {"id": todo_id, "completed": todo_data["completed"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo: {e}")
        raise HTTPException(status_code=500, detail="Failed to update todo")

# Include routers from modules
if voice_available:
    app.include_router(voice_router)
    logger.info("Voice API routes added")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)