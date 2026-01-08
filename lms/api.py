"""
Django Ninja API endpoints for Simple LMS
"""

from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count, Prefetch
from django.core.cache import cache
from django.utils import timezone
from typing import List

from .models import Course, Lesson, Assignment, Submission, Enrollment, UserRole
from .schemas import (
    UserCreate, UserUpdate, UserOut, UserLogin, TokenResponse,
    CourseCreate, CourseUpdate, CourseOut, CourseDetailOut,
    LessonCreate, LessonUpdate, LessonOut,
    AssignmentCreate, AssignmentUpdate, AssignmentOut,
    SubmissionCreate, SubmissionUpdate, SubmissionGrade, SubmissionOut,
    EnrollmentCreate, EnrollmentOut,
    MessageResponse, ErrorResponse
)
from .auth import JWTAuth, create_jwt_token, require_role

User = get_user_model()

# Initialize API
api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="REST API for Learning Management System with JWT Authentication",
    docs_url="/docs",
)

# ==================== Authentication Endpoints ====================

@api.post("/auth/register", response={201: TokenResponse, 400: ErrorResponse}, tags=["Authentication"])
def register(request, payload: UserCreate):
    """Register a new user"""
    
    # Check if email exists
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already registered")
    
    # Check if username exists
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already taken")
    
    # Create user
    user = User.objects.create_user(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        first_name=payload.first_name or "",
        last_name=payload.last_name or "",
        role=payload.role,
        bio=payload.bio or "",
        phone=payload.phone or "",
    )
    
    # Generate token
    token = create_jwt_token(user)
    
    return 201, {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.from_orm(user)
    }


@api.post("/auth/login", response={200: TokenResponse, 401: ErrorResponse}, tags=["Authentication"])
def login(request, payload: UserLogin):
    """Login and get JWT token"""
    
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        raise HttpError(401, "Invalid credentials")
    
    if not user.check_password(payload.password):
        raise HttpError(401, "Invalid credentials")
    
    if not user.is_active:
        raise HttpError(401, "Account is inactive")
    
    # Update last login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Generate token
    token = create_jwt_token(user)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.from_orm(user)
    }


@api.get("/auth/me", response=UserOut, auth=JWTAuth(), tags=["Authentication"])
def get_current_user(request):
    """Get current authenticated user"""
    return request.auth


# ==================== User Endpoints ====================

@api.get("/users", response=List[UserOut], auth=JWTAuth(), tags=["Users"])
@require_role('admin')
def list_users(request, role: str = None):
    """List all users (Admin only)"""
    users = User.objects.all()
    
    if role:
        users = users.filter(role=role)
    
    return users


@api.get("/users/{user_id}", response=UserOut, auth=JWTAuth(), tags=["Users"])
def get_user(request, user_id: int):
    """Get user by ID"""
    user = get_object_or_404(User, id=user_id)
    return user


@api.put("/users/{user_id}", response=UserOut, auth=JWTAuth(), tags=["Users"])
def update_user(request, user_id: int, payload: UserUpdate):
    """Update user profile"""
    user = get_object_or_404(User, id=user_id)
    
    # Check permission
    if request.auth.id != user_id and not request.auth.is_admin():
        raise HttpError(403, "Permission denied")
    
    # Update fields
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.save()
    return user


@api.delete("/users/{user_id}", response=MessageResponse, auth=JWTAuth(), tags=["Users"])
@require_role('admin')
def delete_user(request, user_id: int):
    """Delete user (Admin only)"""
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return {"message": "User deleted successfully"}


# ==================== Course Endpoints ====================

@api.get("/courses", response=List[CourseOut], tags=["Courses"])
def list_courses(request, category: str = None, level: str = None, instructor_id: int = None):
    """List all active courses (with Redis caching)"""
    
    # Build cache key
    cache_key = f"courses_list_{category}_{level}_{instructor_id}"
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Query database
    courses = Course.objects.get_active().select_related('instructor')
    
    if category:
        courses = courses.filter(category=category)
    if level:
        courses = courses.filter(level=level)
    if instructor_id:
        courses = courses.filter(instructor_id=instructor_id)
    
    # Annotate with counts
    courses = courses.annotate(
        enrollment_count=Count('enrollments')
    )
    
    # Convert to schema
    result = []
    for course in courses:
        course_data = CourseOut.from_orm(course)
        course_data.instructor_name = course.instructor.get_full_name()
        course_data.enrollment_count = course.enrollment_count
        result.append(course_data)
    
    # Cache for 5 minutes
    cache.set(cache_key, result, 300)
    
    return result


