"""
AI Service Module
Handles interactions with OpenAI models (GPT-4o-mini and GPT-o3 reasoning)
"""

import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered recipe interpretation and ingredient mapping"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.gpt_4o_mini_model = "gpt-4o-mini"
        # Use o3 reasoning model for ingredient mapping
        self.gpt_o3_model = "o3"
    
    async def interpret_query(self, user_query: str) -> Dict[str, Any]:
        """
        Use GPT-4o-mini to interpret natural language recipe search query
        
        Args:
            user_query: Natural language search query (e.g., "quick Italian pasta without cheese")
        
        Returns:
            Structured filters dictionary with:
            - keywords: List of search keywords
            - cuisine: Cuisine type (optional)
            - restrictions: List of dietary restrictions (optional)
            - max_time: Maximum cooking time in minutes (optional)
        
        Example response:
        {
            "keywords": ["pasta"],
            "cuisine": "Italian",
            "restrictions": ["no cheese"],
            "max_time": 30
        }
        """
        try:
            system_prompt = """You are a culinary assistant that interprets recipe search queries.
Extract structured information from natural language queries.

Return ONLY valid JSON with these fields:
- keywords: array of strings (main ingredients or dish types to search)
- cuisine: string or null (e.g., "Italian", "Chinese", "Mexican")
- restrictions: array of strings (dietary restrictions like "no cheese", "vegetarian", "vegan")
- max_time: number or null (maximum cooking time in minutes)

Examples:
Query: "quick Italian pasta without cheese"
Response: {"keywords": ["pasta"], "cuisine": "Italian", "restrictions": ["no cheese"], "max_time": 30}

Query: "spicy chicken curry"
Response: {"keywords": ["chicken", "curry"], "cuisine": null, "restrictions": ["spicy"], "max_time": null}

Query: "easy vegetarian soup under 20 minutes"
Response: {"keywords": ["soup"], "cuisine": null, "restrictions": ["vegetarian"], "max_time": 20}
"""
            
            response = self.client.chat.completions.create(
                model=self.gpt_4o_mini_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure all required fields exist with defaults
            return {
                "keywords": result.get("keywords", []),
                "cuisine": result.get("cuisine"),
                "restrictions": result.get("restrictions", []),
                "max_time": result.get("max_time")
            }
            
        except Exception as e:
            logger.error(f"Error interpreting query: {str(e)}")
            # Fallback: return simple keyword extraction
            return {
                "keywords": [user_query],
                "cuisine": None,
                "restrictions": [],
                "max_time": None
            }
    
    async def map_ingredients(
        self, 
        recipe_ingredients: List[Dict[str, str]], 
        inventory_items: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Use AI reasoning to semantically map recipe ingredients to inventory
        Uses gpt-4o-mini for reliable ingredient matching
        
        Args:
            recipe_ingredients: List of recipe ingredients [{"name": "...", "quantity": "...", "unit": "..."}]
            inventory_items: List of inventory items [{"name": "...", "unit": "..."}]
        
        Returns:
            List of mapping results:
            [{
                "recipe_ingredient": str,
                "recipe_quantity": str,
                "recipe_unit": str,
                "mapped_to": str or null,
                "match_confidence": float (0.0-1.0),
                "match_type": "exact" | "substitute" | "missing",
                "note": str (explanation or suggestion)
            }]
        """
        # Use gpt-4o-mini for reliable matching
        models_to_try = ["gpt-4o-mini", "gpt-4"]
        
        for model_name in models_to_try:
            try:
                print(f"Attempting ingredient mapping with model: {model_name}")
                return await self._map_with_model(model_name, recipe_ingredients, inventory_items)
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {str(e)}")
                print(f"WARNING: {model_name} failed: {str(e)}")
                if model_name == models_to_try[-1]:  # Last model
                    raise
                else:
                    print(f"Falling back to next model...")
                    continue
        
        # This should never be reached, but just in case
        raise Exception("All AI models failed")
    
    async def _map_with_model(
        self,
        model_name: str,
        recipe_ingredients: List[Dict[str, str]], 
        inventory_items: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Internal method to map ingredients using a specific model"""
        try:
            # Prepare data for the AI
            recipe_list = "\n".join([
                f"- {ing.get('name', 'Unknown')} ({ing.get('quantity', '')} {ing.get('unit', '')})"
                for ing in recipe_ingredients
            ])
            
            inventory_list = "\n".join([
                f"- {item.get('name', 'Unknown')} ({item.get('unit', 'pz')})"
                for item in inventory_items
            ])
            
            system_prompt = """You are an expert AI sous-chef specializing in ingredient matching and substitutions.

Your task: Match recipe ingredients to the restaurant's inventory items semantically.

Rules:
1. EXACT MATCH: Same ingredient or very similar (e.g., "tomatoes" → "San Marzano tomatoes")
2. SUBSTITUTE: Compatible replacement (e.g., "butter" → "margarine", "basil" → "dried basil")
3. MISSING: No suitable match exists in inventory

For each recipe ingredient, analyze and return:
- recipe_ingredient: exact name from recipe
- recipe_quantity: amount needed
- recipe_unit: unit of measurement
- mapped_to: inventory item name (or null if missing)
- match_confidence: 0.0 to 1.0 (1.0 = perfect match)
- match_type: "exact" | "substitute" | "missing"
- note: Brief explanation or substitution advice

Return ONLY valid JSON array. No markdown, no extra text."""
            
            user_prompt = f"""Recipe Ingredients:
{recipe_list}

Inventory Available:
{inventory_list}

Match each recipe ingredient to inventory. Return JSON array of mappings."""
            
            # Use standard chat completion for all models
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            result = response.choices[0].message.content
            
            # Debug: Print the raw response
            print(f"DEBUG: Raw AI response: {result[:500] if result else 'EMPTY'}")
            
            if not result or not result.strip():
                logger.error("AI returned empty response")
                raise ValueError("AI returned empty response")
            
            # Try to extract JSON if wrapped in markdown code blocks
            if result.startswith("```"):
                # Extract JSON from markdown code block
                lines = result.split('\n')
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or (not line.startswith("```") and json_lines):
                        json_lines.append(line)
                result = '\n'.join(json_lines).strip()
            
            # Parse response - handle if it's wrapped in a root key
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                # If response has a wrapper key like "mappings", extract it
                if "mappings" in parsed:
                    mappings = parsed["mappings"]
                elif "ingredients" in parsed:
                    mappings = parsed["ingredients"]
                else:
                    # Try to find the first list value
                    mappings = None
                    for value in parsed.values():
                        if isinstance(value, list):
                            mappings = value
                            break
                    if not mappings:
                        mappings = []
            else:
                mappings = parsed if isinstance(parsed, list) else []
            
            # Ensure all recipe_quantity values are strings
            for mapping in mappings:
                if 'recipe_quantity' in mapping and not isinstance(mapping['recipe_quantity'], str):
                    mapping['recipe_quantity'] = str(mapping['recipe_quantity'])
            
            return mappings
            
        except Exception as e:
            logger.error(f"Error mapping ingredients: {str(e)}")
            print(f"ERROR in map_ingredients: {str(e)}")  # Debug print
            import traceback
            traceback.print_exc()  # Print full traceback
            # Fallback: return basic structure marking all as missing
            return [
                {
                    "recipe_ingredient": ing.get("name", "Unknown"),
                    "recipe_quantity": ing.get("quantity", ""),
                    "recipe_unit": ing.get("unit", ""),
                    "mapped_to": None,
                    "match_confidence": 0.0,
                    "match_type": "missing",
                    "note": f"Unable to perform AI matching: {str(e)}"
                }
                for ing in recipe_ingredients
            ]


# Singleton instance
_ai_service: Optional[AIService] = None

def get_ai_service() -> AIService:
    """Get or create the AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

