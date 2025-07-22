from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='stock_icons/', blank=True, null=True)  
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class StockPriceHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.stock.symbol} - {self.price} at {self.timestamp}"

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['user']
    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    TRANSACTION_STATUS = (
        ('PENDING', 'pending'),
        ('COMPLETED', 'completed'),
        ('FAILED', 'failed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20,choices=TRANSACTION_STATUS,default='PENDING')  # PENDING, COMPLETED, FAILED
    price_per_stock = models.DecimalField(max_digits=10, decimal_places=2) 
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-timestamp']
        unique_together = ('user', 'stock', 'timestamp') 
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} {self.quantity} of {self.stock.symbol} at {self.price_per_stock}"

class Holding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ['user', 'stock']
        unique_together = ('user', 'stock')  # Prevent duplicate holding
    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol} ({self.quantity})"