@api.get("/courses/{course_id}", response=CourseDetailOut, tags=["Courses"])
def get_course(request, course_id: int):
    """Get course details with lessons and assignments"""
    
    cache_key = f"course_detail_{course_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    course = get_object_or_404(
        Course.objects.select_related('instructor')
        .prefetch_related('lessons', 'assignments'),
        id=course_id
    )
    
    course_data = CourseDetailOut.from_orm(course)
    course_data.instructor_name = course.instructor.get_full_name()
    course_data.enrollment_count = course.get_enrollment_count()
    course_data.lessons = [LessonOut.from_orm(l) for l in course.lessons.all()]
    course_data.assignments = [AssignmentOut.from_orm(a) for a in course.assignments.all()]
    
    cache.set(cache_key, course_data, 300)
    return course_data


@api.post("/courses", response={201: CourseOut}, auth=JWTAuth(), tags=["Courses"])
@require_role('admin', 'dosen')
def create_course(request, payload: CourseCreate):
    """Create new course (Dosen and Admin only)"""
    
    # Check if slug exists
    if Course.objects.filter(slug=payload.slug).exists():
        raise HttpError(400, "Course with this slug already exists")
    
    course = Course.objects.create(
        instructor=request.auth,
        **payload.dict()
    )
    
    # Invalidate cache
    cache.delete_pattern("courses_list_*")
    
    result = CourseOut.from_orm(course)
    result.instructor_name = course.instructor.get_full_name()
    return 201, result


@api.put("/courses/{course_id}", response=CourseOut, auth=JWTAuth(), tags=["Courses"])
@require_role('admin', 'dosen')
def update_course(request, course_id: int, payload: CourseUpdate):
    """Update course (Owner or Admin only)"""
    course = get_object_or_404(Course, id=course_id)
    
    # Check permission
    if course.instructor != request.auth and not request.auth.is_admin():
        raise HttpError(403, "Permission denied")
    
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(course, field, value)
    
    course.save()
    
    # Invalidate cache
    cache.delete_pattern("courses_*")
    
    result = CourseOut.from_orm(course)
    result.instructor_name = course.instructor.get_full_name()
    return result


@api.delete("/courses/{course_id}", response=MessageResponse, auth=JWTAuth(), tags=["Courses"])
@require_role('admin', 'dosen')
def delete_course(request, course_id: int):
    """Delete course (Owner or Admin only)"""
    course = get_object_or_404(Course, id=course_id)
    
    if course.instructor != request.auth and not request.auth.is_admin():
        raise HttpError(403, "Permission denied")
    
    course.delete()
    
    # Invalidate cache
    cache.delete_pattern("courses_*")
    
    return {"message": "Course deleted successfully"}


# ==================== Enrollment Endpoints ====================

@api.post("/enrollments", response={201: EnrollmentOut}, auth=JWTAuth(), tags=["Enrollments"])
@require_role('mahasiswa')
def enroll_course(request, payload: EnrollmentCreate):
    """Enroll in a course (Mahasiswa only)"""
    
    course = get_object_or_404(Course, id=payload.course_id, is_active=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.auth, course=course).exists():
        raise HttpError(400, "Already enrolled in this course")
    
    enrollment = Enrollment.objects.create(
        student=request.auth,
        course=course
    )
    
    # Invalidate cache
    cache.delete_pattern("courses_*")
    
    return 201, EnrollmentOut.from_orm(enrollment)


@api.get("/enrollments/my", response=List[EnrollmentOut], auth=JWTAuth(), tags=["Enrollments"])
@require_role('mahasiswa')
def my_enrollments(request):
    """Get current user's enrollments"""
    enrollments = Enrollment.objects.filter(student=request.auth, is_active=True)
    return enrollments


# ==================== Lesson Endpoints ====================

@api.post("/lessons", response={201: LessonOut}, auth=JWTAuth(), tags=["Lessons"])
@require_role('admin', 'dosen')
def create_lesson(request, payload: LessonCreate):
    """Create new lesson (Dosen and Admin only)"""
    
    course = get_object_or_404(Course, id=payload.course_id)
    
    # Check permission
    if course.instructor != request.auth and not request.auth.is_admin():
        raise HttpError(403, "Permission denied")
    
    lesson = Lesson.objects.create(**payload.dict())
    
    # Invalidate cache
    cache.delete(f"course_detail_{course.id}")
    
    return 201, LessonOut.from_orm(lesson)


