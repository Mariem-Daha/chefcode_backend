"""
TheMealDB API Service
Provides recipe search functionality using TheMealDB public API
API Documentation: https://www.themealdb.com/api.php
"""

import httpx
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MealDBService:
    """Service for interacting with TheMealDB API"""
    
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    
    def __init__(self):
        """Initialize MealDB service"""
        self.base_url = self.BASE_URL
    
    async def search_by_name(self, query: str) -> List[Dict[str, Any]]:
        """
        Search recipes by name using TheMealDB API
        
        Args:
            query: Search query string (e.g., "pasta", "chicken")
        
        Returns:
            List of recipe dictionaries with structure:
            [{
                "id": str,
                "name": str,
                "image": str (URL),
                "category": str,
                "area": str (cuisine),
                "instructions": str,
                "ingredients": [{"name": str, "measure": str}],
                "source_url": str
            }]
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/search.php",
                    params={"s": query}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("meals"):
                    return []
                
                # Parse and structure the recipes
                recipes = []
                for meal in data["meals"]:
                    # Extract ingredients and measures (TheMealDB has 20 ingredient slots)
                    ingredients = []
                    for i in range(1, 21):
                        ingredient_name = meal.get(f"strIngredient{i}", "")
                        ingredient_measure = meal.get(f"strMeasure{i}", "")
                        
                        if ingredient_name and ingredient_name.strip():
                            ingredients.append({
                                "name": ingredient_name.strip(),
                                "measure": ingredient_measure.strip() if ingredient_measure else ""
                            })
                    
                    recipe = {
                        "id": meal.get("idMeal"),
                        "name": meal.get("strMeal"),
                        "image": meal.get("strMealThumb"),
                        "category": meal.get("strCategory"),
                        "area": meal.get("strArea"),  # Cuisine type
                        "instructions": meal.get("strInstructions", ""),
                        "ingredients": ingredients,
                        "source_url": meal.get("strSource") or meal.get("strYoutube") or "",
                        "tags": meal.get("strTags", "").split(",") if meal.get("strTags") else []
                    }
                    recipes.append(recipe)
                
                return recipes
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching TheMealDB: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error searching TheMealDB: {str(e)}")
            return []
    
    async def search_by_ingredient(self, ingredient: str) -> List[Dict[str, Any]]:
        """
        Search recipes by main ingredient
        
        Args:
            ingredient: Main ingredient name (e.g., "chicken", "beef")
        
        Returns:
            List of simplified recipe info (less detail than search_by_name)
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/filter.php",
                    params={"i": ingredient}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("meals"):
                    return []
                
                # This endpoint returns limited info, so we'll return basic structure
                recipes = []
                for meal in data["meals"]:
                    recipe = {
                        "id": meal.get("idMeal"),
                        "name": meal.get("strMeal"),
                        "image": meal.get("strMealThumb"),
                        "category": None,
                        "area": None,
                        "instructions": None,
                        "ingredients": [],
                        "source_url": ""
                    }
                    recipes.append(recipe)
                
                return recipes
                
        except Exception as e:
            logger.error(f"Error searching by ingredient: {str(e)}")
            return []
    
    async def get_recipe_by_id(self, meal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full recipe details by ID
        
        Args:
            meal_id: TheMealDB recipe ID
        
        Returns:
            Full recipe dictionary or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/lookup.php",
                    params={"i": meal_id}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("meals") or len(data["meals"]) == 0:
                    return None
                
                meal = data["meals"][0]
                
                # Extract ingredients
                ingredients = []
                for i in range(1, 21):
                    ingredient_name = meal.get(f"strIngredient{i}", "")
                    ingredient_measure = meal.get(f"strMeasure{i}", "")
                    
                    if ingredient_name and ingredient_name.strip():
                        ingredients.append({
                            "name": ingredient_name.strip(),
                            "measure": ingredient_measure.strip() if ingredient_measure else ""
                        })
                
                recipe = {
                    "id": meal.get("idMeal"),
                    "name": meal.get("strMeal"),
                    "image": meal.get("strMealThumb"),
                    "category": meal.get("strCategory"),
                    "area": meal.get("strArea"),
                    "instructions": meal.get("strInstructions", ""),
                    "ingredients": ingredients,
                    "source_url": meal.get("strSource") or meal.get("strYoutube") or "",
                    "tags": meal.get("strTags", "").split(",") if meal.get("strTags") else []
                }
                
                return recipe
                
        except Exception as e:
            logger.error(f"Error fetching recipe by ID: {str(e)}")
            return None


# Singleton instance
_mealdb_service: Optional[MealDBService] = None

def get_mealdb_service() -> MealDBService:
    """Get or create the MealDB service singleton"""
    global _mealdb_service
    if _mealdb_service is None:
        _mealdb_service = MealDBService()
    return _mealdb_service

