from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Stock, Account, Transaction, Holding

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


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
        stock = validated_data['stock']
        quantity = validated_data['quantity']
        account = Account.objects.get(user=user)
        price = validated_data['price_per_stock']

        if validated_data['transaction_type'] == 'BUY':
            # deduct balance
            account.balance -= quantity * price
            account.save()

            # update holding
            holding, created = Holding.objects.get_or_create(user=user, stock=stock)
            holding.quantity += quantity
            holding.save()

        elif validated_data['transaction_type'] == 'SELL':
            # add balance
            account.balance += quantity * price
            account.save()

            # update holding
            holding = Holding.objects.get(user=user, stock=stock)
            holding.quantity -= quantity
            if holding.quantity == 0:
                holding.delete()
            else:
                holding.save()

        return Transaction.objects.create(**validated_data)


class HoldingSerializer(serializers.ModelSerializer):
    stock = StockSerializer()

    class Meta:
        model = Holding
        fields = ['id', 'stock', 'quantity']