@api.put("/lessons/{lesson_id}", response=LessonOut, auth=JWTAuth(), tags=["Lessons"])
@require_role('admin', 'dosen')
def update_lesson(request, lesson_id: int, payload: LessonUpdate):
    """Update lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if lesson.course.instructor != request.auth and not request.auth.is_admin():
        raise HttpError(403, "Permission denied")
    
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(lesson, field, value)
    
    lesson.save()
    
    # Invalidate cache
    cache.delete(f"course_detail_{lesson.course_id}")
    
    return LessonOut.from_orm(lesson)


@api.delete("/lessons/{lesson_id}", response=MessageResponse, auth=JWTAuth(), tags=["Lessons"])
@require_role('admin', 'dosen')
def delete_lesson(request, lesson_id: int):
    """Delete lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if lesson.course.instructor != request.auth and not request.auth.is_admin():
        raise HttpError(403, "Permission denied")
    
    course_id = lesson.course_id
    lesson.delete()
    
    # Invalidate cache
    cache.delete(f"course_detail_{course_id}")
    
    return {"message": "Lesson deleted successfully"}


# ==================== Assignment Endpoints ====================

@api.post("/assignments", response={201: AssignmentOut}, auth=JWTAuth(), tags=["Assignments"])
@require_role('admin', 'dosen')
def create_assignment(request, payload: AssignmentCreate):
    """Create new assignment"""
    course = get_object_or_404(Course, id=payload.course_id)
    
    if course.instructor != request.auth and not request.auth.is_admin():
        raise HttpError(403, "Permission denied")
    
    assignment = Assignment.objects.create(**payload.dict())
    
    result = AssignmentOut.from_orm(assignment)
    result.is_overdue = assignment.is_overdue()
    
    return 201, result


@api.get("/assignments/{assignment_id}", response=AssignmentOut, auth=JWTAuth(), tags=["Assignments"])
def get_assignment(request, assignment_id: int):
    """Get assignment details"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    result = AssignmentOut.from_orm(assignment)
    result.is_overdue = assignment.is_overdue()
    
    return result


# ==================== Submission Endpoints ====================

@api.post("/submissions", response={201: SubmissionOut}, auth=JWTAuth(), tags=["Submissions"])
@require_role('mahasiswa')
def create_submission(request, payload: SubmissionCreate):
    """Submit assignment"""
    assignment = get_object_or_404(Assignment, id=payload.assignment_id)
    
    # Check if already submitted
    if Submission.objects.filter(assignment=assignment, student=request.auth).exists():
        raise HttpError(400, "Already submitted this assignment")
    
    submission = Submission.objects.create(
        assignment=assignment,
        student=request.auth,
        content=payload.content
    )
    
    result = SubmissionOut.from_orm(submission)
    result.is_late = submission.is_late()
    result.is_graded = submission.is_graded()
    
    return 201, result


@api.get("/submissions/my", response=List[SubmissionOut], auth=JWTAuth(), tags=["Submissions"])
@require_role('mahasiswa')
def my_submissions(request):
    """Get current user's submissions"""
    submissions = Submission.objects.filter(student=request.auth)
    
    result = []
    for sub in submissions:
        sub_data = SubmissionOut.from_orm(sub)
        sub_data.is_late = sub.is_late()
        sub_data.is_graded = sub.is_graded()
        result.append(sub_data)
    
    return result


@api.post("/submissions/{submission_id}/grade", response=SubmissionOut, auth=JWTAuth(), tags=["Submissions"])
@require_role('admin', 'dosen')
def grade_submission(request, submission_id: int, payload: SubmissionGrade):
    """Grade submission (Dosen and Admin only)"""
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Check permission
    if submission.assignment.course.instructor != request.auth and not request.auth.is_admin():
        raise HttpError(403, "Permission denied")
    
    submission.score = payload.score
    submission.feedback = payload.feedback or ""
    submission.graded_by = request.auth
    submission.graded_at = timezone.now()
    submission.save()
    
    result = SubmissionOut.from_orm(submission)
    result.is_late = submission.is_late()
    result.is_graded = submission.is_graded()
    
    return result


# ==================== Test Endpoints ====================

@api.get("/test-session", tags=["Testing"])
def test_session(request):
    """Test session storage in Redis"""
    request.session['test_key'] = 'test_value'
    request.session['timestamp'] = str(timezone.now())
    return {"session": "created", "data": dict(request.session.items())}


@api.get("/health", tags=["Testing"])
def health_check(request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": timezone.now().isoformat()
    }
