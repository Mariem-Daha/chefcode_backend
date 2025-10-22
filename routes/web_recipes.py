"""
Web Recipe Search Routes
Handles recipe search from web sources (TheMealDB) and AI-powered ingredient mapping
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import logging

from database import SessionLocal
from models import Recipe, InventoryItem
from auth import verify_api_key
from services.ai_service import get_ai_service
from services.mealdb_service import get_mealdb_service

router = APIRouter()
logger = logging.getLogger(__name__)


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class InterpretQueryRequest(BaseModel):
    """Request model for query interpretation"""
    query: str = Field(..., description="Natural language recipe search query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Find a quick Italian pasta recipe without cheese"
            }
        }


class InterpretQueryResponse(BaseModel):
    """Response model for interpreted query"""
    keywords: List[str] = Field(default_factory=list)
    cuisine: Optional[str] = None
    restrictions: List[str] = Field(default_factory=list)
    max_time: Optional[int] = None


class SearchRecipesRequest(BaseModel):
    """Request model for recipe search"""
    query: str = Field(..., description="Search query or keywords")
    cuisine: Optional[str] = None
    restrictions: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "pasta",
                "cuisine": "Italian",
                "restrictions": ["no cheese"]
            }
        }


class RecipeIngredient(BaseModel):
    """Recipe ingredient model"""
    name: str
    measure: str


class WebRecipeResponse(BaseModel):
    """Response model for web recipe"""
    id: str
    name: str
    image: Optional[str]
    category: Optional[str]
    area: Optional[str]  # Cuisine
    instructions: str
    ingredients: List[RecipeIngredient]
    source_url: str


class MapIngredientsRequest(BaseModel):
    """Request model for ingredient mapping"""
    recipe_id: str = Field(..., description="TheMealDB recipe ID")
    recipe_ingredients: List[Dict[str, str]] = Field(
        ..., 
        description="List of recipe ingredients with name, quantity, and unit"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipe_id": "52772",
                "recipe_ingredients": [
                    {"name": "Spaghetti", "quantity": "400", "unit": "g"},
                    {"name": "Tomatoes", "quantity": "500", "unit": "g"}
                ]
            }
        }


class IngredientMapping(BaseModel):
    """Single ingredient mapping result"""
    recipe_ingredient: str
    recipe_quantity: str
    recipe_unit: str
    mapped_to: Optional[str]
    match_confidence: float = Field(ge=0.0, le=1.0)
    match_type: str = Field(..., description="exact, substitute, or missing")
    note: str
    
    # Allow numbers to be automatically converted to strings
    @classmethod
    def model_validate(cls, obj):
        if isinstance(obj, dict):
            # Convert recipe_quantity to string if it's a number
            if 'recipe_quantity' in obj and not isinstance(obj['recipe_quantity'], str):
                obj['recipe_quantity'] = str(obj['recipe_quantity'])
        return super().model_validate(obj)


class MapIngredientsResponse(BaseModel):
    """Response model for ingredient mapping"""
    recipe_id: str
    mappings: List[IngredientMapping]


class SaveWebRecipeRequest(BaseModel):
    """Request model for saving web recipe"""
    recipe_id: str
    name: str
    instructions: str
    cuisine: Optional[str]
    image_url: Optional[str]
    source_url: str
    ingredients_raw: List[Dict[str, str]]  # Original web ingredients
    ingredients_mapped: List[Dict[str, Any]]  # AI-mapped ingredients
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipe_id": "52772",
                "name": "Teriyaki Chicken Casserole",
                "instructions": "Preheat oven to 350°...",
                "cuisine": "Japanese",
                "image_url": "https://example.com/image.jpg",
                "source_url": "https://www.themealdb.com/meal/52772",
                "ingredients_raw": [
                    {"name": "soy sauce", "measure": "3/4 cup"}
                ],
                "ingredients_mapped": [
                    {
                        "recipe_ingredient": "soy sauce",
                        "mapped_to": "Soy Sauce",
                        "match_confidence": 1.0,
                        "match_type": "exact"
                    }
                ]
            }
        }


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/interpret_query", response_model=InterpretQueryResponse)
async def interpret_query(request: InterpretQueryRequest):
    """
    Endpoint 1: Interpret natural language query using GPT-4o-mini
    
    Converts user's natural text into structured search filters.
    Example: "quick Italian pasta without cheese" → 
    {"keywords": ["pasta"], "cuisine": "Italian", "restrictions": ["no cheese"]}
    """
    try:
        ai_service = get_ai_service()
        result = await ai_service.interpret_query(request.query)
        return InterpretQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error interpreting query: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to interpret query: {str(e)}"
        )


@router.post("/search_recipes", response_model=List[WebRecipeResponse])
async def search_recipes(request: SearchRecipesRequest):
    """
    Endpoint 2: Search recipes using TheMealDB API
    
    Takes structured filters and searches TheMealDB for matching recipes.
    Returns array of recipes with full details including ingredients.
    """
    try:
        mealdb_service = get_mealdb_service()
        
        # Primary search by query/keywords
        recipes = await mealdb_service.search_by_name(request.query)
        
        # Apply filters
        if request.cuisine:
            # Filter by cuisine (case-insensitive)
            cuisine_lower = request.cuisine.lower()
            recipes = [
                r for r in recipes 
                if r.get("area") and cuisine_lower in r["area"].lower()
            ]
        
        # Note: TheMealDB doesn't have cooking time or dietary restrictions
        # in the free API, so we can't filter by those directly
        # Could add AI-based filtering here if needed
        
        if not recipes:
            return []
        
        # Convert to response model
        response_recipes = []
        for recipe in recipes:
            response_recipes.append(WebRecipeResponse(
                id=recipe["id"],
                name=recipe["name"],
                image=recipe.get("image"),
                category=recipe.get("category"),
                area=recipe.get("area"),
                instructions=recipe["instructions"],
                ingredients=[
                    RecipeIngredient(name=ing["name"], measure=ing["measure"])
                    for ing in recipe["ingredients"]
                ],
                source_url=recipe["source_url"]
            ))
        
        return response_recipes
        
    except Exception as e:
        logger.error(f"Error searching recipes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search recipes: {str(e)}"
        )


@router.post("/map_ingredients", response_model=MapIngredientsResponse)
async def map_ingredients(
    request: MapIngredientsRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint 3: Map recipe ingredients to inventory using GPT-o3 reasoning
    
    Uses AI to semantically match recipe ingredients with restaurant's inventory.
    Returns confidence scores and suggests substitutes for missing items.
    """
    try:
        # Get all inventory items
        inventory_items = db.query(InventoryItem).all()
        inventory_list = [
            {"name": item.name, "unit": item.unit, "quantity": item.quantity}
            for item in inventory_items
        ]
        
        if not inventory_list:
            # No inventory to map against
            logger.warning("No inventory items found for mapping")
            return MapIngredientsResponse(
                recipe_id=request.recipe_id,
                mappings=[
                    IngredientMapping(
                        recipe_ingredient=ing["name"],
                        recipe_quantity=ing.get("quantity", ""),
                        recipe_unit=ing.get("unit", ""),
                        mapped_to=None,
                        match_confidence=0.0,
                        match_type="missing",
                        note="No inventory items available"
                    )
                    for ing in request.recipe_ingredients
                ]
            )
        
        # Use AI service to perform semantic matching
        ai_service = get_ai_service()
        mappings = await ai_service.map_ingredients(
            request.recipe_ingredients,
            inventory_list
        )
        
        # Convert to response model
        mapping_objects = [
            IngredientMapping(**mapping) for mapping in mappings
        ]
        
        return MapIngredientsResponse(
            recipe_id=request.recipe_id,
            mappings=mapping_objects
        )
        
    except Exception as e:
        logger.error(f"Error mapping ingredients: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to map ingredients: {str(e)}"
        )


