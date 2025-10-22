# ChefCode FastAPI Backend

A comprehensive FastAPI backend for the ChefCode inventory management system that perfectly matches the frontend data structures and API expectations.

## Features

- **Inventory Management**: Add, update, and track inventory items with automatic quantity merging
- **Recipe Management**: Create and manage recipes with ingredient lists
- **Task Tracking**: Production task management with status tracking
- **Data Synchronization**: Full data sync endpoints matching original backend format
- **ChatGPT Integration**: AI assistant for inventory and recipe management (requires OpenAI API key)
- **Health Checks**: System health monitoring endpoints

## Project Structure

```
Backend/
├── main.py              # FastAPI application entry point
├── database.py          # SQLite database configuration
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response models
├── requirements.txt     # Python dependencies
├── routes/
│   ├── __init__.py
│   ├── inventory.py     # Inventory management endpoints
│   ├── recipes.py       # Recipe management endpoints
│   ├── tasks.py         # Task management endpoints
│   ├── chat.py          # ChatGPT integration endpoints
│   ├── data.py          # Data retrieval endpoints
│   └── actions.py       # Action handling endpoints
└── .github/
    └── copilot-instructions.md
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   uvicorn main:app --reload
   ```

3. **Access the API**:
   - API Server: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Core Endpoints (Matching Frontend Expectations)

- `GET /api/data` - Get all data (inventory, recipes, tasks) in frontend format
- `POST /api/sync-data` - Sync all data from frontend
- `POST /api/action` - Handle frontend actions (add-inventory, save-recipe, add-task)
- `POST /api/chatgpt-smart` - ChatGPT AI integration

### Individual Resource Endpoints

#### Inventory
- `GET /api/inventory` - Get all inventory items
- `POST /api/inventory` - Add new inventory item
- `PUT /api/inventory/{id}` - Update inventory item
- `DELETE /api/inventory/{id}` - Delete inventory item

#### Recipes
- `GET /api/recipes` - Get all recipes
- `POST /api/recipes` - Create new recipe
- `GET /api/recipes/{id}` - Get specific recipe
- `PUT /api/recipes/{id}` - Update recipe
- `DELETE /api/recipes/{id}` - Delete recipe

#### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `PUT /api/tasks/{id}/status` - Update task status
- `DELETE /api/tasks/{id}` - Delete task

## Database

Uses SQLite for development with the following tables:
- `inventory_items` - Inventory management
- `recipes` - Recipe storage with JSON ingredient lists
- `tasks` - Production task tracking
- `sync_data` - Data synchronization history

## Frontend Connection

### Connecting Your ChefCode Frontend

1. **Update API Base URL**: Change the frontend API calls from `localhost:3000` to `localhost:8000`
2. **Port Configuration**: FastAPI runs on port 8000 (vs Node.js on 3000)
3. **Endpoint Compatibility**: All original endpoints are preserved with same data formats

### Testing the Connection

1. Start the FastAPI server: `uvicorn main:app --reload`
2. Open your frontend application
3. Update the API base URL in your frontend code:
   ```javascript
   // Change from:
   const api = new ChefCodeAPI('http://localhost:3000');
   // To:
   const api = new ChefCodeAPI('http://localhost:8000');
   ```
4. Test functionality:
   - Add inventory items
   - Create recipes
   - Manage tasks
   - Use ChatGPT features (with API key)

## Configuration

### Environment Variables

Create a `.env` file for configuration:

```env
# Optional: OpenAI API key for ChatGPT integration
OPENAI_API_KEY=your_openai_api_key_here

# Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///./chefcode.db
```

### ChatGPT Integration

To enable ChatGPT features:
1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Set the `OPENAI_API_KEY` environment variable
3. Restart the server

## Production Deployment

### Database Migration to PostgreSQL

1. **Install PostgreSQL dependencies**:
   ```bash
   pip install psycopg2-binary
   ```

2. **Update database.py**:
   ```python
   # Change from SQLite
   SQLITE_DATABASE_URL = "sqlite:///./chefcode.db"
   
   # To PostgreSQL
   DATABASE_URL = "postgresql://username:password@localhost/chefcode"
   ```

3. **Update connection args**:
   ```python
   engine = create_engine(DATABASE_URL)  # Remove SQLite-specific args
   ```

### Production Checklist

- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Set CORS origins to your frontend domain
- [ ] Enable HTTPS
- [ ] Set up logging and monitoring
- [ ] Configure backup strategies

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Database Management
```bash
# Reset database (development only)
rm chefcode.db

# Server will recreate tables on next startup
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Port Conflicts**: Change port with `--port` flag
3. **Database Issues**: Delete `chefcode.db` file to reset
4. **CORS Errors**: Check frontend URL in CORS configuration

### Debug Mode

Run with detailed logging:
```bash
uvicorn main:app --reload --log-level debug
```

## Support

The backend is designed to be a drop-in replacement for the original Node.js backend, maintaining full compatibility with the existing ChefCode frontend.