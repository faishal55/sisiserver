"""
Django Admin configuration for LMS models
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Course, Lesson, Assignment, Submission, Enrollment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'bio', 'phone', 'avatar')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


class LessonInline(admin.TabularInline):
    """Inline admin for Lesson"""
    model = Lesson
    extra = 0
    fields = ['title', 'order', 'duration_minutes', 'is_published']
    ordering = ['order']


class AssignmentInline(admin.TabularInline):
    """Inline admin for Assignment"""
    model = Assignment
    extra = 0
    fields = ['title', 'due_date', 'max_score']
    ordering = ['-due_date']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model"""
    
    list_display = ['title', 'instructor', 'category', 'level', 'enrollment_count_display', 'is_active', 'created_at']
    list_filter = ['category', 'level', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'instructor__username']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'instructor')
        }),
        ('Course Details', {
            'fields': ('category', 'level', 'thumbnail')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    inlines = [LessonInline, AssignmentInline]
    
    readonly_fields = ['created_at', 'updated_at']
    
    def enrollment_count_display(self, obj):
        count = obj.get_enrollment_count()
        return format_html('<b>{}</b> students', count)
    enrollment_count_display.short_description = 'Enrollments'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for Lesson model"""
    
    list_display = ['title', 'course', 'order', 'duration_minutes', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at', 'course']
    search_fields = ['title', 'description', 'course__title']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['course', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'slug', 'description')
        }),
        ('Content', {
            'fields': ('content', 'video_url', 'duration_minutes')
        }),
        ('Settings', {
            'fields': ('order', 'is_published')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin interface for Assignment model"""
    
    list_display = ['title', 'course', 'due_date', 'max_score', 'average_score_display', 'is_overdue_display']
    list_filter = ['due_date', 'created_at', 'course']
    search_fields = ['title', 'description', 'course__title']
    date_hierarchy = 'due_date'
    ordering = ['-due_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description')
        }),
        ('Assignment Details', {
            'fields': ('instructions', 'max_score', 'due_date', 'attachment')
        }),
    )
    
    readonly_fields = ['created_at']
    
    def average_score_display(self, obj):
        avg = obj.get_average_score()
        if avg > 0:
            return format_html('<b>{:.1f}</b>', avg)
        return '-'
    average_score_display.short_description = 'Avg Score'
    
    def is_overdue_display(self, obj):
        if obj.is_overdue():
            return format_html('<span style="color: red;">✗ Overdue</span>')
        return format_html('<span style="color: green;">✓ Active</span>')
    is_overdue_display.short_description = 'Status'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Submission model"""
    
    list_display = ['student', 'assignment', 'submitted_at', 'score', 'is_graded_display', 'is_late_display']
    list_filter = ['submitted_at', 'graded_at', 'assignment__course']
    search_fields = ['student__username', 'assignment__title', 'content']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('assignment', 'student', 'content', 'attachment')
        }),
        ('Grading', {
            'fields': ('score', 'feedback', 'graded_by', 'graded_at')
        }),
    )
    
    readonly_fields = ['submitted_at', 'updated_at', 'graded_at']
    
    def is_graded_display(self, obj):
        if obj.is_graded():
            return format_html('<span style="color: green;">✓ Graded</span>')
        return format_html('<span style="color: orange;">⧖ Pending</span>')
    is_graded_display.short_description = 'Graded'
    
    def is_late_display(self, obj):
        if obj.is_late():
            return format_html('<span style="color: red;">✗ Late</span>')
        return format_html('<span style="color: green;">✓ On Time</span>')
    is_late_display.short_description = 'Timeliness'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for Enrollment model"""
    
    list_display = ['student', 'course', 'enrolled_at', 'progress', 'is_active']
    list_filter = ['is_active', 'enrolled_at', 'course']
    search_fields = ['student__username', 'course__title']
    date_hierarchy = 'enrolled_at'
    ordering = ['-enrolled_at']
    
    fieldsets = (
        ('Enrollment Info', {
            'fields': ('student', 'course', 'is_active')
        }),
        ('Progress', {
            'fields': ('progress',)
        }),
    )
    
    readonly_fields = ['enrolled_at']


# Customize admin site
admin.site.site_header = "Simple LMS Administration"
admin.site.site_title = "Simple LMS Admin"
admin.site.index_title = "Welcome to Simple LMS Admin Panel"
