from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from users.models import User
from users.services import fetch_random_users
from unittest.mock import patch, Mock
from django.db import transaction
import logging
from django.db import IntegrityError

logger = logging.getLogger(__name__)


class UserModelTest(TestCase):
    def test_user_creation(self):
        """Test user creation."""
        user = User.objects.create(
            gender="male",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="123-456",
            location="New York",
            picture="john.jpg"
        )
        self.assertEqual(user.get_more_info(), reverse('users:user_detail', args=[user.id]))
        self.assertEqual(str(user), reverse('users:user_detail', args=[user.id]))


class FetchRandomUsersTest(TestCase):
    def setUp(self):
        self.mock_response_data = {
            "results": [
                {
                    "gender": "female",
                    "name": {"first": "Jane", "last": "Smith"},
                    "phone": "1234567890",
                    "email": "jane.smith@example.com",
                    "location": {"city": "London"},
                    "picture": {"medium": "jane.jpg"}
                },
                {
                    "gender": "male",
                    "name": {"first": "Bob", "last": "Jones"},
                    "phone": "0987654321",
                    "email": "bob.jones@example.com",
                    "location": {"city": "Paris"},
                    "picture": {"medium": "bob.jpg"}
                }
            ]
        }

    @patch("users.services.requests.get")
    def test_fetch_random_users_success(self, mock_get):
        """Test fetch_random_users() with successful API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fetch_random_users(count=2)
        self.assertEqual(User.objects.count(), 2)
        user1 = User.objects.get(email="jane.smith@example.com")
        self.assertEqual(user1.first_name, "Jane")
        self.assertEqual(user1.location, "London")

class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            gender="male",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="123-456",
            location="New York",
            picture="john.jpg"
        )

    def test_user_list_view(self):
        """Test user list view page."""
        response = self.client.get('/')
        self.assertContains(response, "Test")
        self.assertContains(response, "User")
        
    def test_user_detail_view(self):
        """Test user detail view page."""
        response = self.client.get(f'/{self.user.id}/')
        self.assertContains(response, "test@example.com")

    @patch('users.views.choice')
    def test_random_user_view(self, mock_choice):
        """Test random page."""
        mock_choice.return_value = self.user
        response = self.client.get('/random/')
        self.assertContains(response, "Test User")
        self.assertContains(response, "test@example.com")
        self.assertContains(response, "123-456")
        self.assertContains(response, "New York")
        self.assertContains(response, "john.jpg")

    @patch("users.views.fetch_random_users")
    def test_load_users_view_success(self, mock_fetch):
        """Test creating new users via form."""
        def side_effect(count):
            for i in range(count):
                User.objects.create(
                    gender="female",
                    first_name=f"User{i}",
                    last_name="Test",
                    email=f"user{i}@example.com",
                    phone=f"123456789{i}",
                    location="Test City",
                    picture="test.jpg"
                )
        mock_fetch.side_effect = side_effect
        cache.clear()
        initial_user_count = User.objects.count()
        response = self.client.post(
            reverse("users:load_users"),
            {"count": "5"},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("users:user_list") + "?page=1", 302)])

        mock_fetch.assert_called_with(5)

        self.assertEqual(User.objects.count(), initial_user_count + 5)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "5 пользователей загружено.")

        cache_key = "user_list_page_1"
        self.assertIsNotNone(cache.get(cache_key))

