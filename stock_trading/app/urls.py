from django.contrib import admin
from django.urls import path
from .views import  RegisterView, LogoutView ,StockListView, AccountCreateView, TransactionListCreateView, HoldingListView, get_users, StockDetailView,AccountRetrieveUpdateDestroyView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', get_users.as_view(), name='get-users'),
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('stocks/<int:pk>/', StockDetailView.as_view(), name='stock-detail'),
    path('account/create/', AccountCreateView.as_view(), name='account-detail'),
    path('account/', AccountRetrieveUpdateDestroyView.as_view(), name='account-retrieve-update-destroy'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('holdings/', HoldingListView.as_view(), name='holding-list'),
]
