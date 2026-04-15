from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Роли пользователей
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin')
    ]

    # ====== Основные данные ======
    age = models.PositiveIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    # ====== CRM-ДАННЫЕ ======
    notes = models.TextField(blank=True, null=True)  # заметки преподавателя

    created_at = models.DateTimeField(auto_now_add=True)

    def is_student(self):
        return self.role == 'student'

    def is_teacher(self):
        return self.role == 'teacher'

    def __str__(self):
        return self.username