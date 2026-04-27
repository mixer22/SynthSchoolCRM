from apps.students.models import Experience, ExperienceLog


def add_xp(user, amount, reason=""):
    xp_obj, _ = Experience.objects.get_or_create(user=user)

    xp_obj.total_xp += amount
    xp_obj.save()

    ExperienceLog.objects.create(
        user=user,
        amount=amount,
        reason=reason
    )

    return xp_obj