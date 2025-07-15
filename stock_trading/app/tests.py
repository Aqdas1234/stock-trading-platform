import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Account, Stock, Transaction, Holding
from django.conf import settings

from unittest.mock import patch



@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.skipif(not settings.TESTING, reason="Requires Redis")
def test_that_needs_redis():
    pass

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def auth_client(user, api_client):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
def test_register_view(api_client):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123"
    }
    response = api_client.post('/register/', data)
    assert response.status_code == 201
    assert User.objects.filter(username="newuser").exists()

@pytest.mark.django_db
def test_account_create_view(auth_client, user):
    data = {"balance": 10000}
    response = auth_client.post("/account/create/", data)
    assert response.status_code == 201
    assert Account.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_account_retrieve_view(auth_client, user):
    Account.objects.create(user=user, balance=5000)
    response = auth_client.get("/account/")
    assert response.status_code == 200
    assert response.data["balance"] == "5000.00"

@pytest.mark.django_db
def test_stock_create_and_list(auth_client):
    data = {"symbol": "AAPL", "name": "Apple Inc.", "current_price": 150}
    response = auth_client.post("/stocks/", data)
    assert response.status_code == 201
    list_response = auth_client.get("/stocks/")
    assert list_response.status_code == 200
    # Check if response is paginated
    if 'results' in list_response.data:
        stocks = list_response.data['results']
    else:
        stocks = list_response.data
        
    assert any(stock["symbol"] == "AAPL" for stock in stocks)

@pytest.mark.django_db
@patch('app.tasks.process_transaction.delay')
def test_transaction_list_create(mock_task,auth_client, user):
    mock_task.return_value = None 
    stock = Stock.objects.create(symbol="TSLA", name="Tesla", current_price=100)
    Account.objects.create(user=user, balance=10000)

    transaction_data = {
        "stock_symbol": "TSLA",
        "transaction_type": "BUY",
        "quantity": 5
    }
    response = auth_client.post("/transactions/", transaction_data)
    assert response.status_code in [200, 201]

    list_response = auth_client.get("/transactions/")
    assert list_response.status_code == 200


@pytest.mark.django_db
def test_holding_list_view(auth_client, user):
    # Setup
    stock = Stock.objects.create(
        symbol="GOOG",
        name="Google",
        current_price=100.00
    )
    Holding.objects.create(
        user=user,
        stock=stock,
        quantity=10
    )

    response = auth_client.get("/holdings/", format='json')
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'
    
    response_data = response.json()
    assert isinstance(response_data, dict), "Expected paginated response"
    assert 'results' in response_data, "Expected paginated results"
    assert isinstance(response_data['results'], list), "Expected list in results"
    
    holdings = response_data['results']
    assert len(holdings) > 0
