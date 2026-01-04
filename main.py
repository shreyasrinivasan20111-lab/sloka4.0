from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, Response
from typing import List, Optional, Dict, Any
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import os
import signal
import sys
import atexit
import logging
import traceback
from pathlib import Path
from datetime import datetime, timedelta

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent

# Configure comprehensive logging - adapt to environment
log_handlers = [logging.StreamHandler(sys.stdout)]

# Only add file handler in local development (not in serverless environments like Vercel)
try:
    # Check if we can write to the file system (will fail in Vercel/serverless)
    test_file = BASE_DIR / 'test_write.tmp'
    test_file.touch()
    test_file.unlink()  # Clean up
    # If we get here, file system is writable - add file handler
    log_handlers.append(logging.FileHandler(BASE_DIR / 'app.log', mode='a', encoding='utf-8'))
    print("📝 File logging enabled (local environment)")
except (OSError, PermissionError):
    # Read-only file system (Vercel/serverless) - only console logging
    print("📝 Console-only logging (serverless environment)")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
    handlers=log_handlers
)

# Create logger for this module
logger = logging.getLogger(__name__)

# Set specific loggers for better debugging
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("fastapi").setLevel(logging.DEBUG)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)  # SQL queries
logging.getLogger("httpx").setLevel(logging.DEBUG)  # HTTP requests

import database
import crud
import auth
import blob_utils

load_dotenv()

# Environment-based configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# Set active configuration based on environment
# Use DATABASE_URL directly (common pattern for deployment platforms)
database_url = os.getenv("DATABASE_URL")
if not database_url:
    # Fallback to environment-specific URLs if DATABASE_URL is not set
    if ENVIRONMENT == "production":
        database_url = os.getenv("PROD_DATABASE_URL")
        print(f"🚀 Running in PRODUCTION mode")
    else:
        database_url = os.getenv("DEV_DATABASE_URL") 
        print(f"🔧 Running in DEVELOPMENT mode")
else:
    if ENVIRONMENT == "production":
        print(f"🚀 Running in PRODUCTION mode with DATABASE_URL")
    else:
        print(f"🔧 Running in DEVELOPMENT mode with DATABASE_URL")

# Set the DATABASE_URL environment variable
if database_url:
    os.environ["DATABASE_URL"] = database_url
else:
    print("⚠️  WARNING: No DATABASE_URL configured")

# Configure Blob Storage Token
blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")
if not blob_token:
    # Fallback to environment-specific tokens if BLOB_READ_WRITE_TOKEN is not set
    if ENVIRONMENT == "production":
        blob_token = os.getenv("PROD_BLOB_READ_WRITE_TOKEN")
    else:
        blob_token = os.getenv("DEV_BLOB_READ_WRITE_TOKEN")

# Set the BLOB_READ_WRITE_TOKEN environment variable
if blob_token:
    os.environ["BLOB_READ_WRITE_TOKEN"] = blob_token
else:
    print("⚠️  WARNING: No BLOB_READ_WRITE_TOKEN configured")

app = FastAPI(title="🕉️ Spiritual Course Management System", version="1.0.0")

# Comprehensive error handling middleware
@app.middleware("http")
async def error_logging_middleware(request: Request, call_next):
    start_time = datetime.now()
    
    try:
        # Log incoming request details
        logger.info(f"🔥 INCOMING REQUEST: {request.method} {request.url}")
        logger.debug(f"📋 Request Headers: {dict(request.headers)}")
        
        # Note: We can't log request body here as it would consume the stream
        # Request body logging will be handled in individual endpoints
        
        response = await call_next(request)
        
        # Log response details
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ RESPONSE: {request.method} {request.url} | Status: {response.status_code} | Time: {process_time:.4f}s")
        
        return response
        
    except Exception as e:
        # Log detailed error information
        process_time = (datetime.now() - start_time).total_seconds()
        error_id = f"ERR_{int(datetime.now().timestamp())}"
        
        logger.error(f"❌ CRITICAL ERROR [{error_id}]: {request.method} {request.url}")
        logger.error(f"🕐 Process Time: {process_time:.4f}s")
        logger.error(f"🎯 Error Type: {type(e).__name__}")
        logger.error(f"💬 Error Message: {str(e)}")
        logger.error(f"📊 Request Details:")
        logger.error(f"   - URL: {request.url}")
        logger.error(f"   - Method: {request.method}")
        logger.error(f"   - Headers: {dict(request.headers)}")
        logger.error(f"   - Client: {request.client}")
        logger.error(f"🔍 Full Stack Trace:")
        logger.error(traceback.format_exc())
        
        # Return user-friendly error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
                "error_id": error_id,
                "timestamp": datetime.now().isoformat()
            }
        )

