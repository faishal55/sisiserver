# Simple LMS API Documentation

## Base URL
```
http://localhost:8000/api/lms
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Response Format
All responses are in JSON format. Success responses follow this structure:
```json
{
  "data": {...},
  "message": "Success message"
}
```

Error responses:
```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

---

## Authentication Endpoints

### Register New User
Creates a new user account.

**Endpoint:** `POST /auth/register`  
**Authentication:** Not required  
**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "mahasiswa",  // Options: admin, dosen, mahasiswa
  "bio": "Optional bio",
  "phone": "Optional phone"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "role": "mahasiswa",
    "is_active": true,
    "date_joined": "2026-01-08T10:00:00Z"
  }
}
```

### Login
Authenticate and get JWT token.

**Endpoint:** `POST /auth/login`  
**Authentication:** Not required  
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "mahasiswa"
  }
}
```

### Get Current User
Get authenticated user information.

**Endpoint:** `GET /auth/me`  
**Authentication:** Required  

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "role": "mahasiswa",
  "bio": "Student bio",
  "phone": "1234567890",
  "is_active": true,
  "date_joined": "2026-01-08T10:00:00Z"
}
```

---

## Course Endpoints

### List All Courses
Get all active courses (cached for 5 minutes).

**Endpoint:** `GET /courses`  
**Authentication:** Not required  
**Query Parameters:**
- `category` (optional): Filter by category
- `level` (optional): Filter by level (beginner, intermediate, advanced)
- `instructor_id` (optional): Filter by instructor

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Python Programming Fundamentals",
    "slug": "python-programming",
    "description": "Learn Python from scratch",
    "category": "Programming",
    "level": "beginner",
    "instructor_id": 2,
    "instructor_name": "Dr. John Doe",
    "is_active": true,
    "created_at": "2026-01-01T10:00:00Z",
    "updated_at": "2026-01-01T10:00:00Z",
    "enrollment_count": 15
  }
]
```

### Get Course Details
Get detailed course information including lessons and assignments.

**Endpoint:** `GET /courses/{course_id}`  
**Authentication:** Not required  

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Python Programming Fundamentals",
  "slug": "python-programming",
  "description": "Learn Python from scratch",
  "category": "Programming",
  "level": "beginner",
  "instructor_id": 2,
  "instructor_name": "Dr. John Doe",
  "is_active": true,
  "enrollment_count": 15,
  "lessons": [
    {
      "id": 1,
      "title": "Introduction to Python",
      "slug": "intro-python",
      "description": "Getting started",
      "order": 1,
      "duration_minutes": 30,
      "is_published": true
    }
  ],
  "assignments": [
    {
      "id": 1,
      "title": "Python Basics Quiz",
      "description": "Test your knowledge",
      "max_score": 100,
      "due_date": "2026-01-15T23:59:59Z",
      "is_overdue": false
    }
  ]
}
```

### Create Course
Create a new course (Dosen and Admin only).

**Endpoint:** `POST /courses`  
**Authentication:** Required (role: dosen or admin)  
**Request Body:**
```json
{
  "title": "New Course",
  "slug": "new-course",
  "description": "Course description",
  "category": "Programming",
  "level": "beginner"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "title": "New Course",
  "slug": "new-course",
  "description": "Course description",
  "category": "Programming",
  "level": "beginner",
  "instructor_id": 2,
  "is_active": true,
  "created_at": "2026-01-08T10:00:00Z"
}
```

### Update Course
Update an existing course (Owner or Admin only).

**Endpoint:** `PUT /courses/{course_id}`  
**Authentication:** Required (owner or admin)  
**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "is_active": true
}
```

### Delete Course
Delete a course (Owner or Admin only).

**Endpoint:** `DELETE /courses/{course_id}`  
**Authentication:** Required (owner or admin)  

**Response (200 OK):**
```json
{
  "message": "Course deleted successfully"
}
```

---

## Enrollment Endpoints

### Enroll in Course
Enroll current user in a course (Mahasiswa only).

**Endpoint:** `POST /enrollments`  
**Authentication:** Required (role: mahasiswa)  
**Request Body:**
```json
{
  "course_id": 1
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "student_id": 3,
  "course_id": 1,
  "enrolled_at": "2026-01-08T10:00:00Z",
  "is_active": true,
  "progress": 0.0
}
```

### Get My Enrollments
Get all enrollments for current user (Mahasiswa only).

