"""
Django models for Simple LMS
Implements User, Course, Lesson, Assignment, and Submission models
with custom managers and role-based access control
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Q, Count, Avg


class UserRole(models.TextChoices):
    """User role choices for RBAC"""
    ADMIN = 'admin', 'Administrator'
    DOSEN = 'dosen', 'Dosen'
    MAHASISWA = 'mahasiswa', 'Mahasiswa'


class UserManager(BaseUserManager):
    """Custom manager for User model"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)
    
    def get_by_role(self, role):
        """Get users by role"""
        return self.filter(role=role, is_active=True)
    
    def get_dosen(self):
        """Get all dosen users"""
        return self.get_by_role(UserRole.DOSEN)
    
    def get_mahasiswa(self):
        """Get all mahasiswa users"""
        return self.get_by_role(UserRole.MAHASISWA)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with role-based access control"""
    
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.MAHASISWA,
        db_index=True
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Additional profile fields
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['username', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return full name of user"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def is_dosen(self):
        """Check if user is dosen"""
        return self.role == UserRole.DOSEN
    
    def is_mahasiswa(self):
        """Check if user is mahasiswa"""
        return self.role == UserRole.MAHASISWA


class CourseManager(models.Manager):
    """Custom manager for Course model"""
    
    def get_active(self):
        """Get all active courses"""
        return self.filter(is_active=True)
    
    def get_by_instructor(self, instructor):
        """Get courses by instructor"""
        return self.filter(instructor=instructor, is_active=True)
    
    def get_enrolled_by_student(self, student):
        """Get courses enrolled by student"""
        return self.filter(enrollments__student=student, is_active=True)
    
    def with_stats(self):
        """Get courses with enrollment and lesson stats"""
        return self.annotate(
            enrollment_count=Count('enrollments', distinct=True),
            lesson_count=Count('lessons', distinct=True)
        )


class Course(models.Model):
    """Course model representing a course in the LMS"""
    
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'role': UserRole.DOSEN}
    )
    
    # Course details
    thumbnail = models.ImageField(upload_to='courses/', null=True, blank=True)
    category = models.CharField(max_length=100, db_index=True)
    level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    
    # Enrollment
    students = models.ManyToManyField(
        User,
        through='Enrollment',
        related_name='courses_enrolled',
        limit_choices_to={'role': UserRole.MAHASISWA}
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CourseManager()
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['instructor', 'created_at']),
            models.Index(fields=['category', 'level']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_enrollment_count(self):
        """Get number of enrolled students"""
        return self.enrollments.filter(is_active=True).count()
    
    def is_enrolled(self, student):
        """Check if student is enrolled"""
        return self.enrollments.filter(student=student, is_active=True).exists()


class Enrollment(models.Model):
    """Enrollment model for many-to-many relationship between Course and User"""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['student', 'is_active']),
            models.Index(fields=['course', 'enrolled_at']),
        ]
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class LessonManager(models.Manager):
    """Custom manager for Lesson model"""
    
    def get_by_course(self, course):
        """Get lessons by course"""
        return self.filter(course=course).order_by('order')
    
    def get_published(self):
        """Get published lessons"""
        return self.filter(is_published=True)


class Lesson(models.Model):
    """Lesson model representing a lesson/module in a course"""
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    
    # Content
    content = models.TextField()
    video_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    # Status
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = LessonManager()
    
    class Meta:
        db_table = 'lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['course', 'order']
        unique_together = ['course', 'slug']
        indexes = [
            models.Index(fields=['course', 'order']),
            models.Index(fields=['is_published', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class AssignmentManager(models.Manager):
    """Custom manager for Assignment model"""
    
    def get_by_course(self, course):
        """Get assignments by course"""
        return self.filter(course=course).order_by('-due_date')
    
    def get_active(self):
        """Get active assignments"""
        return self.filter(due_date__gte=timezone.now())
    
    def get_overdue(self):
        """Get overdue assignments"""
        return self.filter(due_date__lt=timezone.now())


class Assignment(models.Model):
    """Assignment model representing an assignment in a course"""
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Assignment details
    instructions = models.TextField()
    max_score = models.PositiveIntegerField(default=100)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    
    # Files
    attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
    
    objects = AssignmentManager()
    
    class Meta:
        db_table = 'assignments'
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['course', 'due_date']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def is_overdue(self):
        """Check if assignment is overdue"""
        return timezone.now() > self.due_date
    
    def get_average_score(self):
        """Get average score for this assignment"""
        return self.submissions.filter(
            score__isnull=False
        ).aggregate(Avg('score'))['score__avg'] or 0


class SubmissionManager(models.Manager):
    """Custom manager for Submission model"""
    
    def get_by_student(self, student):
        """Get submissions by student"""
        return self.filter(student=student).order_by('-submitted_at')
    
    def get_by_assignment(self, assignment):
        """Get submissions by assignment"""
        return self.filter(assignment=assignment).order_by('-submitted_at')
    
    def get_graded(self):
        """Get graded submissions"""
        return self.filter(score__isnull=False)
    
    def get_pending(self):
        """Get pending submissions"""
        return self.filter(score__isnull=True)


class Submission(models.Model):
    """Submission model representing a student's submission for an assignment"""
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions',
        limit_choices_to={'role': UserRole.MAHASISWA}
    )
    
    # Submission content
    content = models.TextField()
    attachment = models.FileField(upload_to='submissions/', null=True, blank=True)
    
    # Dates
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Grading
    score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    
    objects = SubmissionManager()
    
    class Meta:
        db_table = 'submissions'
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']
        indexes = [
            models.Index(fields=['assignment', 'student']),
            models.Index(fields=['student', 'submitted_at']),
            models.Index(fields=['score', 'graded_at']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    def is_late(self):
        """Check if submission was late"""
        return self.submitted_at > self.assignment.due_date
    
    def is_graded(self):
        """Check if submission is graded"""
        return self.score is not None
