from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
from datetime import date

# Request/Response models for API

class InventoryItemCreate(BaseModel):
    name: str
    unit: str = "pz"
    quantity: float = 0.0
    category: str = "Other"
    price: float = 0.0
    lot_number: Optional[str] = None
    expiry_date: Optional[date] = None
    
    @field_validator('expiry_date')
    @classmethod
    def expiry_date_cannot_be_past(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v

class InventoryItemResponse(BaseModel):
    id: int
    name: str
    unit: str
    quantity: float
    category: str
    price: float
    lot_number: Optional[str] = None
    expiry_date: Optional[date] = None
    
    class Config:
        from_attributes = True

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

class TaskCreate(BaseModel):
    recipe: str
    quantity: int = 1
    assigned_to: Optional[str] = ""
    status: str = "todo"

class TaskResponse(BaseModel):
    id: int
    recipe: str
    quantity: int
    assigned_to: str
    status: str
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    choices: List[Dict[str, Any]]

class ActionRequest(BaseModel):
    action: str
    data: Dict[Any, Any]

class SyncDataRequest(BaseModel):
    inventory: Optional[List[Dict[str, Any]]] = []
    recipes: Optional[Dict[str, Dict[str, Any]]] = {}
    tasks: Optional[List[Dict[str, Any]]] = []

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    category: Optional[str] = None
    price: Optional[float] = None
    lot_number: Optional[str] = None
    expiry_date: Optional[date] = None
    
    @field_validator('expiry_date')
    @classmethod
    def expiry_date_cannot_be_past(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v