**Endpoint:** `GET /enrollments/my`  
**Authentication:** Required (role: mahasiswa)  

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "student_id": 3,
    "course_id": 1,
    "enrolled_at": "2026-01-08T10:00:00Z",
    "is_active": true,
    "progress": 25.5
  }
]
```

---

## Lesson Endpoints

### Create Lesson
Create a new lesson (Dosen and Admin only).

**Endpoint:** `POST /lessons`  
**Authentication:** Required (role: dosen or admin)  
**Request Body:**
```json
{
  "course_id": 1,
  "title": "Lesson Title",
  "slug": "lesson-slug",
  "description": "Lesson description",
  "content": "Lesson content here...",
  "video_url": "https://youtube.com/watch?v=...",
  "duration_minutes": 45,
  "order": 1,
  "is_published": true
}
```

### Update Lesson
Update an existing lesson.

**Endpoint:** `PUT /lessons/{lesson_id}`  
**Authentication:** Required (owner or admin)  

### Delete Lesson
Delete a lesson.

**Endpoint:** `DELETE /lessons/{lesson_id}`  
**Authentication:** Required (owner or admin)  

---

## Assignment Endpoints

### Create Assignment
Create a new assignment (Dosen and Admin only).

**Endpoint:** `POST /assignments`  
**Authentication:** Required (role: dosen or admin)  
**Request Body:**
```json
{
  "course_id": 1,
  "title": "Assignment Title",
  "description": "Assignment description",
  "instructions": "Complete the following tasks...",
  "max_score": 100,
  "due_date": "2026-01-15T23:59:59Z"
}
```

### Get Assignment
Get assignment details.

**Endpoint:** `GET /assignments/{assignment_id}`  
**Authentication:** Required  

**Response (200 OK):**
```json
{
  "id": 1,
  "course_id": 1,
  "title": "Assignment Title",
  "description": "Assignment description",
  "instructions": "Complete the following...",
  "max_score": 100,
  "due_date": "2026-01-15T23:59:59Z",
  "created_at": "2026-01-08T10:00:00Z",
  "is_overdue": false
}
```

---

## Submission Endpoints

### Submit Assignment
Submit an assignment (Mahasiswa only).

**Endpoint:** `POST /submissions`  
**Authentication:** Required (role: mahasiswa)  
**Request Body:**
```json
{
  "assignment_id": 1,
  "content": "My submission content here..."
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "assignment_id": 1,
  "student_id": 3,
  "content": "My submission content...",
  "submitted_at": "2026-01-08T15:30:00Z",
  "score": null,
  "feedback": null,
  "is_late": false,
  "is_graded": false
}
```

### Get My Submissions
Get all submissions for current user (Mahasiswa only).

**Endpoint:** `GET /submissions/my`  
**Authentication:** Required (role: mahasiswa)  

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "assignment_id": 1,
    "student_id": 3,
    "content": "Submission content...",
    "submitted_at": "2026-01-08T15:30:00Z",
    "score": 85.5,
    "feedback": "Good work!",
    "graded_at": "2026-01-09T10:00:00Z",
    "graded_by_id": 2,
    "is_late": false,
    "is_graded": true
  }
]
```

### Grade Submission
Grade a student submission (Dosen and Admin only).

**Endpoint:** `POST /submissions/{submission_id}/grade`  
**Authentication:** Required (role: dosen or admin)  
**Request Body:**
```json
{
  "score": 85.5,
  "feedback": "Good work! Keep it up."
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "assignment_id": 1,
  "student_id": 3,
  "score": 85.5,
  "feedback": "Good work! Keep it up.",
  "graded_at": "2026-01-09T10:00:00Z",
  "graded_by_id": 2,
  "is_graded": true
}
```

---

## Testing Endpoints

### Test Session
Test Redis session storage.

**Endpoint:** `GET /test-session`  
**Authentication:** Not required  

**Response (200 OK):**
```json
{
  "session": "created",
  "data": {
    "test_key": "test_value",
    "timestamp": "2026-01-08T10:00:00"
  }
}
```

### Health Check
Check API health status.

**Endpoint:** `GET /health`  
**Authentication:** Not required  

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-08T10:00:00.000Z"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

---

## Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **admin** | Full access to all resources |
| **dosen** | Create/edit courses, lessons, assignments; Grade submissions |
| **mahasiswa** | View courses, enroll, submit assignments |

---

## Rate Limiting
No rate limiting currently implemented. Consider adding for production.

---

## Caching
- Course lists are cached for 5 minutes
- Course details are cached for 5 minutes
- Cache is automatically invalidated on data changes

---

## Interactive Documentation
Visit `/api/lms/docs` for interactive Swagger UI documentation where you can test all endpoints.
