# Sloka 4.0 - Spiritual Course Management Platform

A modern FastAPI-based spiritual course management system with direct PostgreSQL integration and advanced file management capabilities.

## 🚀 Quick Start

### Development Mode (Recommended)
```bash
# Development start with dev database
./dev_start.sh
```

### Production Mode
```bash
# Start with production database and settings
./prod_start.sh
```

### Legacy Scripts
```bash
# Development mode startup
./dev_start.sh

# Production mode startup  
./prod_start.sh

# Stop the server  
./stop_server.sh
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (we use Vercel Neon)
- Node.js (for file watching in dev mode)
- Vercel Blob storage account

## 🛠️ Server Management Scripts

### `dev_start.sh`
- **Purpose**: Development environment startup
- **Features**:
  - Sets `ENVIRONMENT=development`
  - Uses development database and blob storage
  - Fast startup with minimal overhead
  - Development mode indicators

### `prod_start.sh`
- **Purpose**: Production environment startup
- **Features**:
  - Sets `ENVIRONMENT=production`
  - Uses production database and blob storage
  - Production-ready configuration
  - Production mode indicators

### `stop_server.sh`
- **Purpose**: Graceful server shutdown
- **Features**:
  - Multi-signal termination (SIGTERM → SIGKILL)
  - Process cleanup and verification
  - Quiet mode support (`--quiet` flag)
  - Safe to run multiple times

## 🌍 Environment Configuration

The system supports dual environments with automatic switching:

### Features
- **Active Session Tracking**: All login sessions are tracked server-side
- **Graceful Shutdown**: Sessions are properly cleaned up on server restart
- **Security**: Session cookies are httpOnly with proper SameSite settings
- **Automatic Cleanup**: Sessions are cleared on server termination

### API Endpoints
- `POST /api/auth/student/login` - Student login with session tracking
- `POST /api/auth/admin/login` - Admin login with session tracking  
- `POST /api/auth/logout` - Logout with session cleanup
- `GET /api/auth/sessions/clear` - Clear all active sessions (admin)

## 🔐 Authentication System

### JWT-Based Authentication
- **Students**: Course access and profile management
- **Admins**: Full course and section management
- **Session Tracking**: Server-side session validation
- **Secure Cookies**: httpOnly, SameSite protection

### Security Features
- Password hashing with proper salt
- Duplicate user prevention
- Session invalidation on logout/restart
- Comprehensive error handling

## 🗂️ Project Structure & File Roles

### 📁 **Root Directory Files**

#### **Core Application Files**
- **`main.py`** - Main FastAPI application with all API endpoints, session management, and server configuration
- **`database.py`** - Direct PostgreSQL connection management, table creation, and database utilities
- **`crud.py`** - Database operations using raw SQL queries (Create, Read, Update, Delete functions)
- **`auth.py`** - JWT token authentication, password hashing, and user verification
- **`blob_utils.py`** - Vercel Blob storage integration for file uploads and management

#### **Configuration Files**
- **`.env`** - Environment variables (database URL, blob token, JWT secrets, admin credentials)
- **`.env.example`** - Environment variables template for deployment
- **`requirements.txt`** - Python dependencies list for pip installation
- **`.gitignore`** - Git ignore rules for Python projects and sensitive files

#### **Deployment Files**
- **`vercel.json`** - Vercel deployment configuration
- **`runtime.txt`** - Python runtime version for Vercel
- **`deploy_vercel.sh`** - Automated Vercel deployment script
- **`test_api.py`** - API testing script for deployed applications

#### **Server Management Scripts**
- **`dev_start.sh`** - ⚡ **RECOMMENDED** - Development server startup  
- **`prod_start.sh`** - 🚀 Production server startup
- **`stop_server.sh`** - Graceful server shutdown

### 📁 **api/** - Vercel Serverless Functions

#### **Serverless Functions**
- **`index.py`** - Main serverless function handler for Vercel deployment

#### **Documentation**
- **`README.md`** - This comprehensive guide and documentation

### 📁 **static/** - Frontend Assets

#### **Frontend Files**
- **`index.html`** - Complete single-page application UI with all modals and components
- **`app.js`** - Full JavaScript application logic (authentication, course management, media preview)
- **`styles.css`** - Complete CSS styling with spiritual theme and responsive design

### 📁 **.venv/** - Python Virtual Environment
- Contains all installed Python packages and dependencies
- Automatically managed by Python virtual environment system

## 🔄 **File Dependencies Map**

```
main.py (Entry Point)
├── database.py (DB connection)
├── crud.py (DB operations)  
├── auth.py (Authentication)
├── blob_utils.py (File uploads)
├── .env (Configuration)
└── static/
    ├── index.html (Frontend UI)
    ├── app.js (Frontend logic)
    └── styles.css (Styling)

