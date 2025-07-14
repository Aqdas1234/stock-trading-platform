from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegisterSerializer,StockSerializer, AccountSerializer, TransactionSerializer, HoldingSerializer
from rest_framework.views import APIView
from .models import Stock, Account, Transaction, Holding
from rest_framework.generics import RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class get_users(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

class StockListView(generics.ListCreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['symbol', 'name']



class StockDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]



class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Account, user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)           


class AccountCreateView(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    

class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class HoldingListView(generics.ListAPIView):
    serializer_class = HoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)