# Mount static files with flexible path
static_path = BASE_DIR / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Security
security = HTTPBearer()

# Simple Pydantic models for request validation only
class StudentRegister(BaseModel):
    email: EmailStr
    password: str

class StudentLogin(BaseModel):
    email: str  # Changed from EmailStr to str for testing
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    instructor: Optional[str] = None
    duration: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    instructor: Optional[str] = None
    duration: Optional[str] = None

class CourseEnrollment(BaseModel):
    student_id: int
    course_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class SectionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: Optional[int] = 0

class SectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None

class DocumentCreate(BaseModel):
    title: str
    order_index: Optional[int] = 0

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("🚀 Starting application initialization...")
        logger.info(f"🌍 Environment: {ENVIRONMENT.upper()}")
        logger.info(f"📊 Database URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
        
        # Try to create tables with error handling
        try:
            database.create_tables()
            logger.info("✅ Database tables created successfully")
        except Exception as db_error:
            logger.error(f"⚠️  Database initialization warning: {type(db_error).__name__}: {str(db_error)}")
            logger.error("🔍 Database stack trace:")
            logger.error(traceback.format_exc())
            
            # Check if it's a bcrypt-related error
            if "bcrypt" in str(db_error).lower() or "password cannot be longer than 72 bytes" in str(db_error):
                logger.warning("🔐 Bcrypt compatibility issue detected - continuing without default admin creation")
                logger.warning("   You may need to create admin accounts manually")
            else:
                # For other database errors, still try to continue
                logger.warning("   Continuing startup - some features may not work properly")
        
        # Log environment details
        logger.info(f"🔐 Admin email configured: {bool(os.getenv('ADMIN_EMAIL'))}")
        logger.info(f"🗄️  Blob storage configured: {bool(os.getenv('BLOB_READ_WRITE_TOKEN'))}")
        logger.info(f"⏰ Token expire time: {auth.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        
        logger.info("✅ Application startup completed")
        
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR during startup: {type(e).__name__}: {str(e)}")
        logger.error(f"🔍 Stack trace:")
        logger.error(traceback.format_exc())
        
        # For critical errors, still raise to prevent broken deployment
        # but log more helpful information
        if "bcrypt" in str(e).lower():
            logger.error("🔐 This appears to be a bcrypt/password hashing compatibility issue")
            logger.error("   Common in serverless environments with different bcrypt versions")
        
        raise

@app.on_event("startup")
async def startup_logging_event():
    """Application startup logging event"""
    logger.info(f"📅 FastAPI server starting at: {datetime.now().isoformat()}")
    logger.info(f"📊 Session management enabled - active sessions will be tracked")
    logger.info(f"🔄 Graceful shutdown handlers registered")
    logger.info(f"🔍 Enhanced error logging system enabled with stack traces")
    
    # Check if file logging is available
    file_logging = any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
    if file_logging:
        logger.info(f"📝 Logging to both console and app.log file")
    else:
        logger.info(f"📝 Console-only logging (serverless environment)")
    
    logger.info(f"🎯 Request/Response middleware active for comprehensive debugging")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    try:
        logger.info(f"🛑 FastAPI server shutting down at: {datetime.now().isoformat()}")
        logger.info(f"📊 Active sessions before cleanup: {len(active_sessions)}")
        
        # Clear all active sessions
        active_sessions.clear()
        logger.info("✅ All active sessions cleared successfully")
        
    except Exception as e:
        logger.error(f"💥 ERROR during shutdown: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
    cleanup_sessions()

# Authentication dependencies
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = auth.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def get_current_student(current_user: dict = Depends(get_current_user)):
    if current_user["type"] != "student":
        raise HTTPException(status_code=403, detail="Not authorized as student")
    return current_user

def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    return current_user

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring and deployment verification"""
    try:
        # Basic health info
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": ENVIRONMENT,
            "version": "1.0.0"
        }
        
        # Try a simple database connection test
        try:
            # This is a minimal test - just checking if we can connect
            conn = database.get_db_connection()
            conn.close()
            health_status["database"] = "connected"
        except Exception as db_error:
            logger.warning(f"Health check database warning: {str(db_error)}")
            health_status["database"] = "warning"
            health_status["database_error"] = str(db_error)[:100]  # Truncate long errors
        
        # Check static files availability
        try:
            css_path = BASE_DIR / "static" / "styles.css"
            js_path = BASE_DIR / "static" / "app.js"
            html_path = BASE_DIR / "static" / "index.html"
            
            health_status["static_files"] = {
                "css": css_path.exists(),
                "js": js_path.exists(), 
                "html": html_path.exists(),
                "static_dir": (BASE_DIR / "static").exists()
            }
        except Exception as static_error:
            health_status["static_files"] = {"error": str(static_error)}
        
        # Check key environment variables
        health_status["config"] = {
            "database_configured": bool(os.getenv("DATABASE_URL")),
            "blob_storage_configured": bool(os.getenv("BLOB_READ_WRITE_TOKEN")),
            "admin_email_configured": bool(os.getenv("ADMIN_EMAIL"))
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# Static file serving
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        html_path = BASE_DIR / "static" / "index.html"
        if html_path.exists():
            return FileResponse(str(html_path), media_type="text/html")
        else:
            # Return a simple HTML if static file not found (for debugging)
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sloka 4.0 - Spiritual Course Management</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="/static/styles.css">
            </head>
            <body>
                <div class="container">
                    <h1>🕉️ Sloka 4.0</h1>
                    <p>Spiritual Course Management Platform</p>
                    <p>Loading...</p>
                </div>
                <script src="/static/app.js"></script>
            </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        return HTMLResponse("<h1>Service Temporarily Unavailable</h1>", status_code=503)

# Static CSS route
@app.get("/static/styles.css")
async def get_styles():
    try:
        css_path = BASE_DIR / "static" / "styles.css"
        if css_path.exists():
            return FileResponse(str(css_path), media_type="text/css")
        else:
            # Return basic fallback CSS
            return Response("""
            /* Fallback CSS for Sloka 4.0 */
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; line-height: 1.6;
            }
            .container { 
                max-width: 800px; margin: 0 auto; background: white; 
                padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .loading { text-align: center; color: #7f8c8d; }
            """, media_type="text/css")
    except Exception as e:
        logger.error(f"Error serving CSS: {e}")
        return Response("/* CSS Error */", media_type="text/css", status_code=500)

# Static JS route  
@app.get("/static/app.js")
async def get_app_js():
    try:
        js_path = BASE_DIR / "static" / "app.js"
        if js_path.exists():
            return FileResponse(str(js_path), media_type="application/javascript")
        else:
            # Return basic fallback JS
            return Response("""
            // Fallback JS for Sloka 4.0
            console.log('Sloka 4.0 - Spiritual Course Management Platform');
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Application loaded');
                // Basic functionality can be added here
            });
            """, media_type="application/javascript")
    except Exception as e:
        logger.error(f"Error serving JS: {e}")
        return Response("console.error('JS loading error');", media_type="application/javascript", status_code=500)

# General static file route (for any other static files)
@app.get("/static/{file_path:path}")
async def get_static_file(file_path: str):
    try:
        file_full_path = BASE_DIR / "static" / file_path
        
        # Security check - ensure we're still within static directory
        if not str(file_full_path).startswith(str(BASE_DIR / "static")):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if file_full_path.exists() and file_full_path.is_file():
            # Determine media type based on file extension
            media_type = "text/plain"  # default
            if file_path.endswith('.css'):
                media_type = "text/css"
            elif file_path.endswith('.js'):
                media_type = "application/javascript"
            elif file_path.endswith('.html'):
                media_type = "text/html"
            elif file_path.endswith(('.png', '.jpg', '.jpeg')):
                media_type = f"image/{file_path.split('.')[-1]}"
            elif file_path.endswith('.svg'):
                media_type = "image/svg+xml"
            elif file_path.endswith('.ico'):
                media_type = "image/x-icon"
            
            return FileResponse(str(file_full_path), media_type=media_type)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving static file {file_path}: {e}")
        raise HTTPException(status_code=500, detail="Error serving static file")

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    # Try to serve SVG favicon with proper content type
    favicon_path = BASE_DIR / "static" / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(str(favicon_path), media_type="image/svg+xml")
    else:
        # Return a simple response if no favicon exists
        raise HTTPException(status_code=404, detail="Favicon not found")

# PDF Proxy route for inline viewing
@app.get("/api/pdf-proxy")
async def pdf_proxy(url: str):
    """
    Proxy PDF files to serve them with inline Content-Disposition
    This helps prevent automatic downloads and enables inline viewing
    """
    try:
        logger.info(f"📄 PDF proxy request for URL: {url}")
        
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.debug(f"🌐 Fetching PDF from external URL: {url}")
            response = await client.get(url)
            response.raise_for_status()
            
            content_length = len(response.content)
            logger.info(f"✅ PDF fetched successfully - Size: {content_length} bytes")
            
            # Return PDF with inline disposition
            from fastapi.responses import Response
            return Response(
                content=response.content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": "inline",
                    "Content-Type": "application/pdf",
                    "Content-Length": str(content_length)
                }
            )
            
    except httpx.HTTPStatusError as e:
        error_id = f"PDF_HTTP_ERR_{int(datetime.now().timestamp())}"
        logger.error(f"🔥 PDF HTTP Error [{error_id}]: Status {e.response.status_code}")
        logger.error(f"📎 URL: {url}")
        logger.error(f"💬 Response: {e.response.text[:500]}")
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to fetch PDF - HTTP {e.response.status_code}. Error ID: {error_id}"
        )
        
    except httpx.TimeoutException:
        error_id = f"PDF_TIMEOUT_ERR_{int(datetime.now().timestamp())}"
        logger.error(f"⏰ PDF Timeout Error [{error_id}]: Request timeout for URL: {url}")
        raise HTTPException(
            status_code=408, 
            detail=f"PDF request timeout. Please try again. Error ID: {error_id}"
        )
        
    except httpx.RequestError as e:
        error_id = f"PDF_REQ_ERR_{int(datetime.now().timestamp())}"
        logger.error(f"🌐 PDF Request Error [{error_id}]: {type(e).__name__}: {str(e)}")
        logger.error(f"📎 URL: {url}")
        logger.error(f"🔍 Stack trace:")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=400, 
            detail=f"Network error while fetching PDF. Error ID: {error_id}"
        )
        
    except Exception as e:
        error_id = f"PDF_GEN_ERR_{int(datetime.now().timestamp())}"
        logger.error(f"💥 UNEXPECTED PDF Error [{error_id}]: {type(e).__name__}: {str(e)}")
        logger.error(f"📎 URL: {url}")
        logger.error(f"🔍 Stack trace:")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred while processing PDF. Error ID: {error_id}"
        )

# Authentication endpoints
@app.post("/api/auth/student/register")
def register_student(student: StudentRegister):
    # Check if student already exists
    existing_student = crud.get_student_by_email(student.email)
    if existing_student:
        raise HTTPException(status_code=400, detail="An account with this email already exists. Please try logging in instead.")
    
    # Create student
    new_student = crud.create_student(student.email, student.password)
    if not new_student:
        raise HTTPException(status_code=400, detail="Failed to create account. Please try again.")
    
    return {
        "id": new_student["id"],
        "email": new_student["email"],
        "created_at": new_student["created_at"],
        "is_active": new_student["is_active"]
    }

@app.post("/api/auth/student/login")
def login_student(student_login: StudentLogin):
    try:
        logger.info(f"🔐 Student login attempt for email: {student_login.email}")
        
        # Check if student exists
        logger.debug(f"🔍 Querying database for student: {student_login.email}")
        student = crud.get_student_by_email(student_login.email)
        if not student:
            logger.warning(f"❌ Student login failed - no account found for email: {student_login.email}")
            raise HTTPException(status_code=401, detail="No account found with this email address. Please check your email or register for a new account.")
        
        logger.debug(f"✅ Student found: ID={student.get('id')}, Active={student.get('is_active')}")
        
        # Check if account is active
        if not student.get("is_active", True):
            logger.warning(f"❌ Student login failed - account deactivated for email: {student_login.email}")
            raise HTTPException(status_code=401, detail="Your account has been deactivated. Please contact support for assistance.")
        
        # TEMPORARY FIX: Skip password verification to test if that's the hanging point
        logger.debug(f"🔐 Starting password verification for: {student_login.email}")
        try:
            password_valid = auth.verify_password(student_login.password, student["hashed_password"])
            logger.debug(f"🔐 Password verification completed: {password_valid}")
        except Exception as pwd_error:
            logger.error(f"💥 Password verification error: {type(pwd_error).__name__}: {str(pwd_error)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Password verification failed")
        
        if not password_valid:
            logger.warning(f"❌ Student login failed - incorrect password for email: {student_login.email}")
            raise HTTPException(status_code=401, detail="Incorrect password. Please check your password and try again.")
        
        logger.info(f"✅ Student authentication successful for email: {student_login.email}")
        
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": student["email"], "type": "student"}, expires_delta=access_token_expires
        )
        
        # Track active session
        session_id = f"student_{student['email']}_{datetime.now().timestamp()}"
        active_sessions.add(session_id)
        
        logger.info(f"🎫 Session created for student: {student_login.email} | Session ID: {session_id}")
        
        response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="strict"
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (these are expected errors)
        raise
    except Exception as e:
        # Log unexpected errors with full details
        error_id = f"STUDENT_LOGIN_ERR_{int(datetime.now().timestamp())}"
        logger.error(f"💥 UNEXPECTED ERROR in student login [{error_id}]: {type(e).__name__}: {str(e)}")
        logger.error(f"📧 Email: {student_login.email}")
        logger.error(f"🔍 Stack trace:")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred during login. Error ID: {error_id}"
        )

# Simple test endpoint to debug routing
@app.post("/api/test-login")
def test_login_endpoint(data: dict):
    logger.info("🧪 TEST LOGIN ENDPOINT CALLED!")
    logger.info(f"📦 Received data: {data}")
    return {"message": "Test endpoint working", "received": data}

@app.post("/api/auth/admin/login")
def login_admin(admin_login: AdminLogin):
    try:
        logger.info(f"🔐 Admin login attempt for email: {admin_login.email}")
        
        admin = crud.authenticate_admin(admin_login.email, admin_login.password)
        if not admin:
            # Check if it's an email issue or password issue
            admin_email = os.getenv("ADMIN_EMAIL")
            logger.debug(f"🔍 Admin email comparison: provided={admin_login.email}, expected={admin_email}")
            
            if admin_login.email != admin_email:
                logger.warning(f"❌ Admin login failed - invalid admin email: {admin_login.email}")
                raise HTTPException(status_code=401, detail="Invalid admin email address. Please check your credentials.")
            else:
                logger.warning(f"❌ Admin login failed - incorrect password for admin: {admin_login.email}")
                raise HTTPException(status_code=401, detail="Incorrect admin password. Please verify your password and try again.")
        
        logger.info(f"✅ Admin authentication successful for email: {admin_login.email}")
        
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": admin["email"], "type": "admin"}, expires_delta=access_token_expires
        )
        
        # Track active session
        session_id = f"admin_{admin['email']}_{datetime.now().timestamp()}"
        active_sessions.add(session_id)
        
        logger.info(f"🎫 Admin session created: {admin_login.email} | Session ID: {session_id}")
        
        response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="strict"
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (these are expected errors)
        raise
    except Exception as e:
        # Log unexpected errors with full details
        error_id = f"ADMIN_LOGIN_ERR_{int(datetime.now().timestamp())}"
        logger.error(f"💥 UNEXPECTED ERROR in admin login [{error_id}]: {type(e).__name__}: {str(e)}")
        logger.error(f"📧 Email: {admin_login.email}")
        logger.error(f"🔍 Stack trace:")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred during admin login. Error ID: {error_id}"
        )

@app.post("/api/auth/logout")
def logout(request: Request):
    """Logout endpoint for both students and admins"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        active_sessions.remove(session_id)
    
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("session_id")
    response.delete_cookie("access_token", httponly=True)
    
    return response

@app.get("/api/auth/sessions/clear")
def clear_all_sessions():
    """Clear all active sessions - for server restart/admin purposes"""
    session_count = len(active_sessions)
    cleanup_sessions()
    return {"message": f"Cleared {session_count} active sessions"}

# Student endpoints
@app.get("/api/student/courses")
def get_my_courses(current_user: dict = Depends(get_current_student)):
    student = crud.get_student_by_email(current_user["email"])
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud.get_student_courses(student["id"])

@app.get("/api/student/profile")
def get_student_profile(current_user: dict = Depends(get_current_student)):
    student = crud.get_student_by_email(current_user["email"])
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get student with courses
    courses = crud.get_student_courses(student["id"])
    return {
        "id": student["id"],
        "email": student["email"],
        "created_at": student["created_at"],
        "is_active": student["is_active"],
        "courses": courses
    }

# Admin endpoints
@app.get("/api/admin/students")
def get_all_students(
    current_user: dict = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100
):
    return crud.get_students(skip=skip, limit=limit)

@app.get("/api/admin/courses")
def get_all_courses_admin(
    current_user: dict = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100
):
    return crud.get_courses(skip=skip, limit=limit)

@app.post("/api/admin/courses")
def create_course(
    course: CourseCreate,
    current_user: dict = Depends(get_current_admin)
):
    try:
        logger.info(f"📚 Creating new course: {course.title}")
        logger.debug(f"👤 Course creation requested by admin: {current_user.get('email')}")
        logger.debug(f"📋 Course details: title='{course.title}', instructor='{course.instructor}', duration='{course.duration}'")
        
        new_course = crud.create_course(
            title=course.title,
            description=course.description,
            content=course.content,
            instructor=course.instructor,
            duration=course.duration
        )
        
        if not new_course:
            logger.error(f"❌ Failed to create course - CRUD returned None for: {course.title}")
            raise HTTPException(status_code=400, detail="Failed to create course")
            
        logger.info(f"✅ Course created successfully: ID={new_course.get('id')}, Title='{new_course.get('title')}'")
        return new_course
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        error_id = f"COURSE_CREATE_ERR_{int(datetime.now().timestamp())}"
        logger.error(f"💥 UNEXPECTED ERROR creating course [{error_id}]: {type(e).__name__}: {str(e)}")
        logger.error(f"📚 Course title: {course.title}")
        logger.error(f"👤 Admin: {current_user.get('email')}")
        logger.error(f"🔍 Stack trace:")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while creating the course. Error ID: {error_id}"
        )

@app.put("/api/admin/courses/{course_id}")
def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user: dict = Depends(get_current_admin)
):
    updated_course = crud.update_course(
        course_id=course_id,
        title=course_update.title,
        description=course_update.description,
        content=course_update.content,
        instructor=course_update.instructor,
        duration=course_update.duration
    )
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated_course

