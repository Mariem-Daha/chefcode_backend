from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import InventoryItem, Recipe, Task
import json
from typing import Dict, Any

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/data")
async def get_all_data(db: Session = Depends(get_db)):
    """Get all data for frontend synchronization - matches original backend format"""
    
    # Get inventory
    inventory_items = db.query(InventoryItem).all()
    inventory = [
        {
            "id": item.id,
            "name": item.name,
            "unit": item.unit,
            "quantity": item.quantity,
            "category": item.category,
            "price": item.price,
            "lot_number": item.lot_number,
            "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None
        }
        for item in inventory_items
    ]
    
    # Get recipes
    recipe_items = db.query(Recipe).all()
    recipes = {}
    for recipe in recipe_items:
        items_data = json.loads(recipe.items) if recipe.items else []
        yield_data = json.loads(recipe.yield_data) if recipe.yield_data else None
        recipes[recipe.name] = {
            "items": items_data,
            "yield": yield_data
        }
    
    # Get tasks
    task_items = db.query(Task).all()
    tasks = [
        {
            "id": task.id,
            "recipe": task.recipe,
            "quantity": task.quantity,
            "assignedTo": task.assigned_to,
            "status": task.status
        }
        for task in task_items
    ]
    
    return {
        "inventory": inventory,
        "recipes": recipes,
        "tasks": tasks
    }