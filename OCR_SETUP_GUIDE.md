# OCR Setup Guide for ChefCode

## ✅ OCR Integration Complete!

The OCR functionality has been successfully integrated into the ChefCode backend.

---

## 📦 Installation Steps

### 1. Install Required Dependencies

Navigate to the `Backend` folder and install the new packages:

```bash
cd Backend
pip install -r requirements.txt
```

This will install:
- `google-cloud-documentai` - Google Document AI for OCR
- `google-api-core` - Google API core libraries
- `google-generativeai` - Gemini AI for intelligent extraction
- `pillow` - Image processing library

---

## 🔑 Environment Configuration

### 2. Set Up Environment Variables

Create a `.env` file in the `Backend` folder with your API keys:

```env
# Google Cloud Document AI Configuration
PROJECT_ID=your_google_cloud_project_id
LOCATION=us  # or eu, asia-pacific
PROCESSOR_ID=your_document_ai_processor_id
GOOGLE_APPLICATION_CREDENTIALS=Backend/google-service-account.json

# Google Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Add Google Service Account JSON

If you have a Google Cloud service account JSON file:
- Place it at: `Backend/google-service-account.json`
- Or update the `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`

**Alternative:** You can paste the entire JSON content directly into the `GOOGLE_APPLICATION_CREDENTIALS` environment variable (useful for cloud deployments).

---

## 🚀 Available Endpoints

### OCR Upload Endpoint
**POST** `/api/ocr/upload`

Upload an invoice image/PDF for processing.

**Supported formats:** `.pdf`, `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`

**Response:**
```json
{
  "success": true,
  "data": {
    "supplier": {
      "name": "...",
      "address": "...",
      "phone": "...",
      "email": "...",
      "tax_id": "..."
    },
    "customer": {...},
    "invoice_details": {
      "invoice_number": "FT 123/2024",
      "invoice_date": "2025-04-09",
      "due_date": "2025-05-09"
    },
    "line_items": [
      {
        "item_code": "53747",
        "description": "POLLO PETTO GR 600",
        "type": "carne",
        "quantity": 1,
        "unit": "KG",
        "unit_price": 7.20,
        "total_price": 7.20
      }
    ],
    "financial_summary": {
      "subtotal": 32.64,
      "tax_amount": 7.18,
      "total_amount": 39.82,
      "currency": "EUR"
    }
  }
}
```

### Health Check Endpoint
**GET** `/api/ocr/health`

Check if OCR service is configured and ready.

**Response:**
```json
{
  "status": "ready",
  "has_credentials": true,
  "project_id": "my-project...",
  "location": "us",
  "processor_id": "abc123..."
}
```

---

## 🧪 Testing the OCR

### Option 1: Using the API Documentation

1. Start the backend:
   ```bash
   cd Backend
   python main.py
   ```

2. Open http://localhost:8000/docs

3. Navigate to **OCR** section

4. Try the `/api/ocr/health` endpoint first to verify configuration

5. Use `/api/ocr/upload` to upload an invoice

### Option 2: Using cURL

```bash
# Check health
curl http://localhost:8000/api/ocr/health

# Upload invoice
curl -X POST "http://localhost:8000/api/ocr/upload" \
  -F "file=@path/to/your/invoice.pdf"
```

### Option 3: From the Frontend

The frontend already has OCR UI components. They should now work automatically with the backend!

---

## 🎯 Features

✅ **Multi-format support:** PDF, JPG, PNG, TIFF  
✅ **Google Document AI:** High-accuracy OCR text extraction  
✅ **Gemini AI:** Intelligent data interpretation  
✅ **Automatic validation:** Quantity calculations verified  
✅ **Multi-language:** Supports Italian, English, and more  
✅ **Structured output:** JSON format with all invoice details  
✅ **Error handling:** Graceful fallbacks and detailed error messages  

---

## 🛠️ Troubleshooting

### "Missing environment variables" error
- Make sure you created a `.env` file in the `Backend` folder
- Verify all required variables are set: `PROJECT_ID`, `LOCATION`, `PROCESSOR_ID`, `GEMINI_API_KEY`

### "OCR service not configured" error
- Check that your Google Cloud credentials are valid
- Ensure the service account has Document AI permissions
- Verify the processor ID is correct

### Import errors
- Run `pip install -r requirements.txt` again
- Make sure you're in the Backend folder with the virtual environment activated

### "Processor not found" error
- Verify your `PROJECT_ID`, `LOCATION`, and `PROCESSOR_ID` are correct
- Check that the Document AI processor is enabled in your Google Cloud project

---

## 📝 Notes

- The OCR processor is initialized as a singleton for better performance
- Uploaded files are automatically cleaned up after processing
- Processing includes automatic quantity validation and correction
- The service supports both image analysis and text extraction for maximum accuracy

---

## 🔗 Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Add your API keys to `.env`
3. Place your Google service account JSON file
4. Start the backend: `python main.py`
5. Test with `/api/ocr/health`
6. Upload an invoice via `/api/ocr/upload`

Your OCR is ready to go! 🎉

