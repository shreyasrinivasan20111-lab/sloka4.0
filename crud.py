from database import get_db
import auth
from typing import List, Dict, Optional

# Student operations
def create_student(email: str, password: str) -> Optional[Dict]:
    """Create a new student"""
    hashed_password = auth.get_password_hash(password)
    
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO students (email, hashed_password) VALUES (%s, %s) RETURNING id, email, created_at, is_active",
                (email, hashed_password)
            )
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return {
                    "id": result[0],
                    "email": result[1],
                    "created_at": result[2],
                    "is_active": result[3]
                }
        except Exception:
            conn.rollback()
            return None
    return None

def get_student_by_email(email: str) -> Optional[Dict]:
    """Get student by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, hashed_password, created_at, is_active FROM students WHERE email = %s",
            (email,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                "id": result[0],
                "email": result[1],
                "hashed_password": result[2],
                "created_at": result[3],
                "is_active": result[4]
            }
    return None

def authenticate_student(email: str, password: str) -> Optional[Dict]:
    """Authenticate student credentials"""
    student = get_student_by_email(email)
    if not student:
        return None
    if not student["is_active"]:
        return None
    if not auth.verify_password(password, student["hashed_password"]):
        return None
    return student

def get_students(skip: int = 0, limit: int = 100) -> List[Dict]:
    """Get all students"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, created_at, is_active FROM students ORDER BY created_at DESC OFFSET %s LIMIT %s",
            (skip, limit)
        )
        results = cursor.fetchall()
        
        return [
            {
                "id": result[0],
                "email": result[1],
                "created_at": result[2],
                "is_active": result[3]
            }
            for result in results
        ]

# Admin operations
def create_admin(email: str, password: str) -> Optional[Dict]:
    """Create a new admin"""
    hashed_password = auth.get_password_hash(password)
    
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO admins (email, hashed_password) VALUES (%s, %s) RETURNING id, email, created_at, is_active",
                (email, hashed_password)
            )
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return {
                    "id": result[0],
                    "email": result[1],
                    "created_at": result[2],
                    "is_active": result[3]
                }
        except Exception:
            conn.rollback()
            return None
    return None

def get_admin_by_email(email: str) -> Optional[Dict]:
    """Get admin by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, hashed_password, created_at, is_active FROM admins WHERE email = %s",
            (email,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                "id": result[0],
                "email": result[1],
                "hashed_password": result[2],
                "created_at": result[3],
                "is_active": result[4]
            }
    return None

def authenticate_admin(email: str, password: str) -> Optional[Dict]:
    """Authenticate admin credentials"""
    admin = get_admin_by_email(email)
    if not admin:
        return None
    if not admin["is_active"]:
        return None
    if not auth.verify_password(password, admin["hashed_password"]):
        return None
    return admin

# Course operations
def create_course(title: str, description: str = None, content: str = None, instructor: str = None, duration: str = None) -> Optional[Dict]:
    """Create a new course"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO courses (title, description, content, instructor, duration) VALUES (%s, %s, %s, %s, %s) RETURNING id, title, description, content, instructor, duration, created_at, is_active",
                (title, description, content, instructor, duration)
            )
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return {
                    "id": result[0],
                    "title": result[1],
                    "description": result[2],
                    "content": result[3],
                    "instructor": result[4],
                    "duration": result[5],
                    "created_at": result[6],
                    "is_active": result[7],
                    "sections": []
                }
        except Exception:
            conn.rollback()
            return None
    return None

def get_courses(skip: int = 0, limit: int = 100) -> List[Dict]:
    """Get all courses"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, content, instructor, duration, created_at, is_active FROM courses WHERE is_active = TRUE ORDER BY created_at DESC OFFSET %s LIMIT %s",
            (skip, limit)
        )
        results = cursor.fetchall()
        
        courses = []
        for result in results:
            course = {
                "id": result[0],
                "title": result[1],
                "description": result[2],
                "content": result[3],
                "instructor": result[4],
                "duration": result[5],
                "created_at": result[6],
                "is_active": result[7],
                "sections": get_course_sections(result[0])
            }
            courses.append(course)
        
        return courses

def get_course_by_id(course_id: int) -> Optional[Dict]:
    """Get course by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, content, instructor, duration, created_at, is_active FROM courses WHERE id = %s",
            (course_id,)
        )
        result = cursor.fetchone()
        
        if result:
            course = {
                "id": result[0],
                "title": result[1],
                "description": result[2],
                "content": result[3],
                "instructor": result[4],
                "duration": result[5],
                "created_at": result[6],
                "is_active": result[7],
                "sections": get_course_sections(result[0])
            }
            return course
    return None

