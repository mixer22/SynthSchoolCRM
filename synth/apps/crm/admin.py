from django.contrib import admin

from apps.students.models import (
    StudentProfile,
    Enrollment,
    Experience,
    ExperienceLog,
    Transaction,
    Subscription,
    Attendance
)

from apps.schedule.models import Group, Lesson
from apps.users.models import User


admin.site.register(User)

admin.site.register(StudentProfile)
admin.site.register(Enrollment)

admin.site.register(Experience)
admin.site.register(ExperienceLog)
admin.site.register(Transaction)
admin.site.register(Subscription)
admin.site.register(Attendance)

admin.site.register(Group)
admin.site.register(Lesson)