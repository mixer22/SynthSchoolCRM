from apps.students.models import Enrollment


def add_student_to_group(student, group):
    return Enrollment.objects.get_or_create(
        student=student,
        group=group
    )


def remove_student_from_group(student, group):
    return Enrollment.objects.filter(
        student=student,
        group=group
    ).delete()