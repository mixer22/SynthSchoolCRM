from django.db import models
from django.conf import settings


# =========================
# STUDENT PROFILE
# =========================
class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    age = models.PositiveIntegerField(null=True, blank=True)

    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# =========================
# ENROLLMENT
# =========================
class Enrollment(models.Model):
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    group = models.ForeignKey(
        'schedule.Group',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student'],
                name='one_group_per_student'  # 🔥 ученик только в одной группе
            )
        ]

    def __str__(self):
        return f"{self.student} → {self.group}"


# =========================
# SUBSCRIPTION (АБОНЕМЕНТ)
# =========================
class Subscription(models.Model):
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    title = models.CharField(max_length=100, blank=True)

    total_lessons = models.PositiveIntegerField()
    used_lessons = models.PositiveIntegerField(default=0)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    # =========================
    # 🔢 CORE LOGIC
    # =========================

    def raw_balance(self):
        return self.total_lessons - self.used_lessons

    def remaining_lessons(self):
        return max(self.raw_balance(), 0)

    def debt(self):
        return max(-self.raw_balance(), 0)

    def is_exhausted(self):
        return self.raw_balance() <= 0

    def use_lesson(self):
        self.used_lessons += 1
        self.save()
        return True

    # =========================
    # 📊 AGGREGATION
    # =========================

    @staticmethod
    def get_total_debt(student):
        subs = student.subscriptions.filter(is_active=True)

        return sum(sub.debt() for sub in subs)

    def __str__(self):
        return f"{self.student} | {self.remaining_lessons()} left"
# =========================
# Experience
# =========================
class Experience(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="xp"
    )

    total_xp = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_for_user(cls, user):
        obj, _ = cls.objects.get_or_create(user=user)
        return obj

    # ===== ЛОГИКА =====

    def add_xp(self, amount):
        self.total_xp += amount
        self.save()

    def get_level(self):
        return self.total_xp // 1000

    def get_progress(self):
        return self.total_xp % 1000

    def __str__(self):
        return f"{self.user} | {self.total_xp} XP"

class ExperienceLog(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    amount = models.IntegerField()

    reason = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} +{self.amount} XP ({self.reason})"
# =========================
# TRANSACTION
# =========================
class Transaction(models.Model):
    TYPE_CHOICES = [
        ('add', 'Add'),
        ('remove', 'Remove'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='add')

    amount = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.amount} ({self.type})"
# =========================
# ATTENDANCE (ПОСЕЩАЕМОСТЬ)
# =========================
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ('late', 'Опоздал'),
        ('excused', 'Уважительная причина'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    lesson = models.ForeignKey(
        'schedule.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances'
    )

    date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    comment = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    is_paid = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'lesson', 'date'],
                name='unique_student_lesson_date'
            )
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.user.username} - {self.date} ({self.status})"