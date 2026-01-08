"""
Unit tests for Simple LMS models and API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from lms.models import Course, Lesson, Assignment, Submission, Enrollment, UserRole

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='testpass123',
            role=UserRole.ADMIN
        )
        self.dosen = User.objects.create_user(
            email='dosen@test.com',
            username='dosen',
            password='testpass123',
            role=UserRole.DOSEN
        )
        self.mahasiswa = User.objects.create_user(
            email='mahasiswa@test.com',
            username='mahasiswa',
            password='testpass123',
            role=UserRole.MAHASISWA
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.admin.email, 'admin@test.com')
        self.assertEqual(self.admin.username, 'admin')
        self.assertTrue(self.admin.check_password('testpass123'))
    
    def test_user_roles(self):
        """Test user role methods"""
        self.assertTrue(self.admin.is_admin())
        self.assertFalse(self.admin.is_dosen())
        self.assertFalse(self.admin.is_mahasiswa())
        
        self.assertTrue(self.dosen.is_dosen())
        self.assertFalse(self.dosen.is_admin())
        
        self.assertTrue(self.mahasiswa.is_mahasiswa())
        self.assertFalse(self.mahasiswa.is_admin())
    
    def test_user_manager_methods(self):
        """Test custom user manager methods"""
        dosen_users = User.objects.get_dosen()
        self.assertEqual(dosen_users.count(), 1)
        self.assertEqual(dosen_users.first(), self.dosen)
        
        mahasiswa_users = User.objects.get_mahasiswa()
        self.assertEqual(mahasiswa_users.count(), 1)
        self.assertEqual(mahasiswa_users.first(), self.mahasiswa)
    
    def test_user_string_representation(self):
        """Test user string representation"""
        self.assertIn(self.admin.username, str(self.admin))
        self.assertIn('Administrator', str(self.admin))


class CourseModelTest(TestCase):
    """Test Course model"""
    
    def setUp(self):
        """Set up test data"""
        self.dosen = User.objects.create_user(
            email='dosen@test.com',
            username='dosen',
            password='testpass123',
            role=UserRole.DOSEN
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test course description',
            instructor=self.dosen,
            category='Programming',
            level='beginner'
        )
    
    def test_course_creation(self):
        """Test course is created correctly"""
        self.assertEqual(self.course.title, 'Test Course')
        self.assertEqual(self.course.slug, 'test-course')
        self.assertEqual(self.course.instructor, self.dosen)
        self.assertTrue(self.course.is_active)
    
    def test_course_manager_methods(self):
        """Test course manager methods"""
        active_courses = Course.objects.get_active()
        self.assertEqual(active_courses.count(), 1)
        
        instructor_courses = Course.objects.get_by_instructor(self.dosen)
        self.assertEqual(instructor_courses.count(), 1)
    
    def test_course_enrollment_count(self):
        """Test course enrollment count"""
        mahasiswa = User.objects.create_user(
            email='student@test.com',
            username='student',
            password='testpass123',
            role=UserRole.MAHASISWA
        )
        Enrollment.objects.create(student=mahasiswa, course=self.course)
        self.assertEqual(self.course.get_enrollment_count(), 1)
    
    def test_course_string_representation(self):
        """Test course string representation"""
        self.assertEqual(str(self.course), 'Test Course')


class EnrollmentModelTest(TestCase):
    """Test Enrollment model"""
    
    def setUp(self):
        """Set up test data"""
        self.dosen = User.objects.create_user(
            email='dosen@test.com',
            username='dosen',
            password='testpass123',
            role=UserRole.DOSEN
        )
        self.mahasiswa = User.objects.create_user(
            email='student@test.com',
            username='student',
            password='testpass123',
            role=UserRole.MAHASISWA
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test course',
            instructor=self.dosen,
            category='Programming',
            level='beginner'
        )
        self.enrollment = Enrollment.objects.create(
            student=self.mahasiswa,
            course=self.course
        )
    
    def test_enrollment_creation(self):
        """Test enrollment is created correctly"""
        self.assertEqual(self.enrollment.student, self.mahasiswa)
        self.assertEqual(self.enrollment.course, self.course)
        self.assertTrue(self.enrollment.is_active)
        self.assertEqual(self.enrollment.progress, 0.0)
    
    def test_course_is_enrolled(self):
        """Test course enrollment check"""
        self.assertTrue(self.course.is_enrolled(self.mahasiswa))


class LessonModelTest(TestCase):
    """Test Lesson model"""
    
    def setUp(self):
        """Set up test data"""
        self.dosen = User.objects.create_user(
            email='dosen@test.com',
            username='dosen',
            password='testpass123',
            role=UserRole.DOSEN
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test course',
            instructor=self.dosen,
            category='Programming',
            level='beginner'
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Test Lesson',
            slug='test-lesson',
            description='Test lesson description',
            content='Lesson content here',
            order=1,
            duration_minutes=30,
            is_published=True
        )
    
    def test_lesson_creation(self):
        """Test lesson is created correctly"""
        self.assertEqual(self.lesson.title, 'Test Lesson')
        self.assertEqual(self.lesson.course, self.course)
        self.assertEqual(self.lesson.order, 1)
        self.assertTrue(self.lesson.is_published)
    
    def test_lesson_manager_methods(self):
        """Test lesson manager methods"""
        course_lessons = Lesson.objects.get_by_course(self.course)
        self.assertEqual(course_lessons.count(), 1)
        
        published_lessons = Lesson.objects.get_published()
        self.assertEqual(published_lessons.count(), 1)


class AssignmentModelTest(TestCase):
    """Test Assignment model"""
    
    def setUp(self):
        """Set up test data"""
        self.dosen = User.objects.create_user(
            email='dosen@test.com',
            username='dosen',
            password='testpass123',
            role=UserRole.DOSEN
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test course',
            instructor=self.dosen,
            category='Programming',
            level='beginner'
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test assignment description',
            instructions='Complete the task',
            max_score=100,
            due_date=timezone.now() + timedelta(days=7)
        )
    
    def test_assignment_creation(self):
        """Test assignment is created correctly"""
        self.assertEqual(self.assignment.title, 'Test Assignment')
        self.assertEqual(self.assignment.course, self.course)
        self.assertEqual(self.assignment.max_score, 100)
    
    def test_assignment_is_overdue(self):
        """Test assignment overdue check"""
        self.assertFalse(self.assignment.is_overdue())
        
        # Create overdue assignment
        overdue_assignment = Assignment.objects.create(
            course=self.course,
            title='Overdue Assignment',
            description='Test',
            instructions='Test',
            max_score=100,
            due_date=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(overdue_assignment.is_overdue())


class SubmissionModelTest(TestCase):
    """Test Submission model"""
    
    def setUp(self):
        """Set up test data"""
        self.dosen = User.objects.create_user(
            email='dosen@test.com',
            username='dosen',
            password='testpass123',
            role=UserRole.DOSEN
        )
        self.mahasiswa = User.objects.create_user(
            email='student@test.com',
            username='student',
            password='testpass123',
            role=UserRole.MAHASISWA
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test course',
            instructor=self.dosen,
            category='Programming',
            level='beginner'
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test',
            instructions='Complete',
            max_score=100,
            due_date=timezone.now() + timedelta(days=7)
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.mahasiswa,
            content='My submission content'
        )
    
    def test_submission_creation(self):
        """Test submission is created correctly"""
        self.assertEqual(self.submission.assignment, self.assignment)
        self.assertEqual(self.submission.student, self.mahasiswa)
        self.assertIsNone(self.submission.score)
        self.assertFalse(self.submission.is_graded())
    
    def test_submission_grading(self):
        """Test submission grading"""
        self.submission.score = 85.0
        self.submission.feedback = 'Good work'
        self.submission.graded_by = self.dosen
        self.submission.graded_at = timezone.now()
        self.submission.save()
        
        self.assertTrue(self.submission.is_graded())
        self.assertEqual(self.submission.score, 85.0)
    
    def test_submission_is_late(self):
        """Test submission late check"""
        self.assertFalse(self.submission.is_late())
        
        # Create late submission
        late_assignment = Assignment.objects.create(
            course=self.course,
            title='Past Assignment',
            description='Test',
            instructions='Test',
            max_score=100,
            due_date=timezone.now() - timedelta(days=1)
        )
        late_submission = Submission.objects.create(
            assignment=late_assignment,
            student=self.mahasiswa,
            content='Late submission'
        )
        self.assertTrue(late_submission.is_late())
