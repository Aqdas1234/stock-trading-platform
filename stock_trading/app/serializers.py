from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Stock, Account, Transaction, Holding, StockPriceHistory
from .tasks import process_transaction

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class StockPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPriceHistory
        fields = ['id', 'price', 'timestamp']

class StockSerializer(serializers.ModelSerializer):
    price_history = StockPriceHistorySerializer(many=True, read_only=True)
    icon = serializers.ImageField(required=False)  # 👈 handle image uploads

    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'icon', 'current_price', 'price_history']

class AccountSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'user', 'balance', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    stock_symbol = serializers.CharField(write_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'stock_symbol', 'transaction_type','status', 'quantity', 'price_per_stock', 'timestamp']
        read_only_fields = ['price_per_stock', 'timestamp']

    def validate(self, data):
        user = self.context['request'].user
        stock = Stock.objects.filter(symbol=data['stock_symbol']).first()
        if not stock:
            raise serializers.ValidationError("Invalid stock symbol.")

        data['stock'] = stock
        data['price_per_stock'] = stock.current_price
        account = Account.objects.get(user=user)

        if data['transaction_type'] == 'BUY':
            cost = data['quantity'] * stock.current_price
            if account.balance < cost:
                raise serializers.ValidationError("Insufficient balance to buy.")
        elif data['transaction_type'] == 'SELL':
            holding = Holding.objects.filter(user=user, stock=stock).first()
            if not holding or holding.quantity < data['quantity']:
                raise serializers.ValidationError("Not enough stock to sell.")
        return data

    def create(self, validated_data):
        user = validated_data['user']
        stock_symbol = validated_data['stock'].symbol
        quantity = validated_data['quantity']
        transaction_type = validated_data['transaction_type']

        transaction = Transaction.objects.create(
        user=user,
        stock=validated_data['stock'],
        transaction_type=transaction_type,
        quantity=quantity,
        price_per_stock=validated_data['price_per_stock'],
        status='pending'
        )
        process_transaction.delay({
            'user_id': user.id,
            'stock_symbol': stock_symbol,
            'transaction_type': transaction_type,
            'quantity': quantity,
            'transaction_id': transaction.id
        })

        return transaction


class HoldingSerializer(serializers.ModelSerializer):
    stock = StockSerializer()

    class Meta:
        model = Holding
        fields = ['id', 'stock', 'quantity']
