from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class PerfilTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.client.login(email='test@example.com', password='password123')

    def test_perfil_view_status_code(self):
        url = reverse('perfil_usuario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