def update_course(course_id: int, title: str = None, description: str = None, content: str = None, instructor: str = None, duration: str = None) -> Optional[Dict]:
    """Update course"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            # Build dynamic update query
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = %s")
                params.append(title)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if content is not None:
                updates.append("content = %s")
                params.append(content)
            if instructor is not None:
                updates.append("instructor = %s")
                params.append(instructor)
            if duration is not None:
                updates.append("duration = %s")
                params.append(duration)
            
            if not updates:
                return get_course_by_id(course_id)
            
            params.append(course_id)
            query = f"UPDATE courses SET {', '.join(updates)} WHERE id = %s RETURNING id, title, description, content, instructor, duration, created_at, is_active"
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                course = {
                    "id": result[0],
                    "title": result[1],
                    "description": result[2],
                    "content": result[3],
                    "instructor": result[4],
                    "duration": result[5],
                    "created_at": result[6],
                    "is_active": result[7],
                    "sections": get_course_sections(result[0])
                }
                return course
        except Exception:
            conn.rollback()
            return None
    return None

def delete_course(course_id: int) -> bool:
    """Delete course (soft delete)"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE courses SET is_active = FALSE WHERE id = %s",
                (course_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            return False

# Enrollment operations
def enroll_student_in_course(student_id: int, course_id: int) -> bool:
    """Enroll student in course"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO student_course (student_id, course_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (student_id, course_id)
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

def remove_student_from_course(student_id: int, course_id: int) -> bool:
    """Remove student from course"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM student_course WHERE student_id = %s AND course_id = %s",
                (student_id, course_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            return False

def get_student_courses(student_id: int) -> List[Dict]:
    """Get courses enrolled by student"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.title, c.description, c.content, c.instructor, c.duration, c.created_at, c.is_active 
            FROM courses c
            JOIN student_course sc ON c.id = sc.course_id
            WHERE sc.student_id = %s AND c.is_active = TRUE
            ORDER BY c.created_at DESC
        """, (student_id,))
        results = cursor.fetchall()
        
        courses = []
        for result in results:
            course = {
                "id": result[0],
                "title": result[1],
                "description": result[2],
                "content": result[3],
                "instructor": result[4],
                "duration": result[5],
                "created_at": result[6],
                "is_active": result[7],
                "sections": get_course_sections(result[0])
            }
            courses.append(course)
        
        return courses

def get_course_students(course_id: int) -> List[Dict]:
    """Get students enrolled in course"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.email, s.created_at, s.is_active
            FROM students s
            JOIN student_course sc ON s.id = sc.student_id
            WHERE sc.course_id = %s AND s.is_active = TRUE
            ORDER BY s.created_at DESC
        """, (course_id,))
        results = cursor.fetchall()
        
        return [
            {
                "id": result[0],
                "email": result[1],
                "created_at": result[2],
                "is_active": result[3]
            }
            for result in results
        ]

# Section operations
def create_course_section(course_id: int, title: str, description: str = None, order_index: int = 0) -> Optional[Dict]:
    """Create a new course section"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO course_sections (course_id, title, description, order_index) VALUES (%s, %s, %s, %s) RETURNING id, course_id, title, description, order_index, created_at",
                (course_id, title, description, order_index)
            )
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return {
                    "id": result[0],
                    "course_id": result[1],
                    "title": result[2],
                    "description": result[3],
                    "order_index": result[4],
                    "created_at": result[5],
                    "documents": []
                }
        except Exception:
            conn.rollback()
            return None
    return None

def get_course_sections(course_id: int) -> List[Dict]:
    """Get all sections for a course with their documents"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, course_id, title, description, order_index, created_at
            FROM course_sections 
            WHERE course_id = %s 
            ORDER BY order_index ASC, created_at ASC
        """, (course_id,))
        sections = cursor.fetchall()
        
        result = []
        for section in sections:
            section_data = {
                "id": section[0],
                "course_id": section[1],
                "title": section[2],
                "description": section[3],
                "order_index": section[4],
                "created_at": section[5],
                "documents": get_section_documents(section[0])
            }
            result.append(section_data)
        
        return result

def update_course_section(section_id: int, title: str = None, description: str = None, order_index: int = None) -> Optional[Dict]:
    """Update a course section"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = %s")
                params.append(title)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if order_index is not None:
                updates.append("order_index = %s")
                params.append(order_index)
            
            if not updates:
                return None
            
            params.append(section_id)
            query = f"UPDATE course_sections SET {', '.join(updates)} WHERE id = %s RETURNING id, course_id, title, description, order_index, created_at"
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return {
                    "id": result[0],
                    "course_id": result[1],
                    "title": result[2],
                    "description": result[3],
                    "order_index": result[4],
                    "created_at": result[5],
                    "documents": get_section_documents(result[0])
                }
        except Exception:
            conn.rollback()
            return None
    return None

def delete_course_section(section_id: int) -> bool:
    """Delete a course section and all its documents"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM course_sections WHERE id = %s", (section_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            return False

# Document operations
def add_section_document(section_id: int, title: str, file_url: str, file_type: str, order_index: int = 0) -> Optional[Dict]:
    """Add a document to a course section"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO section_documents (section_id, title, file_url, file_type, order_index) VALUES (%s, %s, %s, %s, %s) RETURNING id, section_id, title, file_url, file_type, order_index, created_at",
                (section_id, title, file_url, file_type, order_index)
            )
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return {
                    "id": result[0],
                    "section_id": result[1],
                    "title": result[2],
                    "file_url": result[3],
                    "file_type": result[4],
                    "order_index": result[5],
                    "created_at": result[6]
                }
        except Exception:
            conn.rollback()
            return None
    return None

def get_section_documents(section_id: int) -> List[Dict]:
    """Get all documents for a section"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, section_id, title, file_url, file_type, order_index, created_at
            FROM section_documents 
            WHERE section_id = %s 
            ORDER BY order_index ASC, created_at ASC
        """, (section_id,))
        results = cursor.fetchall()
        
        return [
            {
                "id": result[0],
                "section_id": result[1],
                "title": result[2],
                "file_url": result[3],
                "file_type": result[4],
                "order_index": result[5],
                "created_at": result[6]
            }
            for result in results
        ]

def delete_section_document(document_id: int) -> bool:
    """Delete a section document"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM section_documents WHERE id = %s", (document_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            return False

def get_course_with_sections(course_id: int) -> Optional[Dict]:
    """Get course with all its sections and documents"""
    course = get_course_by_id(course_id)
    if course:
        course["sections"] = get_course_sections(course_id)
    return course
