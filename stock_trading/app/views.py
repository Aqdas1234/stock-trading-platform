from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions,status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import (RegisterSerializer,StockSerializer, AccountSerializer, TransactionSerializer,
                           HoldingSerializer, StockPriceHistorySerializer, AddBalanceSerializer)
from rest_framework.views import APIView
from .models import Stock, Account, Transaction, Holding, StockPriceHistory
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from datetime import timedelta
from rest_framework.parsers import MultiPartParser, FormParser

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

class GetUsers(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

class StockListCreateView(generics.ListCreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['symbol', 'name']  
    search_fields = ['symbol', 'name']    
    ordering_fields = ['symbol', 'current_price', 'name']  
    ordering = ['id'] 


class StockDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        instance = self.get_object()
        old_price = instance.current_price
        updated_instance = serializer.save()

        if old_price != updated_instance.current_price:
            StockPriceHistory.objects.create(
                stock=updated_instance,
                price=updated_instance.current_price
            )



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

class AddBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddBalanceSerializer(data=request.data)
        if serializer.is_valid():
            balance = serializer.validated_data['balance']
            account = Account.objects.get(user=request.user)
            account.balance += balance
            account.save()

            return Response({
                'message': 'Balance added successfully.',
                'new_balance': account.balance
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'stock__symbol','status']
    search_fields = ['stock__symbol']
    ordering_fields = ['timestamp', 'price_per_stock', 'quantity']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class HoldingListView(generics.ListAPIView):
    serializer_class = HoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)
    
class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
        })
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({"detail": "Invalid credentials"}, status=401)
        access = serializer.validated_data['access']
        refresh = serializer.validated_data['refresh']
        response = Response({"access": access})
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False, 
            samesite='Lax', 
            max_age=7*24 * 60 * 60, 
        )

        return response


class StockPriceHistoryView(generics.ListAPIView):
    serializer_class = StockPriceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        symbol = self.request.query_params.get('symbol')
        hours = self.request.query_params.get('hours')
        days = self.request.query_params.get('days')
        months = self.request.query_params.get('months')

        queryset = StockPriceHistory.objects.all()

        # Filter by stock symbol (you could also allow filtering by ID)
        if symbol:
            queryset = queryset.filter(stock__symbol=symbol)

        # Filter by time range
        now = timezone.now()
        if hours:
            queryset = queryset.filter(timestamp__gte=now - timedelta(hours=int(hours)))
        elif days:
            queryset = queryset.filter(timestamp__gte=now - timedelta(days=int(days)))
        elif months:
            queryset = queryset.filter(timestamp__gte=now - timedelta(days=30 * int(months)))

        return queryset



class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'detail': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'detail': 'Token invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)