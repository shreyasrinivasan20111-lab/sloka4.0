import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from the root
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Import the FastAPI app from main.py
    from main import app
    
    # Add static file routes specifically for Vercel
    from fastapi.responses import FileResponse, Response
    
    # Get the current API directory
    API_DIR = Path(__file__).parent
    STATIC_DIR = API_DIR / "static"
    
    # Root HTML endpoint for Vercel
    @app.get("/api/")
    async def serve_index_html():
        html_file = STATIC_DIR / "index.html"
        if html_file.exists():
            return FileResponse(str(html_file), media_type="text/html")
        return Response("HTML not found", status_code=404)
    
    # Static file endpoints for Vercel
    @app.get("/api/static/styles.css")
    async def serve_css():
        css_file = STATIC_DIR / "styles.css"
        if css_file.exists():
            return FileResponse(str(css_file), media_type="text/css")
        return Response("/* CSS not found */", media_type="text/css", status_code=404)
    
    @app.get("/api/static/app.js") 
    async def serve_js():
        js_file = STATIC_DIR / "app.js"
        if js_file.exists():
            return FileResponse(str(js_file), media_type="application/javascript")
        return Response("console.log('JS not found');", media_type="application/javascript", status_code=404)
    
    @app.get("/api/static/{filename}")
    async def serve_static_file(filename: str):
        static_file = STATIC_DIR / filename
        if static_file.exists() and static_file.is_file():
            # Determine media type
            if filename.endswith('.css'):
                media_type = "text/css"
            elif filename.endswith('.js'):
                media_type = "application/javascript"
            elif filename.endswith('.html'):
                media_type = "text/html"
            elif filename.endswith('.svg'):
                media_type = "image/svg+xml"
            elif filename.endswith('.ico'):
                media_type = "image/x-icon"
            elif filename.endswith(('.png', '.jpg', '.jpeg')):
                media_type = f"image/{filename.split('.')[-1]}"
            else:
                media_type = "text/plain"
            
            return FileResponse(str(static_file), media_type=media_type)
        
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Static file '{filename}' not found")
    
    print("✅ FastAPI app imported successfully for Vercel with static file handlers")
    
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
