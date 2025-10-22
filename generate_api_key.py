#!/usr/bin/env python3
"""
Generate a secure API key for ChefCode backend
"""
import secrets

def generate_api_key(length=32):
    """Generate a secure random API key"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    api_key = generate_api_key()
    print("=" * 60)
    print("Generated Secure API Key:")
    print("=" * 60)
    print(f"\n{api_key}\n")
    print("=" * 60)
    print("\nAdd this to your .env file:")
    print(f"API_KEY={api_key}")
    print("\nAnd configure your frontend to use the same key.")
    print("=" * 60)


