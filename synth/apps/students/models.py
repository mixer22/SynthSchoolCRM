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
                fields=['student', 'group'],
                name='unique_enrollment'
            )
        ]
        verbose_name = "Запись"
        verbose_name_plural = "Записи"


# =========================
# SUBSCRIPTION (АБОНЕМЕНТ)
# =========================
class Subscription(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    total_lessons = models.PositiveIntegerField()
    used_lessons = models.PositiveIntegerField(default=0)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def remaining_lessons(self):
        return self.total_lessons - self.used_lessons

    def __str__(self):
        return f"{self.student.user.username} ({self.remaining_lessons()} left)"


# =========================
# COIN BALANCE
# =========================
class CoinBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coin_balance"
    )

    balance = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Кошелек"
        verbose_name_plural = "Кошельки"

    @staticmethod
    def get_for_user(user):
        obj, _ = CoinBalance.objects.get_or_create(user=user)
        return obj

    @staticmethod
    def add_coins(user, amount, reason=""):
        balance = CoinBalance.get_for_user(user)
        balance.balance += amount
        balance.save()

        Transaction.objects.create(
            user=user,
            amount=amount,
            comment=reason,
            type='add'
        )


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
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"


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
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    is_paid = models.BooleanField(default=False)

    comment = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'lesson'],
                name='unique_student_lesson_attendance'
            )
        ]

        verbose_name = "Посещение"
        verbose_name_plural = "Посещения"

    def __str__(self):
        return f"{self.student.user.username} - {self.lesson} ({self.status})"

    # =========================
    # BUSINESS LOGIC
    # =========================

    def is_debt(self):
        return self.subscription is None

    def mark_paid(self):
        self.is_paid = True
        self.save()