@router.post("/save_recipe")
async def save_web_recipe(
    request: SaveWebRecipeRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Endpoint 4: Save imported web recipe to database
    
    Saves the recipe with both original and mapped ingredients.
    Links to user/restaurant and stores web metadata (source URL, image, etc.)
    """
    try:
        # Check if recipe name already exists
        existing_recipe = db.query(Recipe).filter(
            Recipe.name == request.name
        ).first()
        
        if existing_recipe:
            raise HTTPException(
                status_code=400,
                detail=f"Recipe '{request.name}' already exists in your catalogue"
            )
        
        # Convert mapped ingredients to the format used by existing recipes
        # Format: [{"name": "...", "qty": ..., "unit": "..."}]
        items_for_recipe = []
        for mapping in request.ingredients_mapped:
            if mapping.get("mapped_to"):  # Only include successfully mapped items
                items_for_recipe.append({
                    "name": mapping.get("mapped_to"),
                    "qty": float(mapping.get("recipe_quantity", 0)) if mapping.get("recipe_quantity") else 0,
                    "unit": mapping.get("recipe_unit", "pz")
                })
        
        # Create new recipe
        new_recipe = Recipe(
            name=request.name,
            items=json.dumps(items_for_recipe),
            instructions=request.instructions,
            source_url=request.source_url,
            image_url=request.image_url,
            cuisine=request.cuisine,
            ingredients_raw=json.dumps(request.ingredients_raw),
            ingredients_mapped=json.dumps(request.ingredients_mapped)
        )
        
        db.add(new_recipe)
        db.commit()
        db.refresh(new_recipe)
        
        return {
            "success": True,
            "message": f"Recipe '{request.name}' saved successfully",
            "recipe_id": new_recipe.id,
            "name": new_recipe.name,
            "items_count": len(items_for_recipe)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving recipe: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save recipe: {str(e)}"
        )


@router.get("/test")
async def test_web_recipes():
    """Test endpoint to verify the router is working"""
    return {
        "status": "ok",
        "message": "Web recipes router is operational",
        "endpoints": [
            "/interpret_query",
            "/search_recipes", 
            "/map_ingredients",
            "/save_recipe"
        ]
    }

