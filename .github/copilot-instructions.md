<!-- ChefCode FastAPI Backend Project Instructions -->

This is a FastAPI backend for the ChefCode application that provides inventory management, recipe management, task tracking, and ChatGPT integration.

## Project Structure
- FastAPI backend with SQLite database
- Endpoints for inventory, recipes, tasks, and AI chat
- Models matching the frontend data structures
- CORS enabled for frontend communication

## Key Features
- Inventory management (add, get, update items)
- Recipe management (create, store, retrieve recipes)
- Production task tracking
- ChatGPT integration for AI assistance
- Data synchronization with frontend
- Health check endpoints

## Development
- Use uvicorn for development server
- SQLite database for local development
- Ready for PostgreSQL migration in production
- CORS configured for frontend integration

## API Endpoints
- GET /api/data - Complete data sync endpoint
- POST /api/sync-data - Sync data from frontend
- POST /api/action - Handle frontend actions
- POST /api/chatgpt-smart - AI chat integration
- Individual CRUD endpoints for inventory, recipes, tasks

## Backend Connection
- Runs on port 8000 (FastAPI default)
- Compatible with existing ChefCode frontend
- Drop-in replacement for Node.js backend
- Maintains same data formats and endpoint structure