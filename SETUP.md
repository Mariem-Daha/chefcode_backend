# Backend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

### 2. Generate API Key

**Option A: Use the generator script**
```bash
python generate_api_key.py
```

**Option B: Manual generation**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Configure Environment

Create a `.env` file in the Backend directory:

```env
# REQUIRED: API Authentication Key
API_KEY=your-generated-secure-key-here

# OPTIONAL: OpenAI API Key (for ChatGPT features)
OPENAI_API_KEY=your-openai-key

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

# Environment
ENVIRONMENT=development
```

**⚠️ Important:** The backend will NOT start if `API_KEY` is not set in the `.env` file.

### 4. Run the Server

**Development:**
```bash
python main.py
```

**Production:**
```bash
# Single worker
uvicorn main:app --host 0.0.0.0 --port 8000

# Multiple workers (recommended)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Authentication

All write operations (POST, PUT, DELETE) require authentication via the `X-API-Key` header.

**Example:**
```bash
curl -X POST http://localhost:8000/api/inventory \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"name":"Test Item","unit":"kg","quantity":5,"category":"Other","price":10}'
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | **Yes** | None | API authentication key (auto-fails if not set) |
| `OPENAI_API_KEY` | No | None | OpenAI API key for ChatGPT features |
| `ALLOWED_ORIGINS` | No | `http://localhost:5500,http://127.0.0.1:5500` | Comma-separated list of allowed CORS origins |
| `ENVIRONMENT` | No | `development` | Set to `production` to disable auto-reload |

## Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use strong API keys** - Use the generator or `secrets.token_urlsafe(32)`
3. **Restrict CORS origins** - Only allow your actual frontend URLs
4. **Use HTTPS in production** - Never use HTTP for sensitive data
5. **Rotate API keys** - Change them periodically
6. **Use environment-specific keys** - Different keys for dev, staging, prod

## Testing

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Test authenticated endpoint
curl -X POST http://localhost:8000/api/action \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"action":"add-inventory","data":{"name":"Test","unit":"kg","quantity":5}}'
```

## Troubleshooting

### "API_KEY environment variable is not set"
- Create a `.env` file in the Backend directory
- Add `API_KEY=your-secure-key`
- Restart the server

### "401 Unauthorized"
- Check that you're including the `X-API-Key` header
- Verify the API key matches the one in `.env`
- Check for typos in the key

### CORS errors
- Add your frontend URL to `ALLOWED_ORIGINS` in `.env`
- Restart the server after changing environment variables

## API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc


