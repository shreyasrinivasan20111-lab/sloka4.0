import psycopg
import os
from dotenv import load_dotenv
from contextlib import contextmanager
from passlib.context import CryptContext

load_dotenv()

# Database connection parameters
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shreyasrinivasan@localhost/spiritual_courses")

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = None
    try:
        conn = psycopg.connect(DATABASE_URL)
        yield conn
    finally:
        if conn:
            conn.close()

def create_tables():
    """Create all necessary tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Create courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                content TEXT,
                instructor VARCHAR(255),
                duration VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Create course sections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_sections (
                id SERIAL PRIMARY KEY,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create section documents table  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS section_documents (
                id SERIAL PRIMARY KEY,
                section_id INTEGER REFERENCES course_sections(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                file_url VARCHAR(512) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create admins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Create student_course junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_course (
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                PRIMARY KEY (student_id, course_id)
            )
        """)
        
        conn.commit()
        
        # Remove old columns and add new sections approach
        cursor.execute("""
            DO $$ 
            BEGIN 
                -- Remove old file columns if they exist
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='courses' AND column_name='file_url') THEN
                    ALTER TABLE courses DROP COLUMN IF EXISTS file_url;
                END IF;
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='courses' AND column_name='audio_url') THEN
                    ALTER TABLE courses DROP COLUMN IF EXISTS audio_url;
                END IF;
                
                -- Add content column if it doesn't exist
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='courses' AND column_name='content') THEN
                    ALTER TABLE courses ADD COLUMN content TEXT;
                END IF;
            END $$;
        """)
        
        conn.commit()
        
        # Create default admin account if none exists
        cursor.execute("SELECT COUNT(*) FROM admins")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash("admin123")
            
            cursor.execute("""
                INSERT INTO admins (email, hashed_password, is_active) 
                VALUES (%s, %s, %s)
            """, ("admin@spiritual.com", hashed_password, True))
            conn.commit()
            print("✓ Default admin account created: admin@spiritual.com / admin123")
        
        print("✓ Database tables created successfully")
