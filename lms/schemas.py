"""
Pydantic schemas for API validation and serialization
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# ==================== User Schemas ====================

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = Field(default='mahasiswa', pattern='^(admin|dosen|mahasiswa)$')
    bio: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    bio: Optional[str]
    phone: Optional[str]
    is_active: bool
    date_joined: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ==================== Course Schemas ====================

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=200)
    description: str
    category: str = Field(..., max_length=100)
    level: str = Field(default='beginner', pattern='^(beginner|intermediate|advanced)$')


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = Field(None, pattern='^(beginner|intermediate|advanced)$')
    is_active: Optional[bool] = None


class CourseOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    category: str
    level: str
    instructor_id: int
    instructor_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    enrollment_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class CourseDetailOut(CourseOut):
    lessons: List['LessonOut'] = []
    assignments: List['AssignmentOut'] = []


# ==================== Enrollment Schemas ====================

class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime
    is_active: bool
    progress: float
    
    class Config:
        from_attributes = True


# ==================== Lesson Schemas ====================

class LessonCreate(BaseModel):
    course_id: int
    title: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=200)
    description: str
    content: str
    video_url: Optional[str] = None
    duration_minutes: int = Field(default=0, ge=0)
    order: int = Field(default=0, ge=0)
    is_published: bool = False


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None


class LessonOut(BaseModel):
    id: int
    course_id: int
    title: str
    slug: str
    description: str
    content: str
    video_url: Optional[str]
    duration_minutes: int
    order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Assignment Schemas ====================

class AssignmentCreate(BaseModel):
    course_id: int
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    instructions: str
    max_score: int = Field(default=100, ge=0, le=100)
    due_date: datetime


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    instructions: Optional[str] = None
    max_score: Optional[int] = Field(None, ge=0, le=100)
    due_date: Optional[datetime] = None


class AssignmentOut(BaseModel):
    id: int
    course_id: int
    title: str
    description: str
    instructions: str
    max_score: int
    due_date: datetime
    created_at: datetime
    is_overdue: bool = False
    
    class Config:
        from_attributes = True


# ==================== Submission Schemas ====================

class SubmissionCreate(BaseModel):
    assignment_id: int
    content: str


class SubmissionUpdate(BaseModel):
    content: Optional[str] = None


class SubmissionGrade(BaseModel):
    score: float = Field(..., ge=0, le=100)
    feedback: Optional[str] = None


class SubmissionOut(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    content: str
    submitted_at: datetime
    updated_at: datetime
    score: Optional[float]
    feedback: Optional[str]
    graded_at: Optional[datetime]
    graded_by_id: Optional[int]
    is_late: bool = False
    is_graded: bool = False
    
    class Config:
        from_attributes = True


# ==================== Generic Responses ====================

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List


# Forward references
CourseDetailOut.model_rebuild()
