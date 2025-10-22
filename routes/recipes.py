from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Recipe
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from auth import verify_api_key

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RecipeItem(BaseModel):
    name: str
    qty: float
    unit: str

class RecipeCreate(BaseModel):
    name: str
    items: List[RecipeItem]
    instructions: Optional[str] = ""

class RecipeResponse(BaseModel):
    id: int
    name: str
    items: List[RecipeItem]
    instructions: str
    
    class Config:
        from_attributes = True

@router.get("/recipes", response_model=List[RecipeResponse])
async def get_recipes(
    skip: int = Query(0, ge=0, description="Number of recipes to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of recipes to return"),
    db: Session = Depends(get_db)
):
    """Get all recipes with pagination"""
    recipes = db.query(Recipe).offset(skip).limit(limit).all()
    result = []
    for recipe in recipes:
        items_data = json.loads(recipe.items) if recipe.items else []
        result.append({
            "id": recipe.id,
            "name": recipe.name,
            "items": items_data,
            "instructions": recipe.instructions or ""
        })
    return result

@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get a specific recipe"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    items_data = json.loads(recipe.items) if recipe.items else []
    return {
        "id": recipe.id,
        "name": recipe.name,
        "items": items_data,
        "instructions": recipe.instructions or ""
    }

@router.post("/recipes", response_model=RecipeResponse)
async def create_recipe(
    recipe: RecipeCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new recipe"""
    # Check if recipe name already exists
    existing_recipe = db.query(Recipe).filter(Recipe.name == recipe.name).first()
    if existing_recipe:
        raise HTTPException(status_code=400, detail="Recipe with this name already exists")
    
    items_json = json.dumps([item.dict() for item in recipe.items])
    db_recipe = Recipe(
        name=recipe.name,
        items=items_json,
        instructions=recipe.instructions
    )
    
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    # Return consistent structure
    return {
        "id": db_recipe.id,
        "name": db_recipe.name,
        "items": [item.dict() for item in recipe.items],
        "instructions": db_recipe.instructions or ""
    }

@router.put("/recipes/{recipe_id}")
async def update_recipe(
    recipe_id: int, 
    recipe: RecipeCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update a recipe"""
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db_recipe.name = recipe.name
    db_recipe.items = json.dumps([item.dict() for item in recipe.items])
    db_recipe.instructions = recipe.instructions
    
    db.commit()
    db.refresh(db_recipe)
    
    # Return consistent structure
    return {
        "id": db_recipe.id,
        "name": db_recipe.name,
        "items": [item.dict() for item in recipe.items],
        "instructions": db_recipe.instructions or ""
    }

@router.delete("/recipes/{recipe_id}")
async def delete_recipe(
    recipe_id: int, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a recipe"""
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(db_recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}