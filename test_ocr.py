"""
Quick OCR Test Script
Tests if the OCR endpoint is working correctly
"""

import urllib.request
import urllib.error
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
OCR_HEALTH_URL = f"{BASE_URL}/api/ocr/health"
OCR_UPLOAD_URL = f"{BASE_URL}/api/ocr/upload"

def test_backend_running():
    """Test if backend is running"""
    print("[*] Testing if backend is running...")
    try:
        req = urllib.request.Request(f"{BASE_URL}/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print("[OK] Backend is running")
                return True
            else:
                print(f"[ERROR] Backend returned status {response.status}")
                return False
    except urllib.error.URLError:
        print("[ERROR] Backend is not running!")
        print("        Please start the backend with: python main.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_ocr_health():
    """Test OCR health endpoint"""
    print("\n[*] Testing OCR health endpoint...")
    try:
        req = urllib.request.Request(OCR_HEALTH_URL)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        print(f"    Status: {data.get('status')}")
        print(f"    Has credentials: {data.get('has_credentials')}")
        
        if data.get('status') == 'ready':
            print("[OK] OCR is configured and ready!")
            return True
        elif data.get('status') == 'not_configured':
            print("[WARNING] OCR is not configured (missing environment variables)")
            print("          This is OK! App works without OCR using Manual Input and AI Assistant")
            return False
        else:
            print(f"[WARNING] OCR status: {data.get('status')}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing OCR health: {e}")
        return False

def test_ocr_upload():
    """Test OCR upload endpoint with a sample file"""
    print("\n[*] Testing OCR upload endpoint...")
    
    # Check if we have a test invoice
    test_files = [
        "test_invoice.pdf",
        "test_invoice.jpg",
        "test_invoice.png",
        "../invoice_sample.pdf"
    ]
    
    test_file = None
    for file_path in test_files:
        if Path(file_path).exists():
            test_file = file_path
            break
    
    if not test_file:
        print("[INFO] No test invoice file found")
        print("       To test upload, place a test invoice as 'test_invoice.pdf' or 'test_invoice.jpg'")
        return False
    
    print(f"[INFO] Using test file: {test_file}")
    
    try:
        # Note: This is a simplified test. For full multipart/form-data upload,
        # you would need the 'requests' library or more complex urllib code.
        print("[INFO] Upload test requires 'requests' library")
        print("       Install with: pip install requests")
        print("       Or test manually at http://localhost:8000/docs")
        return None
            
    except Exception as e:
        print(f"[ERROR] Error testing OCR upload: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("OCR ENDPOINT TEST SUITE")
    print("="*60)
    
    # Test 1: Backend running
    if not test_backend_running():
        print("\n[ERROR] Tests stopped - backend is not running")
        return
    
    # Test 2: OCR health
    ocr_ready = test_ocr_health()
    
    # Test 3: OCR upload (only if configured)
    if ocr_ready:
        test_ocr_upload()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("[OK] Backend: Running")
    print(f"[{'OK' if ocr_ready else 'INFO'}] OCR: {'Configured' if ocr_ready else 'Not Configured (Optional)'}")
    print("\n[INFO] To enable OCR, see Backend/OCR_SETUP_GUIDE.md")
    print("="*60)

if __name__ == "__main__":
    main()

