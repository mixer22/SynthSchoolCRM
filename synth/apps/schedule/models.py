from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

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

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=WEEKDAYS)
    time = models.TimeField()

    def __str__(self):
        return f"{self.group} {self.get_weekday_display()} {self.time.strftime('%H:%M')}"

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"