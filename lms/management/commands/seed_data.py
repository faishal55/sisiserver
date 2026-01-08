"""
Management command to seed database with initial data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from lms.models import Course, Lesson, Assignment, Submission, Enrollment, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with initial test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create Users
        self.stdout.write('Creating users...')
        
        # Admin
        admin, created = User.objects.get_or_create(
            email='admin@lms.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': UserRole.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created admin: {admin.email}'))
        
        # Dosen
        dosen1, created = User.objects.get_or_create(
            email='dosen1@lms.com',
            defaults={
                'username': 'dosen1',
                'first_name': 'Dr. John',
                'last_name': 'Doe',
                'role': UserRole.DOSEN,
                'bio': 'Professor of Computer Science',
            }
        )
        if created:
            dosen1.set_password('dosen123')
            dosen1.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created dosen: {dosen1.email}'))
        
        dosen2, created = User.objects.get_or_create(
            email='dosen2@lms.com',
            defaults={
                'username': 'dosen2',
                'first_name': 'Dr. Jane',
                'last_name': 'Smith',
                'role': UserRole.DOSEN,
                'bio': 'Assistant Professor of Software Engineering',
            }
        )
        if created:
            dosen2.set_password('dosen123')
            dosen2.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created dosen: {dosen2.email}'))
        
        # Mahasiswa
        students = []
        for i in range(1, 6):
            student, created = User.objects.get_or_create(
                email=f'student{i}@lms.com',
                defaults={
                    'username': f'student{i}',
                    'first_name': f'Student',
                    'last_name': f'{i}',
                    'role': UserRole.MAHASISWA,
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created student: {student.email}'))
            students.append(student)
        
        # Create Courses
        self.stdout.write('\nCreating courses...')
        
        course1, created = Course.objects.get_or_create(
            slug='python-programming',
            defaults={
                'title': 'Python Programming Fundamentals',
                'description': 'Learn Python programming from scratch with hands-on projects',
                'instructor': dosen1,
                'category': 'Programming',
                'level': 'beginner',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created course: {course1.title}'))
        
        course2, created = Course.objects.get_or_create(
            slug='web-development',
            defaults={
                'title': 'Modern Web Development',
                'description': 'Build modern web applications with Django and React',
                'instructor': dosen1,
                'category': 'Web Development',
                'level': 'intermediate',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created course: {course2.title}'))
        
        course3, created = Course.objects.get_or_create(
            slug='data-science',
            defaults={
                'title': 'Data Science with Python',
                'description': 'Master data science concepts using Python and popular libraries',
                'instructor': dosen2,
                'category': 'Data Science',
                'level': 'advanced',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created course: {course3.title}'))
        
        # Create Lessons
        self.stdout.write('\nCreating lessons...')
        
        # Python course lessons
        lessons_python = [
            {
                'title': 'Introduction to Python',
                'slug': 'intro-python',
                'description': 'Getting started with Python programming',
                'content': 'Python is a high-level, interpreted programming language...',
                'order': 1,
                'duration_minutes': 30,
                'is_published': True,
            },
            {
                'title': 'Variables and Data Types',
                'slug': 'variables-datatypes',
                'description': 'Understanding Python variables and data types',
                'content': 'In Python, variables are used to store data...',
                'order': 2,
                'duration_minutes': 45,
                'is_published': True,
            },
            {
                'title': 'Control Flow',
                'slug': 'control-flow',
                'description': 'If statements, loops, and more',
                'content': 'Control flow statements control the order...',
                'order': 3,
                'duration_minutes': 60,
                'is_published': True,
            },
        ]
        
        for lesson_data in lessons_python:
            lesson, created = Lesson.objects.get_or_create(
                course=course1,
                slug=lesson_data['slug'],
                defaults=lesson_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created lesson: {lesson.title}'))
        
        # Create Assignments
        self.stdout.write('\nCreating assignments...')
        
        assignment1, created = Assignment.objects.get_or_create(
            course=course1,
            title='Python Basics Quiz',
            defaults={
                'description': 'Test your understanding of Python basics',
                'instructions': 'Complete the quiz within the time limit',
                'max_score': 100,
                'due_date': timezone.now() + timedelta(days=7),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created assignment: {assignment1.title}'))
        
        assignment2, created = Assignment.objects.get_or_create(
            course=course1,
            title='Build a Calculator',
            defaults={
                'description': 'Create a simple calculator application',
                'instructions': 'Use functions and handle exceptions properly',
                'max_score': 100,
                'due_date': timezone.now() + timedelta(days=14),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created assignment: {assignment2.title}'))
        
        # Create Enrollments
        self.stdout.write('\nCreating enrollments...')
        
        for student in students[:3]:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course1,
                defaults={'is_active': True, 'progress': 0}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Enrolled {student.username} in {course1.title}'))
        
        for student in students[2:]:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course2,
                defaults={'is_active': True, 'progress': 0}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Enrolled {student.username} in {course2.title}'))
        
        # Create some submissions
        self.stdout.write('\nCreating submissions...')
        
        submission1, created = Submission.objects.get_or_create(
            assignment=assignment1,
            student=students[0],
            defaults={
                'content': 'My quiz submission with all answers',
                'score': 85.0,
                'feedback': 'Good work! Keep it up.',
                'graded_by': dosen1,
                'graded_at': timezone.now(),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created submission for {students[0].username}'))
        
        submission2, created = Submission.objects.get_or_create(
            assignment=assignment1,
            student=students[1],
            defaults={
                'content': 'Calculator code implementation',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created submission for {students[1].username}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('\nTest Accounts:')
        self.stdout.write('  Admin: admin@lms.com / admin123')
        self.stdout.write('  Dosen: dosen1@lms.com / dosen123')
        self.stdout.write('  Student: student1@lms.com / student123')
