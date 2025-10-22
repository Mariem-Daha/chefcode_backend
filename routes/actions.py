from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import InventoryItem, Recipe, Task, SyncData
from pydantic import BaseModel
from typing import Dict, Any, List
import json
from datetime import datetime, date
from auth import verify_api_key

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_date_string(date_str):
    """Convert date string to date object"""
    if not date_str:
        return None
    if isinstance(date_str, date):
        return date_str
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

class ActionRequest(BaseModel):
    action: str
    data: Dict[Any, Any]

class SyncDataRequest(BaseModel):
    inventory: List[Dict[str, Any]]
    recipes: Dict[str, Dict[str, Any]]
    tasks: List[Dict[str, Any]]

@router.post("/action")
async def handle_action(
    request: ActionRequest, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Handle various actions from frontend - matches original backend format"""
    
    action = request.action
    data = request.data
    
    if action == "add-inventory":
        # Add inventory item - validate required fields
        item_data = data
        
        if "name" not in item_data:
            raise HTTPException(status_code=400, detail="Missing required field: name")
        
        # Check if item exists and merge if same price
        existing_item = db.query(InventoryItem).filter(InventoryItem.name == item_data["name"]).first()
        
        if existing_item and abs(existing_item.price - item_data.get("price", 0)) < 0.01:
            # Merge quantities for same item at same price (only if HACCP fields match)
            existing_lot = existing_item.lot_number or ""
            existing_expiry = existing_item.expiry_date
            new_lot = item_data.get("lot_number") or ""
            new_expiry = parse_date_string(item_data.get("expiry_date"))
            
            if existing_lot == new_lot and existing_expiry == new_expiry:
                existing_item.quantity += item_data.get("quantity", 0)
                db.commit()
                return {"success": True, "message": "Item quantity updated"}
            else:
                # HACCP fields differ - create separate item for traceability
                new_item = InventoryItem(
                    name=item_data["name"],
                    unit=item_data.get("unit", "pz"),
                    quantity=item_data.get("quantity", 0),
                    category=item_data.get("category", "Other"),
                    price=item_data.get("price", 0),
                    lot_number=item_data.get("lot_number"),
                    expiry_date=parse_date_string(item_data.get("expiry_date"))
                )
                db.add(new_item)
                db.commit()
                return {"success": True, "message": "Item added (separate entry for HACCP traceability)"}
        else:
            # Create new item with HACCP fields
            new_item = InventoryItem(
                name=item_data["name"],
                unit=item_data.get("unit", "pz"),
                quantity=item_data.get("quantity", 0),
                category=item_data.get("category", "Other"),
                price=item_data.get("price", 0),
                lot_number=item_data.get("lot_number"),
                expiry_date=parse_date_string(item_data.get("expiry_date"))
            )
            db.add(new_item)
            db.commit()
            return {"success": True, "message": "Item added successfully"}
    
    elif action == "save-recipe":
        # Save recipe - validate required fields
        recipe_data = data
        
        if "name" not in recipe_data:
            raise HTTPException(status_code=400, detail="Missing required field: name")
        if "recipe" not in recipe_data:
            raise HTTPException(status_code=400, detail="Missing required field: recipe")
        
        name = recipe_data["name"]
        recipe_info = recipe_data["recipe"]
        
        # Check if recipe exists
        existing_recipe = db.query(Recipe).filter(Recipe.name == name).first()
        
        items_json = json.dumps(recipe_info.get("items", []))
        
        if existing_recipe:
            # Update existing recipe
            existing_recipe.items = items_json
            existing_recipe.instructions = recipe_info.get("instructions", "")
            db.commit()
            return {"success": True, "message": "Recipe updated successfully"}
        else:
            # Create new recipe
            new_recipe = Recipe(
                name=name,
                items=items_json,
                instructions=recipe_info.get("instructions", "")
            )
            db.add(new_recipe)
            db.commit()
            return {"success": True, "message": "Recipe saved successfully"}
    
    elif action == "add-task":
        # Add task - validate required fields
        task_data = data
        
        if "recipe" not in task_data:
            raise HTTPException(status_code=400, detail="Missing required field: recipe")
        
        new_task = Task(
            recipe=task_data["recipe"],
            quantity=task_data.get("quantity", 1),
            assigned_to=task_data.get("assignedTo", ""),
            status=task_data.get("status", "todo")
        )
        db.add(new_task)
        db.commit()
        return {"success": True, "message": "Task added successfully"}
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

@router.post("/sync-data")
async def sync_data(
    request: SyncDataRequest, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Sync all data from frontend - matches original backend format"""
    
    try:
        # Store sync data for backup
        sync_record = SyncData(
            data_type="full_sync",
            data_content=json.dumps(request.dict())
        )
        db.add(sync_record)
        
        # Sync inventory - Fix N+1 query problem
        if request.inventory:
            # Fetch all existing items in one query
            inventory_names = [item["name"] for item in request.inventory if "name" in item]
            existing_items = db.query(InventoryItem).filter(InventoryItem.name.in_(inventory_names)).all()
            existing_items_dict = {item.name: item for item in existing_items}
            
            for item_data in request.inventory:
                if "name" not in item_data:
                    continue
                    
                existing_item = existing_items_dict.get(item_data["name"])
                if existing_item:
                    # Update existing
                    existing_item.unit = item_data.get("unit", "pz")
                    existing_item.quantity = item_data.get("quantity", 0)
                    existing_item.category = item_data.get("category", "Other")
                    existing_item.price = item_data.get("price", 0)
                    existing_item.lot_number = item_data.get("lot_number")
                    existing_item.expiry_date = parse_date_string(item_data.get("expiry_date"))
                else:
                    # Create new - convert date string to date object
                    item_data_copy = item_data.copy()
                    item_data_copy['expiry_date'] = parse_date_string(item_data.get("expiry_date"))
                    new_item = InventoryItem(**item_data_copy)
                    db.add(new_item)
        
        # Sync recipes - Fix N+1 query problem and handle deletions
        # Get all existing recipes from database
        all_existing_recipes = db.query(Recipe).all()
        existing_recipes_dict = {recipe.name: recipe for recipe in all_existing_recipes}
        
        # Get recipe names from frontend
        frontend_recipe_names = set(request.recipes.keys()) if request.recipes else set()
        
        # Delete recipes that exist in DB but not in frontend
        for db_recipe in all_existing_recipes:
            if db_recipe.name not in frontend_recipe_names:
                db.delete(db_recipe)
        
        # Add or update recipes from frontend
        if request.recipes:
            for recipe_name, recipe_data in request.recipes.items():
                existing_recipe = existing_recipes_dict.get(recipe_name)
                items_json = json.dumps(recipe_data.get("items", []))
                yield_json = json.dumps(recipe_data.get("yield")) if recipe_data.get("yield") else None
                
                if existing_recipe:
                    existing_recipe.items = items_json
                    existing_recipe.yield_data = yield_json
                else:
                    new_recipe = Recipe(
                        name=recipe_name,
                        items=items_json,
                        yield_data=yield_json
                    )
                    db.add(new_recipe)
        
        # Sync tasks - Fix N+1 query problem
        if request.tasks:
            task_ids = [task_data["id"] for task_data in request.tasks if "id" in task_data]
            existing_tasks = db.query(Task).filter(Task.id.in_(task_ids)).all() if task_ids else []
            existing_tasks_dict = {task.id: task for task in existing_tasks}
            
            for task_data in request.tasks:
                if "recipe" not in task_data:
                    continue
                    
                if "id" in task_data:
                    existing_task = existing_tasks_dict.get(task_data["id"])
                    if existing_task:
                        existing_task.recipe = task_data["recipe"]
                        existing_task.quantity = task_data.get("quantity", 1)
                        existing_task.assigned_to = task_data.get("assignedTo", "")
                        existing_task.status = task_data.get("status", "todo")
                        continue
                
                # Create new task
                new_task = Task(
                    recipe=task_data["recipe"],
                    quantity=task_data.get("quantity", 1),
                    assigned_to=task_data.get("assignedTo", ""),
                    status=task_data.get("status", "todo")
                )
                db.add(new_task)
        
        db.commit()
        return {"success": True, "message": "Data synchronized successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Sync failed. Please try again.")
