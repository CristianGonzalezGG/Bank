from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from .models import Client, Account

# Create your tests here.

class ClientModelTest(TestCase):
    def setUp(self):
        self.test_client = Client.objects.create(
            name="Test Client",
            email="test@example.com",
            phone_number="1234567890",
            address="123 Test St"
        )
        self.account = Account.objects.create(
            client=self.test_client,
            numberAccount="1234567890"
        )

    # Este método prueba la creación del cliente
    def test_client_creation(self):
        self.assertEqual(self.test_client.name, "Test Client")
        self.assertEqual(self.test_client.email, "test@example.com")
        self.assertEqual(self.test_client.get_account_number(), "1234567890")

    # Este método prueba la creación de la cuenta
    def test_account_creation(self):
        self.assertEqual(self.account.client.name, "Test Client")
        self.assertEqual(self.account.numberAccount, "1234567890")

class ClientViewTest(TestCase):
    # Este método crea un cliente y una cuenta para las pruebas
    def setUp(self):
        self.test_client = Client.objects.create(
            name="Test Client",
            email="test@example.com",
            phone_number="1234567890",
            address="123 Test St"
        )
        self.account = Account.objects.create(
            client=self.test_client,
            numberAccount="1234567890"
        )

    # Este método prueba la vista de lista de clientes
    def test_client_list_view(self):
        response = self.client.get(reverse('blog:client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Client")

    # Este método prueba la vista de detalle del cliente
    def test_client_detail_view(self):
        response = self.client.get(reverse('blog:client_detail', args=[self.test_client.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Client")
        self.assertContains(response, "1234567890")