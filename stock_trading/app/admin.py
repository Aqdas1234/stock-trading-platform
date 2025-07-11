from django.contrib import admin
from .models import Stock, Account, Transaction, Holding

# Register your models here.
admin.site.register(Stock)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Holding)    