from celery import shared_task
from .models import Transaction, Holding, Account, Stock
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def process_transaction(data):
    user = User.objects.get(id=data['user_id'])
    stock = Stock.objects.get(symbol=data['stock_symbol'])
    quantity = data['quantity']
    transaction_type = data['transaction_type']
    price = stock.current_price

    account = Account.objects.get(user=user)

    if transaction_type == 'BUY':
        account.balance -= quantity * price
        account.save()
        holding, created = Holding.objects.get_or_create(user=user, stock=stock)
        holding.quantity += quantity
        holding.save()

    elif transaction_type == 'SELL':
        account.balance += quantity * price
        account.save()
        holding = Holding.objects.get(user=user, stock=stock)
        holding.quantity -= quantity
        if holding.quantity == 0:
            holding.delete()
        else:
            holding.save()

    Transaction.objects.create(
        user=user,
        stock=stock,
        transaction_type=transaction_type,
        quantity=quantity,
        price_per_stock=price,
        status='completed'
    )
