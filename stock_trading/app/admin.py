from django.contrib import admin
from .models import Stock, Account, Transaction, Holding

# Register your models here.
admin.site.register(Stock)
admin.site.register(Account)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'stock', 'transaction_type', 'status', 'timestamp')
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Holding)    