from django.contrib import admin
from django.urls import path
from .views import  (RegisterView, LogoutView ,CustomTokenObtainPairView,StockListCreateView, 
                    AccountCreateView,UserMeView, TransactionListCreateView, HoldingListView, 
                    GetUsers, StockDetailView,AccountRetrieveUpdateDestroyView,StockPriceHistoryView)
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', GetUsers.as_view(), name='get-users'),
    path('stocks/', StockListCreateView.as_view(), name='stock-list'),
    path('stocks/<int:pk>/', StockDetailView.as_view(), name='stock-detail'),
    path('account/create/', AccountCreateView.as_view(), name='account-detail'),
    path('account/', AccountRetrieveUpdateDestroyView.as_view(), name='account-retrieve-update-destroy'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('holdings/', HoldingListView.as_view(), name='holding-list'),
    path('user/me/', UserMeView.as_view(), name='user-me'), 
    path('stock-history/', StockPriceHistoryView.as_view(), name='stock-price-history'),
]