Server Scripts (Independent)
├── dev_start.sh → main.py (Development)
├── prod_start.sh → main.py (Production)
└── stop_server.sh (Process management)
```

## 📋 **File Usage Guide**

### **For Daily Development**
```bash
./dev_start.sh      # Start development server (dev database)
./stop_server.sh    # Stop server when done
```

### **For Production Deployment**
```bash
./prod_start.sh     # Start with production database
./stop_server.sh    # Stop server when done
```

### **Core Application Flow**
1. **`main.py`** → Loads configuration from **`.env`**
2. **`database.py`** → Creates tables and connections
3. **`auth.py`** → Handles user authentication 
4. **`crud.py`** → Manages all database operations
5. **`blob_utils.py`** → Handles file uploads to Vercel
6. **`static/`** → Serves the complete frontend application

## 🧹 **Cleaned Up Files**

The following unused files have been removed:
- ~~`start.py`~~ - Redundant startup script  
- ~~`init_db.py`~~ - Database seeding (handled in database.py)
- ~~`test_setup.py`~~ - Testing utilities (not needed)
- ~~`test_course_material.txt`~~ - Sample file (not needed)  
- ~~`DEVELOPMENT.md`~~ - Development docs (merged into README)
- ~~`vercel.json`~~ - Vercel deployment config (not used)
- ~~`Icon?`~~ - macOS icon file (cleanup)
- ~~`__pycache__/`~~ - Python cache directory (cleanup)

## 📚 Course Management

### Section-Based Architecture
- **Courses** contain multiple **Sections**
- **Sections** contain multiple **Documents** (PDF, audio, video, images, text)
- **Hierarchical ordering** with proper admin controls
- **Media preview system** with inline viewing

### Features
- ✅ File upload with Vercel Blob storage
- ✅ Media preview modals (PDF, audio, video, images, text)
- ✅ Admin-only section management
- ✅ Student course enrollment
- ✅ Hierarchical content organization
- Assign courses to students
- Remove students from courses
- View all students enrolled in a specific course

## Technology Stack

- **Backend**: Python 3.11, FastAPI
- **Frontend**: HTML5, jQuery 3.7.1, CSS3
- **Database**: PostgreSQL (Vercel Postgres for production)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Deployment**: Vercel

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Sloka4.0
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env` to your environment or modify it with your settings
   - Update database URL for your PostgreSQL instance
   - Change the JWT secret key for security
   - Set admin credentials

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - The admin login credentials are set in your `.env` file (default: admin@spiritual.com / admin123)

### Production Deployment on Vercel

The project is now fully configured for Vercel deployment with proper serverless functions.

#### 🚀 **Quick Deploy**
```bash
# Install Vercel CLI globally
npm install -g vercel

# Deploy with one command
./deploy_vercel.sh
```

#### 📋 **Manual Deployment Steps**

1. **Prerequisites**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Login to Vercel
   vercel login
   ```

2. **Project Setup**
   - Fork this repository to your GitHub account
   - Connect your GitHub account to Vercel dashboard
   - Import this project in Vercel

3. **Environment Variables**
   In your Vercel project dashboard, add these environment variables:
   ```
   ENVIRONMENT=production
   PROD_DATABASE_URL=your_neon_postgres_connection_string
   PROD_BLOB_READ_WRITE_TOKEN=your_vercel_blob_token
   SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ADMIN_EMAIL=your_admin_email
   ADMIN_PASSWORD=your_secure_admin_password
   ```

4. **Deploy**
   ```bash
   # For production deployment
   vercel --prod
   
   # For preview deployment
   vercel
   ```

5. **Test Deployment**
   ```bash
   # Test your deployed API
   python test_api.py https://your-app.vercel.app
   ```

#### 🏗️ **Vercel Configuration Files**

The project includes these Vercel-specific files:
- **`vercel.json`** - Vercel deployment configuration
- **`api/index.py`** - Serverless function handler
- **`runtime.txt`** - Python version specification
- **`.env.example`** - Environment variables template
- **`deploy_vercel.sh`** - Automated deployment script
- **`test_api.py`** - API testing script

#### 🔧 **Architecture for Vercel**

```
Vercel Deployment Structure:
├── api/
│   └── index.py          # Serverless function entry point
├── static/               # Static files served directly
├── main.py              # FastAPI application (imported by api/index.py)
├── vercel.json          # Deployment configuration
└── runtime.txt          # Python version
```

## 🌐 Environment Configuration

### 🔧 Development vs Production Settings

The application now supports automatic environment switching:

#### **Development Environment** (Default)
- **Database**: Neon development database  
- **Blob Storage**: Development blob storage
- **Usage**: Local development and testing

#### **Production Environment**
- **Database**: Neon production database
- **Blob Storage**: Production blob storage  
- **Usage**: Live deployment

### 📝 Environment Variables

The `.env` file contains both development and production settings:

```bash
# Environment selector (development/production)
ENVIRONMENT=development

# Development Settings
DEV_DATABASE_URL=postgresql://neondb_owner:npg_bRvLyfq71BiD@ep-morning-tooth-ahhhy1hk-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
DEV_BLOB_READ_WRITE_TOKEN=vercel_blob_rw_dXp49gv0ENnc1tWY_RFHMZ6xthYpYbbtlbANtcd0xnlixxs

