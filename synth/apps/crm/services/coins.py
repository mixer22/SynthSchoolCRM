from apps.students.models import CoinBalance, Transaction

def add_coins(user, amount, comment=""):
    balance, _ = CoinBalance.objects.get_or_create(user=user)

    balance.balance += amount
    balance.save()

    Transaction.objects.create(
        user=user,
        amount=amount,
        comment=comment
    )