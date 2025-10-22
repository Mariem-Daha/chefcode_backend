from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, Date
from sqlalchemy.sql import func
from database import Base
from datetime import datetime, date

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    unit = Column(String, default="pz")
    quantity = Column(Float, default=0.0)
    category = Column(String, default="Other")
    price = Column(Float, default=0.0)
    # HACCP Traceability fields
    lot_number = Column(String, nullable=True)  # Batch/Lot number for traceability
    expiry_date = Column(Date, nullable=True)  # Expiry date for HACCP compliance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    items = Column(Text)  # JSON string of recipe items
    instructions = Column(Text, default="")
    yield_data = Column(Text, nullable=True)  # JSON string of yield info: {"qty": 10, "unit": "pz"}
    # Web recipe metadata
    source_url = Column(String, nullable=True)  # Original recipe URL (e.g., TheMealDB)
    image_url = Column(String, nullable=True)  # Recipe thumbnail/image URL
    cuisine = Column(String, nullable=True)  # Cuisine type (Italian, Chinese, etc.)
    ingredients_raw = Column(Text, nullable=True)  # JSON: Original ingredients from web
    ingredients_mapped = Column(Text, nullable=True)  # JSON: AI-mapped ingredients to inventory
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    assigned_to = Column(String, default="")
    status = Column(String, default="todo")  # todo, inprogress, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SyncData(Base):
    __tablename__ = "sync_data"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String, nullable=False)  # 'full_sync', 'inventory', 'recipes', 'tasks'
    data_content = Column(Text)  # JSON string of synced data
    synced_at = Column(DateTime(timezone=True), server_default=func.now())