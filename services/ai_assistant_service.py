"""
AI Assistant Service for ChefCode
Handles intent detection, conversational AI, and action orchestration
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class IntentResult(BaseModel):
    """Structure for intent detection result"""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    requires_confirmation: bool = False
    response_message: str = ""


class AIAssistantService:
    """
    AI Assistant for natural language command processing
    Uses GPT-4o-mini for intent detection and conversational responses
    """
    
    # Supported intents
    INTENTS = {
        "add_inventory": "Add items to inventory",
        "update_inventory": "Update inventory quantities",
        "delete_inventory": "Remove items from inventory",
        "query_inventory": "Query inventory status",
        
        "add_recipe": "Add a new recipe manually",
        "edit_recipe": "Edit existing recipe",
        "delete_recipe": "Delete a recipe",
        "search_recipe_web": "Search recipes online",
        "show_recipe": "Display specific recipe",
        "import_recipe": "Import recipe from search results",
        
        "show_catalogue": "Show recipe catalogue",
        "filter_catalogue": "Filter recipes by category",
        
        "general_query": "General questions",
        "unknown": "Cannot determine intent"
    }
    
    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.conversation_context = []  # Store recent conversation for context
    
    async def detect_intent(self, user_input: str, context: Optional[Dict] = None) -> IntentResult:
        """
        Detect user intent from natural language input
        
        Args:
            user_input: User's natural language command
            context: Optional conversation context
            
        Returns:
            IntentResult with detected intent and extracted entities
        """
        try:
            system_prompt = self._build_intent_detection_prompt()
            
            # Add context if available
            context_info = ""
            if context:
                context_info = f"\n\nConversation context: {json.dumps(context)}"
            
            user_prompt = f"""Analyze this user command and return a structured JSON response:
            
User Input: "{user_input}"{context_info}

Return JSON with this structure:
{{
    "intent": "intent_name",
    "confidence": 0.95,
    "entities": {{
        // Extracted entities based on intent
    }},
    "requires_confirmation": true/false,
    "response_message": "Conversational response to user"
}}

IMPORTANT: Return ONLY the JSON, no markdown formatting."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean markdown if present
            if result_text.startswith("```"):
                lines = result_text.split('\n')
                result_text = '\n'.join([l for l in lines if not l.startswith("```")])
            
            result_dict = json.loads(result_text)
            
            return IntentResult(**result_dict)
            
        except Exception as e:
            logger.error(f"Intent detection error: {str(e)}")
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                entities={},
                response_message=f"I'm not sure what you mean. Could you rephrase that?"
            )
    
    async def parse_recipe_from_text(self, user_input: str) -> Dict[str, Any]:
        """
        Parse recipe details from natural language
        Example: "Add a recipe called Pizza with flour 100 kg and tomato sauce 200 ml"
        
        Returns:
            {
                "recipe_name": "Pizza",
                "ingredients": [
                    {"name": "flour", "quantity": 100, "unit": "kg"},
                    {"name": "tomato sauce", "quantity": 200, "unit": "ml"}
                ],
                "yield_qty": 1,
                "yield_unit": "piece"
            }
        """
        try:
            prompt = f"""You are a recipe parsing expert. Extract ALL ingredient information from this command.

User Input: "{user_input}"

CRITICAL RULES:
1. Extract the recipe name
2. For EACH ingredient, extract:
   - name (ingredient name)
   - quantity (numeric value, if missing use null)
   - unit (measurement unit like kg, g, ml, liters, pieces, etc. If missing use null)
3. Extract yield if mentioned (default: null)

EXAMPLES:
"Add recipe Pizza with flour 500 grams and tomato 200 ml"
→ {{"recipe_name": "Pizza", "ingredients": [{{"name": "flour", "quantity": 500, "unit": "grams"}}, {{"name": "tomato", "quantity": 200, "unit": "ml"}}], "yield_qty": null, "yield_unit": null}}

"Add recipe spaghetti with flour and salt"
→ {{"recipe_name": "spaghetti", "ingredients": [{{"name": "flour", "quantity": null, "unit": null}}, {{"name": "salt", "quantity": null, "unit": null}}], "yield_qty": null, "yield_unit": null}}

Return ONLY valid JSON, no markdown, no explanation:
{{
    "recipe_name": "string",
    "ingredients": [
        {{"name": "string", "quantity": number or null, "unit": "string or null"}},
        ...
    ],
    "yield_qty": number or null,
    "yield_unit": "string or null",
    "instructions": "string or empty"
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise recipe data extractor. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean markdown
            if result.startswith("```"):
                lines = result.split('\n')
                result = '\n'.join([l for l in lines if not l.startswith("```")])
            
            parsed = json.loads(result)
            
            # Convert null to proper values
            for ing in parsed.get('ingredients', []):
                if ing.get('quantity') is None:
                    ing['quantity'] = None
                if ing.get('unit') is None:
                    ing['unit'] = None
            
            return parsed
            
        except Exception as e:
            logger.error(f"Recipe parsing error: {str(e)}")
            raise ValueError(f"Could not parse recipe: {str(e)}")
    
    async def generate_response(self, intent: str, action_result: Dict[str, Any]) -> str:
        """
        Generate a conversational response based on the action result
        
        Args:
            intent: The detected intent
            action_result: Result from the action handler
            
        Returns:
            Conversational response string
        """
        try:
            prompt = f"""Generate a short, friendly response for this action:

