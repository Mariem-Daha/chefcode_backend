from fastapi import Header, HTTPException, status
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Simple API key authentication
# In production, use a more robust authentication system (JWT, OAuth2, etc.)
API_KEY = os.getenv("API_KEY")

# Ensure API key is configured
if not API_KEY:
    raise RuntimeError(
        "API_KEY environment variable is not set. "
        "Please create a .env file with API_KEY=your-secret-key"
    )

async def verify_api_key(x_api_key: Optional[str] = Header(None, description="API Key for authentication")):
    """
    Dependency to verify API key authentication.
    Clients must include X-API-Key header with valid API key.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required. Include X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return x_api_key

