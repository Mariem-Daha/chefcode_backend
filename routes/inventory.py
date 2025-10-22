from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import InventoryItem
from schemas import InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse
from typing import List
from auth import verify_api_key

router = APIRouter()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/inventory", response_model=List[InventoryItemResponse])
async def get_inventory(db: Session = Depends(get_db)):
    """Get all inventory items"""
    items = db.query(InventoryItem).all()
    return items

@router.post("/inventory", response_model=InventoryItemResponse)
async def add_inventory_item(
    item: InventoryItemCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Add a new inventory item"""
    # Check if item with same name already exists
    existing_item = db.query(InventoryItem).filter(InventoryItem.name == item.name).first()
    
    if existing_item:
        # Update quantity if same price, otherwise create new entry
        if abs(existing_item.price - item.price) < 0.01:  # Same price
            existing_item.quantity += item.quantity
            db.commit()
            db.refresh(existing_item)
            return existing_item
    
    # Create new item
    db_item = InventoryItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/inventory/{item_id}")
async def update_inventory_item(
    item_id: int, 
    item: InventoryItemUpdate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update an inventory item (partial update supported)"""
    db_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Only update fields that were explicitly set (exclude_unset=True)
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/inventory/delete")
async def delete_inventory_item_by_id(
    request: dict,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete an inventory item by ID from request body"""
    item_id = request.get("id")
    if not item_id:
        raise HTTPException(status_code=400, detail="Item ID is required")
    
    db_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

@router.delete("/inventory/{item_id}")
async def delete_inventory_item(
    item_id: int, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete an inventory item"""
    db_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}