Intent: {intent}
Action Result: {json.dumps(action_result)}

Rules:
- Be conversational and concise (max 2 sentences)
- Use emojis sparingly for emphasis
- Confirm what was done
- If error, be helpful and suggest alternatives

Return only the response text, nothing else."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are ChefCode's friendly AI assistant. Be concise and helpful."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            return "Action completed." if action_result.get("success") else "Something went wrong."
    
    def _build_intent_detection_prompt(self) -> str:
        """Build the system prompt for intent detection with examples"""
        return """You are ChefCode's intelligent assistant. Analyze user commands and detect their intent.

SUPPORTED INTENTS:

📦 INVENTORY:
- add_inventory: Add items to inventory
  Example: "Add 5 kg of rice at 2.50 euros"
  Entities: {"item_name": "rice", "quantity": 5, "unit": "kg", "price": 2.50, "category": "Grains"}
  IMPORTANT: 
  - Always extract price if mentioned (at, for, cost, price, euro, dollar, etc.)
  - ALWAYS infer the category from the item name using these categories:
    * "Meat" - beef, chicken, pork, lamb, fish, seafood, etc.
    * "Vegetables" - tomatoes, onions, lettuce, carrots, peppers, etc.
    * "Fruits" - apples, oranges, bananas, berries, etc.
    * "Dairy" - milk, cheese, butter, yogurt, cream, etc.
    * "Grains" - rice, pasta, flour, bread, cereals, etc.
    * "Beverages" - water, juice, soda, wine, beer, etc.
    * "Spices" - salt, pepper, herbs, seasonings, etc.
    * "Oils" - olive oil, vegetable oil, cooking oil, etc.
    * "Other" - only if item doesn't fit any category above
  
  More examples:
  - "Add 10 kg of tomatoes" → category: "Vegetables"
  - "Add 2 liters of milk" → category: "Dairy"
  - "Add 500 grams of chicken" → category: "Meat"
  - "Add 1 liter of olive oil" → category: "Oils"

- update_inventory: Update quantities
  Example: "Update flour to 10 kg"
  Entities: {"item_name": "flour", "quantity": 10, "unit": "kg"}

- delete_inventory: Remove items
  Example: "Remove tomatoes from inventory"
  Entities: {"item_name": "tomatoes"}

- query_inventory: Check stock
  Example: "How much rice do we have?"
  Entities: {"item_name": "rice"}

🍳 RECIPE MANAGEMENT:
- add_recipe: Create new recipe manually
  Example: "Add a recipe called Pizza with flour 100 kg and cheese 50 kg"
  Entities: {"recipe_name": "Pizza", "raw_text": "...full input..."}

- edit_recipe: Modify existing recipe (add/remove/change ingredient)
  Example: "Edit recipe Pizza by adding 2 grams of salt"
  Entities: {"recipe_name": "Pizza", "action": "adding", "ingredient_name": "salt", "quantity": "2", "unit": "grams"}
  
  Example: "Remove flour from Pizza recipe"
  Entities: {"recipe_name": "Pizza", "action": "remove", "ingredient_name": "flour"}
  
  Example: "Change tomatoes in Pizza to 500 grams"
  Entities: {"recipe_name": "Pizza", "action": "change", "ingredient_name": "tomatoes", "quantity": "500", "unit": "grams"}

- delete_recipe: Remove recipe
  Example: "Delete the recipe Pasta"
  Entities: {"recipe_name": "Pasta"}

- search_recipe_web: Search recipes online
  Example: "Search pasta recipes" or "Find Italian recipes"
  Entities: {"query": "pasta", "filters": {"cuisine": "Italian"}}

- show_recipe: Display specific recipe
  Example: "Show me the Pizza recipe"
  Entities: {"recipe_name": "Pizza"}

- import_recipe: Import from search results
  Example: "Import the second one" or "Import that recipe"
  Entities: {"index": 2, "recipe_id": "..."}

📚 CATALOGUE:
- show_catalogue: Show all recipes
  Example: "Show all recipes" or "Open recipe catalogue"
  Entities: {}

- filter_catalogue: Filter by category
  Example: "Show dessert recipes"
  Entities: {"category": "dessert"}

❓ OTHER:
- general_query: General questions
- unknown: Cannot determine

RULES:
1. Set requires_confirmation=true for destructive actions (add, update, delete)
2. Extract ALL relevant entities from the input
3. Be conversational in response_message
4. If ambiguous, ask clarifying questions
5. For numbers, always extract both quantity and unit
6. For recipe commands, capture the full raw text for later parsing

Return JSON only, no markdown."""

    def add_to_context(self, role: str, content: str):
        """Add message to conversation context"""
        self.conversation_context.append({"role": role, "content": content})
        # Keep only last 10 messages
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]
    
    def clear_context(self):
        """Clear conversation context"""
        self.conversation_context = []

