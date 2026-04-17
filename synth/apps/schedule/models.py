from django.db import models


# =========================
# GROUP
# =========================
class Group(models.Model):
    name = models.CharField(max_length=100)

    teacher = models.ForeignKey(
        'teachers.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


# =========================
# LESSON
# =========================
class Lesson(models.Model):
    WEEKDAYS = [
        (0, "ПН"),
        (1, "ВТ"),
        (2, "СР"),
        (3, "ЧТ"),
        (4, "ПТ"),
        (5, "СБ"),
        (6, "ВС"),
    ]

    group = models.OneToOneField(Group, on_delete=models.CASCADE)

    weekday = models.IntegerField(choices=WEEKDAYS)
    time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        ordering = ['weekday', 'time']

        constraints = [
            models.UniqueConstraint(
                fields=['group', 'weekday', 'time'],
                name='unique_group_lesson_slot'
            )
        ]

    def __str__(self):
        return f"{self.group.name} {self.get_weekday_display()} {self.time.strftime('%H:%M')}"