@app.delete("/api/admin/courses/{course_id}")
def delete_course(
    course_id: int,
    current_user: dict = Depends(get_current_admin)
):
    success = crud.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}

@app.post("/api/admin/enroll")
def enroll_student(
    enrollment: CourseEnrollment,
    current_user: dict = Depends(get_current_admin)
):
    success = crud.enroll_student_in_course(enrollment.student_id, enrollment.course_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to enroll student")
    return {"message": "Student enrolled successfully"}

@app.delete("/api/admin/enroll")
def remove_student_enrollment(
    enrollment: CourseEnrollment,
    current_user: dict = Depends(get_current_admin)
):
    success = crud.remove_student_from_course(enrollment.student_id, enrollment.course_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove student from course")
    return {"message": "Student removed from course successfully"}

@app.get("/api/admin/courses/{course_id}/students")
def get_course_students(
    course_id: int,
    current_user: dict = Depends(get_current_admin)
):
    return crud.get_course_students(course_id)

# Section management endpoints
@app.post("/api/admin/courses/{course_id}/sections")
def create_section(
    course_id: int,
    section: SectionCreate,
    current_user: dict = Depends(get_current_admin)
):
    new_section = crud.create_course_section(
        course_id=course_id,
        title=section.title,
        description=section.description,
        order_index=section.order_index
    )
    if not new_section:
        raise HTTPException(status_code=400, detail="Failed to create section")
    return new_section

@app.get("/api/admin/courses/{course_id}/sections")
def get_course_sections(
    course_id: int,
    current_user: dict = Depends(get_current_admin)
):
    return crud.get_course_sections(course_id)

@app.put("/api/admin/sections/{section_id}")
def update_section(
    section_id: int,
    section_update: SectionUpdate,
    current_user: dict = Depends(get_current_admin)
):
    updated_section = crud.update_course_section(
        section_id=section_id,
        title=section_update.title,
        description=section_update.description,
        order_index=section_update.order_index
    )
    if not updated_section:
        raise HTTPException(status_code=404, detail="Section not found")
    return updated_section

@app.delete("/api/admin/sections/{section_id}")
def delete_section(
    section_id: int,
    current_user: dict = Depends(get_current_admin)
):
    success = crud.delete_course_section(section_id)
    if not success:
        raise HTTPException(status_code=404, detail="Section not found")
    return {"message": "Section deleted successfully"}

@app.post("/api/admin/sections/{section_id}/documents")
async def add_section_document(
    section_id: int,
    title: str = Form(...),
    file: UploadFile = File(...),
    order_index: int = Form(0),
    current_user: dict = Depends(get_current_admin)
):
    try:
        logger.info(f"📁 File upload started: {file.filename} for section {section_id}")
        logger.debug(f"👤 Upload requested by admin: {current_user.get('email')}")
        logger.debug(f"📋 Upload details: title='{title}', order_index={order_index}")
        logger.debug(f"🗂️  File details: name={file.filename}, content_type={file.content_type}, size={file.size}")
        
        # Validate file type
        if not (blob_utils.is_allowed_document_file(file.filename) or blob_utils.is_allowed_audio_file(file.filename)):
            logger.warning(f"❌ File upload rejected - invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Upload file to blob storage
        logger.debug(f"📖 Reading file content for: {file.filename}")
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"✅ File content read successfully - Size: {file_size} bytes")
        
        content_type = blob_utils.get_content_type(file.filename)
        
        # Determine file type for categorization
        file_type = "audio" if blob_utils.is_allowed_audio_file(file.filename) else "document"
        folder = f"section_{file_type}s"
        
        logger.info(f"☁️  Uploading to blob storage: folder={folder}, type={file_type}")
        
        file_url = await blob_utils.upload_file_to_blob(file_content, f"{folder}/{file.filename}", content_type)
        
        if not file_url:
            logger.error(f"❌ Blob storage upload failed for file: {file.filename}")
            raise HTTPException(status_code=500, detail="Failed to upload file")
            
        logger.info(f"✅ File uploaded to blob storage successfully: {file_url[:100]}...")
        
        # Add document record
        logger.debug(f"💾 Adding document record to database")
        document = crud.add_section_document(
            section_id=section_id,
            title=title,
            file_url=file_url,
            file_type=file_type,
            order_index=order_index
        )
        
        if not document:
            logger.error(f"❌ Failed to create document record in database for: {file.filename}")
            raise HTTPException(status_code=400, detail="Failed to add document")
        
        logger.info(f"✅ Document upload completed successfully: ID={document.get('id')}, Title='{title}'")
        return document
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        error_id = f"FILE_UPLOAD_ERR_{int(datetime.now().timestamp())}"
        logger.error(f"💥 UNEXPECTED ERROR during file upload [{error_id}]: {type(e).__name__}: {str(e)}")
        logger.error(f"📁 File: {file.filename if file else 'None'}")
        logger.error(f"📊 Section ID: {section_id}")
        logger.error(f"👤 Admin: {current_user.get('email')}")
        logger.error(f"🔍 Stack trace:")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during file upload. Error ID: {error_id}"
        )

@app.delete("/api/admin/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_admin)
):
    success = crud.delete_section_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

# Public endpoints (no auth required)
@app.get("/api/courses")
def get_courses(skip: int = 0, limit: int = 100):
    return crud.get_courses(skip=skip, limit=limit)

@app.get("/api/courses/{course_id}")
def get_course(course_id: int):
    course = crud.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# Session store for tracking active sessions
active_sessions = set()

def cleanup_sessions():
    """Clear all active sessions"""
    active_sessions.clear()
    print(f"{datetime.now().isoformat()}: All active sessions cleared")

# Register cleanup function for graceful shutdown
atexit.register(cleanup_sessions)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n{datetime.now().isoformat()}: Received shutdown signal {signum}")
    cleanup_sessions()
    sys.exit(0)

# Register signal handlers only in non-serverless environments
# Serverless environments like Vercel handle process lifecycle differently
try:
    # Check if we're in a serverless environment
    is_serverless = os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME') or os.getenv('FUNCTIONS_WORKER_RUNTIME')
    
    if not is_serverless:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        print("🔄 Signal handlers registered for graceful shutdown")
    else:
        print("☁️  Serverless environment detected - skipping signal handlers")
        
except Exception as e:
    print(f"⚠️  Warning: Could not register signal handlers: {e}")

# For Vercel deployment, the app instance is used directly
# For local development, we can still run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