# Production Settings  
PROD_DATABASE_URL=postgresql://neondb_owner:npg_5mOaAbJiYR4V@ep-blue-dawn-a4hwwpcl-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
PROD_BLOB_READ_WRITE_TOKEN=vercel_blob_rw_hcFLqNYxHdxAPEBk_nN6BlZIvpEQlFL4fiCVZbMIpgqL7zP
```

### 🚀 Environment Scripts

- **`./dev_start.sh`** - Starts in **DEVELOPMENT** mode
- **`./prod_start.sh`** - Starts in **PRODUCTION** mode

### 🔄 Switching Environments

**Method 1: Use Different Scripts**
```bash
./dev_start.sh      # Development mode
./prod_start.sh     # Production mode
```

**Method 2: Set Environment Variable**
```bash
export ENVIRONMENT=production
./dev_start.sh      # Now runs in production mode
```

**Method 3: Edit .env File**
```bash
# Change ENVIRONMENT=development to ENVIRONMENT=production in .env
```

## API Endpoints

### Authentication
- `POST /api/auth/student/register` - Student registration
- `POST /api/auth/student/login` - Student login
- `POST /api/auth/admin/login` - Admin login

### Student Endpoints
- `GET /api/student/courses` - Get enrolled courses
- `GET /api/student/profile` - Get student profile

### Admin Endpoints
- `GET /api/admin/students` - Get all students
- `GET /api/admin/courses` - Get all courses (admin view)
- `POST /api/admin/courses` - Create new course
- `PUT /api/admin/courses/{id}` - Update course
- `DELETE /api/admin/courses/{id}` - Delete course
- `POST /api/admin/enroll` - Enroll student in course
- `DELETE /api/admin/enroll` - Remove student from course
- `GET /api/admin/courses/{id}/students` - Get course students

### Public Endpoints
- `GET /api/courses` - Get all active courses
- `GET /api/courses/{id}` - Get specific course details

## UI/UX Design Philosophy

The application embraces a spiritual aesthetic with:

- **Purple Gradient Theme**: Primary colors using spiritual purple tones
- **Om Symbol**: Used throughout as a spiritual identifier
- **Smooth Animations**: Gentle transitions and hover effects
- **Clean Typography**: Inter font for modern readability
- **Card-Based Layout**: Organized content in visually appealing cards
- **Responsive Design**: Works beautifully on desktop, tablet, and mobile

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Role-Based Access**: Separate permissions for students and admins
- **Input Validation**: Pydantic models for API validation
- **CORS Security**: Configurable CORS settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For support or questions, please open an issue on GitHub or contact the development team.

---

**May your learning journey be filled with wisdom and growth** 🕉️

## 📊 **Final Project Structure**

```
Sloka4.0/                          # Spiritual Course Management Platform
├── 🏗️  CORE APPLICATION
│   ├── main.py                    # FastAPI app + API endpoints + session mgmt
│   ├── database.py                # PostgreSQL connections + table creation  
│   ├── crud.py                    # Raw SQL database operations
│   ├── auth.py                    # JWT authentication + password hashing
│   └── blob_utils.py              # Vercel Blob file storage integration
│
├── �  SERVERLESS API
│   └── api/
│       └── index.py               # Vercel serverless function handler
│
├── �🎨  FRONTEND
│   └── static/
│       ├── index.html             # Complete SPA with modals + components
│       ├── app.js                 # Full JS logic + media preview
│       └── styles.css             # Spiritual theme + responsive design
│
├── ⚙️   CONFIGURATION  
│   ├── .env                       # Environment variables + secrets
│   ├── .env.example               # Environment template for deployment
│   ├── requirements.txt           # Python dependencies
│   ├── runtime.txt                # Python version for Vercel
│   ├── vercel.json                # Vercel deployment config
│   └── .gitignore                 # Git ignore rules
│
├── 🚀  SERVER SCRIPTS
│   ├── dev_start.sh               # ⭐ DEV startup (recommended)
│   ├── prod_start.sh              # 🚀 PROD startup  
│   ├── stop_server.sh             # Graceful shutdown
│   └── deploy_vercel.sh           # Automated Vercel deployment
│
├── 🧪  TESTING
│   └── test_api.py                # API testing script
│
├── 📚  DOCUMENTATION
│   └── README.md                  # This comprehensive guide
│
└── 🔧  PYTHON ENVIRONMENT
    └── .venv/                     # Virtual environment + dependencies
```

## 🎯 **Total Files: 21** (Clean & Purposeful)
- **5** Core Python files (main app logic)
- **1** Serverless function (Vercel deployment)
- **3** Frontend files (complete UI)  
- **6** Configuration files (including deployment configs)
- **4** Server management scripts (including deployment script)
- **1** Testing script
- **1** Documentation file

**Added Vercel deployment support** for seamless production deployment.

---

**Your Sloka 4.0 platform is now production-ready with Vercel deployment! 🚀🕉️**
