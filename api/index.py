import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from the root
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Import the FastAPI app from main.py
    from main import app
    
    # Ensure app is properly configured for serverless
    print("✅ FastAPI app imported successfully for Vercel")
    
except Exception as e:
    print(f"❌ Error importing FastAPI app: {e}")
    # Create a minimal FastAPI app as fallback
    from fastapi import FastAPI
    app = FastAPI(title="Error - Sloka 4.0", description="Import error occurred")
    
    @app.get("/")
    def error_root():
        return {"error": "Application import failed", "message": str(e)}

# Vercel expects the app to be available directly
# The app variable is automatically used by Vercel's Python runtime
