from apps.students.models import CoinBalance, Transaction


def add_coins(user, amount, comment=""):
    """
    Начисление монет пользователю
    """
    if amount <= 0:
        raise ValueError("Amount must be positive")

    balance = CoinBalance.get_for_user(user)
    balance.balance += amount
    balance.save()

    Transaction.objects.create(
        user=user,
        amount=amount,
        comment=comment,
        type='add'
    )


def remove_coins(user, amount, comment=""):
    """
    Списание монет у пользователя
    """
    if amount <= 0:
        raise ValueError("Amount must be positive")

    balance = CoinBalance.get_for_user(user)
    balance.balance -= amount
    balance.save()

    Transaction.objects.create(
        user=user,
        amount=amount,
        comment=comment,
        type='remove'
    )