from celery import shared_task
from .models import Transaction, Holding, Account, Stock
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

@shared_task
def process_transaction(data):
    try:
        user = User.objects.get(id=data['user_id'])
        stock = Stock.objects.get(symbol=data['stock_symbol'])
        quantity = data['quantity']
        transaction_type = data['transaction_type']
        price = stock.current_price
        transaction = Transaction.objects.get(id=data['transaction_id'])
        account = Account.objects.get(user=user)

        if transaction_type == 'BUY':
            cost = quantity * price
            if account.balance < cost:
                transaction.status = 'failed'
                transaction.save()
                return {
                    "status": "failed",
                    "reason": "Insufficient balance",
                    "transaction_id": transaction.id
                }

            account.balance -= cost
            account.save()

            holding, created = Holding.objects.get_or_create(
                user=user, stock=stock, defaults={'quantity': quantity}
            )
            if not created:
                holding.quantity += quantity
                holding.save()

        elif transaction_type == 'SELL':
            holding = Holding.objects.filter(user=user, stock=stock).first()
            if not holding or holding.quantity < quantity:
                transaction.status = 'failed'
                transaction.save()
                return {
                    "status": "failed",
                    "reason": "Not enough shares to sell",
                    "transaction_id": transaction.id
                }

            holding.quantity -= quantity
            if holding.quantity == 0:
                holding.delete()
            else:
                holding.save()

            account.balance += quantity * price
            account.save()

        transaction.status = 'completed'
        transaction.save()
        return {
            "status": transaction.status,
            "transaction_id": transaction.id
        }

    except Exception as e:
        if 'transaction' in locals():
            transaction.status = 'failed'
            transaction.save()
        return {
            "status": "failed",
            "reason": str(e),
            "transaction_id": data.get('transaction_id', None)
        }
