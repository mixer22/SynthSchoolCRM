from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from ..schedule.models import Group

User = get_user_model()

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'group'], name='unique_enrollment')
        ]
        verbose_name = "Запись"
        verbose_name_plural = "Записи"


class CoinBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Кошелек"
        verbose_name_plural = "Кошельки"

    @staticmethod
    def add_coins(user, amount, reason=""):
        balance, _ = CoinBalance.objects.get_or_create(user=user)

        balance.balance += amount
        balance.save()

        Transaction.objects.create(
            user=user,
            amount=amount,
            comment=reason
        )


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"