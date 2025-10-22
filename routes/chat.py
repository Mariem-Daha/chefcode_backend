from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional
import json, os, openai
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    prompt: str
    language: Optional[str] = "en"  # Added: language support (en/it)

class ChatResponse(BaseModel):
    status: str
    message: Optional[str] = None
    parsed_data: Optional[dict] = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Multi-language system prompts
SYSTEM_PROMPTS = {
    "en": """You are ChefCode's AI Inventory Parser. Parse commands silently and return only JSON.

Extract: item_name, unit, quantity, unit_price, type, lot_number (optional), expiry_date (optional)

Type detection:
beef/chicken/pork/meat → meat
lettuce/tomato/onion/vegetable → vegetable
apple/banana/orange/fruit → fruit
milk/cheese/yogurt/dairy → dairy
water/juice/wine/soda/beverage → beverage
sugar/flour/pasta/rice/bread → grocery
soap/detergent/cleaner → cleaning

Lot number keywords: "lot", "batch", "lot number", "batch number", "LOT"
Expiry date keywords: "expires", "expiry", "best before", "use by", "exp date", "expiration"
Date formats: Parse dates flexibly (e.g., "Dec 25", "12/25/2024", "2024-12-25", "December 25 2024")

If price missing: {"status": "ask_price", "message": "Price?"}
If complete: {"status": "complete", "parsed_data": {"item_name": "...", "unit": "...", "quantity": ..., "unit_price": ..., "type": "...", "lot_number": "..." or null, "expiry_date": "YYYY-MM-DD" or null}}

Output ONLY valid JSON. No explanations.""",
    
    "it": """Sei l'AI parser di ChefCode. Analizza comandi in silenzio e restituisci solo JSON.

Estrai: item_name, unit, quantity, unit_price, type, lot_number (opzionale), expiry_date (opzionale)

Rilevamento tipo:
manzo/pollo/maiale/carne → meat
lattuga/pomodoro/cipolla/verdura → vegetable
mela/banana/arancia/frutta → fruit
latte/formaggio/yogurt/latticini → dairy
acqua/succo/vino/bevanda → beverage
zucchero/farina/pasta/riso/pane → grocery
sapone/detergente → cleaning

Parole chiave lotto: "lotto", "batch", "numero lotto", "lotto numero"
Parole chiave scadenza: "scadenza", "scade", "da consumarsi entro", "exp", "data scadenza"
Formati data: Analizza date flessibilmente (es. "25 dic", "25/12/2024", "2024-12-25", "25 dicembre 2024")

Se manca prezzo: {"status": "ask_price", "message": "Prezzo?"}
Se completo: {"status": "complete", "parsed_data": {"item_name": "...", "unit": "...", "quantity": ..., "unit_price": ..., "type": "...", "lot_number": "..." o null, "expiry_date": "YYYY-MM-DD" o null}}

Output SOLO JSON valido. Niente spiegazioni."""
}

# Added: Health check endpoint
@router.get("/chat/health")
async def chat_health():
    """Health check for ChatGPT integration"""
    return {
        "status": "available" if client else "unavailable",
        "message": "ChatGPT integration ready" if client else "OPENAI_API_KEY not set",
        "supported_languages": ["en", "it"],
        "default_language": "en"
    }

@router.post("/chatgpt-smart", response_model=ChatResponse)
async def parse_inventory_command(request: ChatRequest):
    if not client:
        # Mock response when API key is not set
        lang = request.language or "en"
        mock_message = {
            "en": "ChatGPT integration ready. Please set OPENAI_API_KEY environment variable to enable AI functionality.",
            "it": "Integrazione ChatGPT pronta. Imposta la variabile d'ambiente OPENAI_API_KEY per abilitare la funzionalità AI."
        }
        return ChatResponse(
            status="mock",
            message=mock_message.get(lang, mock_message["en"])
        )
    
    lang = request.language or "en"
    
    try:
        # Get language-specific system prompt
        system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["en"])
        
        # Run blocking OpenAI call in thread pool to avoid blocking event loop
        response = await run_in_threadpool(
            lambda: client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=0
            )
        )

        ai_response = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(ai_response)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from OpenAI: {ai_response}")
            error_msg = {
                "en": "Unable to parse AI response. Please try again.",
                "it": "Impossibile analizzare la risposta AI. Riprova."
            }
            raise HTTPException(status_code=500, detail=error_msg.get(lang, error_msg["en"]))

        # If missing price → ask user
        if parsed.get("status") == "ask_price":
            return ChatResponse(
                status="ask_price",
                message=parsed.get("message")
            )

        # If complete → save to inventory
        elif parsed.get("status") == "complete":
            data = parsed.get("parsed_data")
            success_msg = {
                "en": f"Item '{data.get('item_name')}' added to inventory.",
                "it": f"Articolo '{data.get('item_name')}' aggiunto all'inventario."
            }
            return ChatResponse(
                status="success",
                message=success_msg.get(lang, success_msg["en"]),
                parsed_data=data
            )

        else:
            error_msg = {
                "en": "Unexpected AI response format",
                "it": "Formato risposta AI inaspettato"
            }
            raise HTTPException(status_code=400, detail=error_msg.get(lang, error_msg["en"]))

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the detailed error internally but return generic message to user
        logger.error(f"ChatGPT error: {type(e).__name__} - {str(e)}")
        error_msg = {
            "en": "An error occurred while processing your request. Please try again.",
            "it": "Si è verificato un errore durante l'elaborazione della richiesta. Riprova."
        }
        raise HTTPException(status_code=500, detail=error_msg.get(lang, error_msg["en"]))
