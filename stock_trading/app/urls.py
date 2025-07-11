from django.contrib import admin
from django.urls import path
from .views import AddStockView, RegisterView, LogoutView ,StockListView, AccountDetailView, TransactionListCreateView, HoldingListView, get_users
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', get_users.as_view(), name='get-users'),
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('stocks/add/', AddStockView.as_view(), name='add-stock'),
    path('account/', AccountDetailView.as_view(), name='account-detail'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('holdings/', HoldingListView.as_view(), name='holding-list'),
]
