"""
Quick diagnostic script to test Web Recipes setup
Run this to verify everything is configured correctly
"""

import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("[*] Checking dependencies...")
    
    missing = []
    
    try:
        import httpx
        print("   [OK] httpx is installed")
    except ImportError:
        print("   [FAIL] httpx is NOT installed")
        missing.append("httpx")
    
    try:
        import openai
        print("   [OK] openai is installed")
    except ImportError:
        print("   [FAIL] openai is NOT installed")
        missing.append("openai")
    
    try:
        import fastapi
        print("   [OK] fastapi is installed")
    except ImportError:
        print("   [FAIL] fastapi is NOT installed")
        missing.append("fastapi")
    
    if missing:
        print(f"\n[WARNING] Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n[*] Checking environment configuration...")
    
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("   [WARNING] .env file not found")
        print("   Create Backend/.env with: OPENAI_API_KEY=your-key-here")
        return False
    
    print("   [OK] .env file exists")
    
    # Check if OPENAI_API_KEY is set
    with open(env_path, 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content and 'sk-' in content:
            print("   [OK] OPENAI_API_KEY appears to be set")
            return True
        else:
            print("   [WARNING] OPENAI_API_KEY not found or invalid in .env")
            return False


def check_routes_file():
    """Check if web_recipes.py exists"""
    print("\n[*] Checking route files...")
    
    routes_path = Path(__file__).parent / "routes" / "web_recipes.py"
    
    if not routes_path.exists():
        print("   [FAIL] routes/web_recipes.py not found!")
        return False
    
    print("   [OK] routes/web_recipes.py exists")
    return True


def check_services():
    """Check if service files exist"""
    print("\n[*] Checking service files...")
    
    services_dir = Path(__file__).parent / "services"
    
    if not services_dir.exists():
        print("   [FAIL] services/ directory not found!")
        return False
    
    ai_service = services_dir / "ai_service.py"
    mealdb_service = services_dir / "mealdb_service.py"
    
    if not ai_service.exists():
        print("   [FAIL] services/ai_service.py not found!")
        return False
    print("   [OK] services/ai_service.py exists")
    
    if not mealdb_service.exists():
        print("   [FAIL] services/mealdb_service.py not found!")
        return False
    print("   [OK] services/mealdb_service.py exists")
    
    return True


def test_imports():
    """Try to import the modules"""
    print("\n[*] Testing module imports...")
    
    try:
        from routes import web_recipes
        print("   [OK] routes.web_recipes imports successfully")
        
        # Check if router exists
        if hasattr(web_recipes, 'router'):
            print("   [OK] web_recipes.router exists")
            
            # Count routes
            route_count = len(web_recipes.router.routes)
            print(f"   [OK] Found {route_count} routes in web_recipes router")
        else:
            print("   [FAIL] web_recipes.router not found!")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Failed to import routes.web_recipes: {str(e)}")
        return False
    
    try:
        from services.ai_service import get_ai_service
        print("   [OK] services.ai_service imports successfully")
    except Exception as e:
        print(f"   [WARNING] Failed to import ai_service: {str(e)}")
        print("      (This is OK if OPENAI_API_KEY is not set)")
    
    try:
        from services.mealdb_service import get_mealdb_service
        print("   [OK] services.mealdb_service imports successfully")
    except Exception as e:
        print(f"   [FAIL] Failed to import mealdb_service: {str(e)}")
        return False
    
    return True


def test_database():
    """Check database schema"""
    print("\n[*] Checking database schema...")
    
    db_path = Path(__file__).parent / "chefcode.db"
    
    if not db_path.exists():
        print("   [INFO] Database not found (will be created on first run)")
        return True
    
    print("   [OK] Database exists")
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(recipes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['source_url', 'image_url', 'cuisine', 'ingredients_raw', 'ingredients_mapped']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"   [WARNING] Missing columns: {', '.join(missing_columns)}")
            print("   Run migration: python migrate_add_web_recipe_fields.py")
            return False
        
        print("   [OK] All required columns exist")
        conn.close()
        return True
        
    except Exception as e:
        print(f"   [WARNING] Could not check database: {str(e)}")
        return True


def main():
    print("=" * 70)
    print("WEB RECIPES FEATURE - DIAGNOSTIC CHECK")
    print("=" * 70)
    print()
    
    checks = [
        check_dependencies(),
        check_env_file(),
        check_routes_file(),
        check_services(),
        test_imports(),
        test_database()
    ]
    
    print("\n" + "=" * 70)
    
    if all(checks):
        print("[SUCCESS] ALL CHECKS PASSED!")
        print()
        print("Next steps:")
        print("1. Restart the backend: python main.py")
        print("2. Test the endpoint: http://localhost:8000/api/web-recipes/test")
        print("3. Try the frontend search feature")
    else:
        print("[FAILED] SOME CHECKS FAILED")
        print()
        print("Please fix the issues above and run this script again.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()

