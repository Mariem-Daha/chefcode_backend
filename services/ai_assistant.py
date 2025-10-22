"""
AI Assistant API Routes
Handles natural language commands for inventory and recipe management
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Recipe, InventoryItem
from services.ai_assistant_service import AIAssistantService
from services.ai_service import AIService
from services.mealdb_service import MealDBService
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize services
ai_assistant = AIAssistantService()
ai_service = AIService()
mealdb_service = MealDBService()


# ===== REQUEST/RESPONSE MODELS =====

class CommandRequest(BaseModel):
    """Request model for AI command"""
    command: str = Field(..., description="Natural language command from user")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Conversation context")


class CommandResponse(BaseModel):
    """Response model for AI command"""
    intent: str
    confidence: float
    message: str
    requires_confirmation: bool = False
    confirmation_data: Optional[Dict[str, Any]] = None
    action_result: Optional[Dict[str, Any]] = None
    search_results: Optional[List[Dict]] = None


class ConfirmationRequest(BaseModel):
    """Request model for confirming an action"""
    confirmation_id: str
    confirmed: bool
    data: Dict[str, Any]


# ===== MAIN COMMAND ENDPOINT =====

@router.post("/command", response_model=CommandResponse)
async def process_command(
    request: CommandRequest,
    db: Session = Depends(get_db)
):
    """
    Process a natural language command from the user
    Detects intent and either executes or requests confirmation
    """
    try:
        # Detect intent
        intent_result = await ai_assistant.detect_intent(
            request.command,
            request.context
        )
        
        logger.info(f"Detected intent: {intent_result.intent} (confidence: {intent_result.confidence})")
        
        # Route to appropriate handler
        if intent_result.intent.startswith("add_inventory"):
            return await handle_add_inventory(intent_result, db)
        
        elif intent_result.intent.startswith("update_inventory"):
            return await handle_update_inventory(intent_result, db)
        
        elif intent_result.intent.startswith("delete_inventory"):
            return await handle_delete_inventory(intent_result, db)
        
        elif intent_result.intent == "query_inventory":
            return await handle_query_inventory(intent_result, db)
        
        elif intent_result.intent == "add_recipe":
            return await handle_add_recipe(intent_result, request.command, db)
        
        elif intent_result.intent == "edit_recipe":
            return await handle_edit_recipe(intent_result, request.command, db)
        
        elif intent_result.intent == "delete_recipe":
            return await handle_delete_recipe(intent_result, db)
        
        elif intent_result.intent == "search_recipe_web":
            return await handle_search_recipe_web(intent_result)
        
        elif intent_result.intent == "show_recipe":
            return await handle_show_recipe(intent_result, db)
        
        elif intent_result.intent == "show_catalogue":
            return handle_show_catalogue(db)
        
        elif intent_result.intent == "filter_catalogue":
            return handle_filter_catalogue(intent_result, db)
        
        else:
            return CommandResponse(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                message=intent_result.response_message or "I'm not sure how to help with that. Try rephrasing?",
                requires_confirmation=False
            )
            
    except Exception as e:
        logger.error(f"Command processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== CONFIRMATION ENDPOINT =====

@router.post("/confirm")
async def confirm_action(
    request: ConfirmationRequest,
    db: Session = Depends(get_db)
):
    """Execute a confirmed action"""
    try:
        if not request.confirmed:
            return {"message": "Action cancelled.", "success": False}
        
        # Execute based on intent stored in confirmation_data
        intent = request.data.get("intent")
        
        if intent == "add_recipe":
            return await execute_add_recipe(request.data, db)
        
        elif intent == "delete_recipe":
            return await execute_delete_recipe(request.data, db)
        
        elif intent == "edit_recipe":
            return await execute_edit_recipe(request.data, db)
        
        elif intent == "add_inventory":
            return await execute_add_inventory(request.data, db)
        
        elif intent == "update_inventory":
            return await execute_update_inventory(request.data, db)
        
        elif intent == "delete_inventory":
            return await execute_delete_inventory(request.data, db)
        
        else:
            return {"message": "Unknown action", "success": False}
            
    except Exception as e:
        logger.error(f"Confirmation execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== INVENTORY HANDLERS =====

async def handle_add_inventory(intent_result, db: Session) -> CommandResponse:
    """Handle add inventory intent with validation - checks if item exists first"""
    entities = intent_result.entities
    
    # Validate mandatory fields
    missing_fields = []
    
    if not entities.get('item_name'):
        missing_fields.append('item name')
    if not entities.get('quantity'):
        missing_fields.append('quantity')
    if not entities.get('unit'):
        missing_fields.append('unit')
    
    # If any mandatory fields are missing, ask for them
    if missing_fields:
        fields_text = ', '.join(missing_fields)
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"📝 To add inventory, I need the {fields_text}. Please provide the missing information.\n\nExample: 'Add 5 kg of rice' or 'Add 10 liters of milk at 2.50 euros'",
            requires_confirmation=False,
            action_result={
                "awaiting_fields": missing_fields,
                "partial_data": entities
            }
        )
    
    # Check if item already exists
    existing_item = db.query(InventoryItem).filter(
        InventoryItem.name.ilike(f"%{entities.get('item_name')}%")
    ).first()
    
    category = entities.get('category', 'Other')
    
    if existing_item:
        # Item exists - will add to existing quantity
        new_total = existing_item.quantity + entities.get('quantity')
        price_info = ""
        if entities.get('price'):
            price_info = f" at €{entities.get('price')}/{entities.get('unit')}"
        
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"📦 '{existing_item.name}' already exists with {existing_item.quantity} {existing_item.unit}.\n\nAdd {entities.get('quantity')} {entities.get('unit')}{price_info}?\n(New total: {new_total} {entities.get('unit')})",
            requires_confirmation=True,
            confirmation_data={
                "intent": "add_inventory",
                "item_name": entities.get('item_name'),
                "quantity": entities.get('quantity'),
                "unit": entities.get('unit'),
                "category": category,
                "price": entities.get('price'),
                "existing_item_id": existing_item.id,
                "is_update": True
            }
        )
    else:
        # New item - need price
        if not entities.get('price'):
            return CommandResponse(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                message=f"📝 '{entities.get('item_name')}' is a new item. Please provide the unit price.\n\nExample: 'Add {entities.get('quantity')} {entities.get('unit')} of {entities.get('item_name')} at 2.50 euros'",
                requires_confirmation=False,
                action_result={
                    "awaiting_price": True,
                    "partial_data": entities
                }
            )
        
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"➕ Add new item: {entities.get('quantity')} {entities.get('unit')} of {entities.get('item_name')} at €{entities.get('price')}/{entities.get('unit')}. Confirm?",
            requires_confirmation=True,
            confirmation_data={
                "intent": "add_inventory",
                "item_name": entities.get('item_name'),
                "quantity": entities.get('quantity'),
                "unit": entities.get('unit'),
                "category": category,
                "price": entities.get('price'),
                "is_update": False
            }
        )


async def handle_update_inventory(intent_result, db: Session) -> CommandResponse:
    """Handle update inventory intent"""
    entities = intent_result.entities
    
    # Check if item exists
    item = db.query(InventoryItem).filter(
        InventoryItem.name.ilike(f"%{entities.get('item_name')}%")
    ).first()
    
    if not item:
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"❌ Item '{entities.get('item_name')}' not found in inventory.",
            requires_confirmation=False
        )
    
    return CommandResponse(
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        message=f"Update {item.name} from {item.quantity} {item.unit} to {entities.get('quantity')} {entities.get('unit')}?",
        requires_confirmation=True,
        confirmation_data={
            "intent": "update_inventory",
            "item_id": item.id,
            "quantity": entities.get('quantity'),
            "unit": entities.get('unit')
        }
    )


async def handle_delete_inventory(intent_result, db: Session) -> CommandResponse:
    """Handle delete inventory intent"""
    entities = intent_result.entities
    
    item = db.query(InventoryItem).filter(
        InventoryItem.name.ilike(f"%{entities.get('item_name')}%")
    ).first()
    
    if not item:
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"❌ Item '{entities.get('item_name')}' not found.",
            requires_confirmation=False
        )
    
    return CommandResponse(
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        message=f"⚠️ Delete {item.name} from inventory?",
        requires_confirmation=True,
        confirmation_data={
            "intent": "delete_inventory",
            "item_id": item.id
        }
    )


async def handle_query_inventory(intent_result, db: Session) -> CommandResponse:
    """Handle inventory query intent"""
    entities = intent_result.entities
    item_name = entities.get('item_name')
    
    if item_name:
        item = db.query(InventoryItem).filter(
            InventoryItem.name.ilike(f"%{item_name}%")
        ).first()
        
        if item:
            message = f"📦 {item.name}: {item.quantity} {item.unit}"
            if item.expiry_date:
                message += f"\nExpires: {item.expiry_date}"
        else:
            message = f"❌ '{item_name}' not found in inventory."
    else:
        # Show all inventory count
        count = db.query(InventoryItem).count()
        message = f"📦 You have {count} items in inventory."
    
    return CommandResponse(
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        message=message,
        requires_confirmation=False
    )


# ===== RECIPE HANDLERS =====

async def handle_add_recipe(intent_result, full_command: str, db: Session) -> CommandResponse:
    """Handle add recipe intent - parse and confirm with validation"""
    try:
        # Parse recipe from natural language
        recipe_data = await ai_assistant.parse_recipe_from_text(full_command)
        
        # Validate mandatory fields
        missing_fields = []
        
        if not recipe_data.get('recipe_name'):
            missing_fields.append('recipe name')
        
        if not recipe_data.get('ingredients') or len(recipe_data.get('ingredients', [])) == 0:
            missing_fields.append('ingredients')
        
        # If mandatory fields are missing, ask for them
        if missing_fields:
            fields_text = ' and '.join(missing_fields)
            
            if 'ingredients' in missing_fields:
                return CommandResponse(
                    intent=intent_result.intent,
                    confidence=intent_result.confidence,
                    message=f"📝 To add a recipe, I need the {fields_text}.\n\nPlease tell me the ingredients for this recipe.\n\nExample: 'flour 500 grams, tomato sauce 200 ml, and cheese 50 grams'",
                    requires_confirmation=False,
                    action_result={
                        "awaiting_ingredients": True,
                        "recipe_name": recipe_data.get('recipe_name')
                    }
                )
            else:
                return CommandResponse(
                    intent=intent_result.intent,
                    confidence=intent_result.confidence,
                    message=f"📝 I need the {fields_text} to add the recipe.\n\nExample: 'Add recipe Pizza with flour 500 grams'",
                    requires_confirmation=False
                )
        
        # Check if recipe already exists
        existing = db.query(Recipe).filter(Recipe.name == recipe_data['recipe_name']).first()
        if existing:
            return CommandResponse(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                message=f"❌ Recipe '{recipe_data['recipe_name']}' already exists.",
                requires_confirmation=False
            )
        
        # Validate ingredient quantities and units
        missing_quantities = []
        for ing in recipe_data['ingredients']:
            if ing.get('quantity') is None or ing.get('unit') is None:
                missing_quantities.append(ing['name'])
        
        if missing_quantities:
            ingredients_text = ', '.join(missing_quantities)
            return CommandResponse(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                message=f"📝 Please provide quantities and units for: {ingredients_text}\n\nExample: 'flour 500 grams, salt 10 grams'",
                requires_confirmation=False,
                action_result={
                    "awaiting_quantities": True,
                    "recipe_name": recipe_data['recipe_name'],
                    "ingredients": recipe_data['ingredients']
                }
            )
        
        # Check for yield
        if recipe_data.get('yield_qty') is None or recipe_data.get('yield_unit') is None:
            # Build ingredients list
            ingredients_list = "\n".join([
                f"  • {ing['name']}: {ing['quantity']} {ing['unit']}"
                for ing in recipe_data['ingredients']
            ])
            
            return CommandResponse(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                message=f"📝 Recipe '{recipe_data['recipe_name']}' with:\n\n{ingredients_list}\n\n⚖️ What is the yield?\n\nExample: '10 servings' or '2 pizzas' or '5 liters'",
                requires_confirmation=False,
                action_result={
                    "awaiting_yield": True,
                    "recipe_data": recipe_data
                }
            )
        
        # Build confirmation message
        ingredients_list = "\n".join([
            f"  • {ing['name']}: {ing['quantity']} {ing['unit']}"
            for ing in recipe_data['ingredients']
        ])
        
        message = f"📝 Add recipe '{recipe_data['recipe_name']}'?\n\nIngredients:\n{ingredients_list}\n\nYield: {recipe_data['yield_qty']} {recipe_data['yield_unit']}"
        
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=message,
            requires_confirmation=True,
            confirmation_data={
                "intent": "add_recipe",
                "recipe_data": recipe_data
            }
        )
        
    except Exception as e:
        logger.error(f"Recipe parsing error: {str(e)}")
        return CommandResponse(
            intent=intent_result.intent,
            confidence=0.0,
            message=f"❌ Could not parse recipe. Please provide the recipe name and ingredients.\n\nExample: 'Add recipe Pizza with flour 500 grams and tomato sauce 200 ml'",
            requires_confirmation=False
        )


async def handle_edit_recipe(intent_result, full_command: str, db: Session) -> CommandResponse:
    """Handle edit recipe intent - parse and execute the edit"""
    entities = intent_result.entities
    recipe_name = entities.get('recipe_name')
    
    recipe = db.query(Recipe).filter(Recipe.name.ilike(f"%{recipe_name}%")).first()
    
    if not recipe:
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"❌ Recipe '{recipe_name}' not found.",
            requires_confirmation=False
        )
    
    # Parse the edit action from the full command
    action = entities.get('action', '')  # add, remove, change
    ingredient_name = entities.get('ingredient_name', '')
    quantity = entities.get('quantity', '')
    unit = entities.get('unit', '')
    
    # If we have enough info to make the edit
    if action and ingredient_name:
        message = f"✏️ Edit recipe '{recipe.name}':\n"
        
        if action.lower() in ['add', 'adding']:
            message += f"  • Add {quantity} {unit} of {ingredient_name}"
        elif action.lower() in ['remove', 'removing', 'delete']:
            message += f"  • Remove {ingredient_name}"
        elif action.lower() in ['change', 'update', 'modify']:
            message += f"  • Change {ingredient_name} to {quantity} {unit}"
        else:
            message += f"  • Modify {ingredient_name}"
        
        message += "\n\nConfirm?"
        
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=message,
            requires_confirmation=True,
            confirmation_data={
                "intent": "edit_recipe",
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "action": action.lower(),
                "ingredient_name": ingredient_name,
                "quantity": quantity,
                "unit": unit
            }
        )
    else:
        # Not enough information
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"✏️ To edit '{recipe.name}', please specify:\n\nExamples:\n  • 'Add 2 grams of salt'\n  • 'Remove flour'\n  • 'Change tomatoes to 500 grams'",
            requires_confirmation=False
        )


async def handle_delete_recipe(intent_result, db: Session) -> CommandResponse:
    """Handle delete recipe intent"""
    entities = intent_result.entities
    recipe_name = entities.get('recipe_name')
    
    recipe = db.query(Recipe).filter(Recipe.name.ilike(f"%{recipe_name}%")).first()
    
    if not recipe:
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"❌ Recipe '{recipe_name}' not found.",
            requires_confirmation=False
        )
    
    return CommandResponse(
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        message=f"⚠️ Delete recipe '{recipe.name}'? This cannot be undone.",
        requires_confirmation=True,
        confirmation_data={
            "intent": "delete_recipe",
            "recipe_id": recipe.id,
            "recipe_name": recipe.name
        }
    )


async def handle_search_recipe_web(intent_result) -> CommandResponse:
    """Handle search recipe web intent - triggers existing web recipe modal"""
    entities = intent_result.entities
    query = entities.get('query', '')
    
    try:
        # Just return a success message with the query
        # The frontend will handle opening the existing web recipe search modal
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"🔍 Opening recipe search for '{query}'...",
            requires_confirmation=False,
            search_results=[{"trigger": "web_recipe_search"}],  # Signal to frontend
            action_result={"search_query": query}
        )
        
    except Exception as e:
        logger.error(f"Recipe search error: {str(e)}")
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"❌ Search failed: {str(e)}",
            requires_confirmation=False
        )


async def handle_show_recipe(intent_result, db: Session) -> CommandResponse:
    """Handle show recipe intent"""
    entities = intent_result.entities
    recipe_name = entities.get('recipe_name')
    
    recipe = db.query(Recipe).filter(Recipe.name.ilike(f"%{recipe_name}%")).first()
    
    if not recipe:
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"❌ Recipe '{recipe_name}' not found.",
            requires_confirmation=False
        )
    
    # Parse items
    items = json.loads(recipe.items) if recipe.items else []
    ingredients_list = "\n".join([
        f"  • {item['name']}: {item.get('quantity', '?')} {item.get('unit', '')}"
        for item in items
    ])
    
    message = f"📖 **{recipe.name}**\n\nIngredients:\n{ingredients_list}"
    if recipe.instructions:
        message += f"\n\n{recipe.instructions[:200]}..."
    
    return CommandResponse(
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        message=message,
        requires_confirmation=False,
        action_result={"recipe_id": recipe.id}
    )


def handle_show_catalogue(db: Session) -> CommandResponse:
    """Handle show catalogue intent"""
    recipes = db.query(Recipe).all()
    
    recipe_list = "\n".join([f"  • {r.name}" for r in recipes[:10]])
    message = f"📚 Recipe Catalogue ({len(recipes)} total):\n\n{recipe_list}"
    
    if len(recipes) > 10:
        message += f"\n  ... and {len(recipes) - 10} more"
    
    return CommandResponse(
        intent="show_catalogue",
        confidence=1.0,
        message=message,
        requires_confirmation=False,
        action_result={"total_recipes": len(recipes)}
    )


def handle_filter_catalogue(intent_result, db: Session) -> CommandResponse:
    """Handle filter catalogue intent"""
    entities = intent_result.entities
    category = entities.get('category', '').lower()
    
    # Filter recipes (basic text search in name/cuisine)
    recipes = db.query(Recipe).filter(
        (Recipe.name.ilike(f"%{category}%")) | 
        (Recipe.cuisine.ilike(f"%{category}%"))
    ).all()
    
    if not recipes:
        return CommandResponse(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=f"No recipes found in category '{category}'.",
            requires_confirmation=False
        )
    
    recipe_list = "\n".join([f"  • {r.name}" for r in recipes])
    
    return CommandResponse(
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        message=f"📚 {category.title()} Recipes ({len(recipes)}):\n\n{recipe_list}",
        requires_confirmation=False
    )


# ===== EXECUTION FUNCTIONS =====

async def execute_add_recipe(data: Dict, db: Session) -> Dict:
    """Execute confirmed recipe addition"""
    try:
        recipe_data = data['recipe_data']
        
        # Convert ingredients to items format with defaults (use 'qty' to match frontend)
        items = [
            {
                "name": ing['name'],
                "qty": ing.get('quantity') if ing.get('quantity') is not None else 1,
                "unit": ing.get('unit') if ing.get('unit') is not None else 'piece'
            }
            for ing in recipe_data['ingredients']
        ]
        
        # Create recipe with proper defaults
        yield_qty = recipe_data.get('yield_qty')
        yield_unit = recipe_data.get('yield_unit')
        
        # Only set yield_data if values are provided
        yield_data_dict = {}
        if yield_qty is not None and yield_unit is not None:
            yield_data_dict = {"qty": yield_qty, "unit": yield_unit}
        else:
            yield_data_dict = {"qty": 1, "unit": "serving"}
        
        new_recipe = Recipe(
            name=recipe_data['recipe_name'],
            items=json.dumps(items),
            instructions=recipe_data.get('instructions', ''),
            yield_data=json.dumps(yield_data_dict)
        )
        
        db.add(new_recipe)
        db.commit()
        
        return {
            "success": True,
            "message": f"✅ Recipe '{recipe_data['recipe_name']}' added successfully!"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Recipe add execution error: {str(e)}")
        return {"success": False, "message": f"❌ Failed to add recipe: {str(e)}"}


async def execute_delete_recipe(data: Dict, db: Session) -> Dict:
    """Execute confirmed recipe deletion"""
    try:
        recipe = db.query(Recipe).filter(Recipe.id == data['recipe_id']).first()
        if not recipe:
            return {"success": False, "message": "Recipe not found"}
        
        recipe_name = recipe.name
        db.delete(recipe)
        db.commit()
        
        return {
            "success": True,
            "message": f"✅ Recipe '{recipe_name}' deleted."
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Recipe delete execution error: {str(e)}")
        return {"success": False, "message": f"❌ Failed to delete recipe: {str(e)}"}


async def execute_edit_recipe(data: Dict, db: Session) -> Dict:
    """Execute confirmed recipe edit"""
    try:
        recipe = db.query(Recipe).filter(Recipe.id == data['recipe_id']).first()
        if not recipe:
            return {"success": False, "message": "Recipe not found"}
        
        # Parse current items
        items = json.loads(recipe.items) if recipe.items else []
        action = data.get('action', '')
        ingredient_name = data.get('ingredient_name', '').lower()
        quantity = data.get('quantity')
        unit = data.get('unit', '')
        
        # Find existing ingredient (case-insensitive)
        existing_idx = None
        for idx, item in enumerate(items):
            if item.get('name', '').lower() == ingredient_name:
                existing_idx = idx
                break
        
        # Perform action
        if action in ['add', 'adding']:
            if existing_idx is not None:
                # Update existing ingredient
                items[existing_idx]['qty'] = float(quantity) if quantity else items[existing_idx].get('qty', 1)
                items[existing_idx]['unit'] = unit if unit else items[existing_idx].get('unit', '')
                message = f"✅ Updated {ingredient_name} in '{recipe.name}'"
            else:
                # Add new ingredient
                items.append({
                    "name": ingredient_name,
                    "qty": float(quantity) if quantity else 1,
                    "unit": unit
                })
                message = f"✅ Added {quantity} {unit} of {ingredient_name} to '{recipe.name}'"
        
        elif action in ['remove', 'removing', 'delete']:
            if existing_idx is not None:
                removed = items.pop(existing_idx)
                message = f"✅ Removed {removed['name']} from '{recipe.name}'"
            else:
                return {"success": False, "message": f"❌ {ingredient_name} not found in recipe"}
        
        elif action in ['change', 'update', 'modify']:
            if existing_idx is not None:
                items[existing_idx]['qty'] = float(quantity) if quantity else items[existing_idx].get('qty', 1)
                items[existing_idx]['unit'] = unit if unit else items[existing_idx].get('unit', '')
                message = f"✅ Updated {ingredient_name} to {quantity} {unit} in '{recipe.name}'"
            else:
                return {"success": False, "message": f"❌ {ingredient_name} not found in recipe"}
        
        else:
            return {"success": False, "message": "Unknown action"}
        
        # Save updated recipe
        recipe.items = json.dumps(items)
        db.commit()
        
        return {"success": True, "message": message}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Recipe edit execution error: {str(e)}")
        return {"success": False, "message": f"❌ Failed to edit recipe: {str(e)}"}


async def execute_add_inventory(data: Dict, db: Session) -> Dict:
    """Execute confirmed inventory addition"""
    try:
        # Check if item exists, update or create
        existing = db.query(InventoryItem).filter(
            InventoryItem.name.ilike(f"%{data['item_name']}%")
        ).first()
        
        if existing:
            existing.quantity += float(data['quantity'])
            # Update price if provided
            if data.get('price'):
                existing.price = float(data['price'])
            db.commit()
            message = f"✅ Updated {existing.name}: {existing.quantity} {existing.unit}"
        else:
            new_item = InventoryItem(
                name=data['item_name'],
                unit=data['unit'],
                quantity=float(data['quantity']),
                category=data.get('category', 'Other'),
                price=float(data.get('price', 0))
            )
            db.add(new_item)
            db.commit()
            message = f"✅ Added {data['quantity']} {data['unit']} of {data['item_name']}"
        
        return {"success": True, "message": message}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Inventory add error: {str(e)}")
        return {"success": False, "message": f"❌ Failed: {str(e)}"}


async def execute_update_inventory(data: Dict, db: Session) -> Dict:
    """Execute confirmed inventory update"""
    try:
        item = db.query(InventoryItem).filter(InventoryItem.id == data['item_id']).first()
        if not item:
            return {"success": False, "message": "Item not found"}
        
        item.quantity = float(data['quantity'])
        item.unit = data['unit']
        db.commit()
        
        return {
            "success": True,
            "message": f"✅ Updated {item.name} to {item.quantity} {item.unit}"
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"❌ Failed: {str(e)}"}


async def execute_delete_inventory(data: Dict, db: Session) -> Dict:
    """Execute confirmed inventory deletion"""
    try:
        item = db.query(InventoryItem).filter(InventoryItem.id == data['item_id']).first()
        if not item:
            return {"success": False, "message": "Item not found"}
        
        item_name = item.name
        db.delete(item)
        db.commit()
        
        return {"success": True, "message": f"✅ Removed {item_name} from inventory"}
        
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"❌ Failed: {str(e)}"}

