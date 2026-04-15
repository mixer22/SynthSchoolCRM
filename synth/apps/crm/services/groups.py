from apps.students.models import Enrollment


def add_user_to_group(user, group):
    Enrollment.objects.get_or_create(user=user, group=group)


def remove_user_from_group(user_id, group_id):
    Enrollment.objects.filter(user_id=user_id, group_id=group_id).delete()