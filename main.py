from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from database import SessionLocal, engine
import models
from routes import inventory, recipes, tasks, chat, data, actions, web_recipes, ai_assistant, ocr_invoice

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ChefCode Backend",
    description="FastAPI backend for ChefCode inventory management system",
    version="1.0.0"
)

# CORS configuration to allow frontend connections
# In production, replace with specific frontend URLs
# Allow all origins for development (includes file:// protocol and localhost)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(inventory.router, prefix="/api", tags=["inventory"])
app.include_router(recipes.router, prefix="/api", tags=["recipes"]) 
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(data.router, prefix="/api", tags=["data"])
app.include_router(actions.router, prefix="/api", tags=["actions"])
app.include_router(web_recipes.router, prefix="/api/web-recipes", tags=["web-recipes"])
app.include_router(ai_assistant.router, prefix="/api/ai-assistant", tags=["ai-assistant"])
app.include_router(ocr_invoice.router, prefix="/api/ocr", tags=["ocr"])

@app.get("/")
async def root():
    return {"message": "ChefCode FastAPI Backend", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ChefCode Backend"}

if __name__ == "__main__":
    # Use reload=True only in development
    # For production, use: uvicorn main:app --host 0.0.0.0 --port $PORT
    is_dev = os.getenv("ENVIRONMENT", "development") == "development"
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=is_dev)