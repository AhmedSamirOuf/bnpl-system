from django.test import TestCase
from django.contrib.auth import get_user_model

class UserModelTest(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email='test@user.com',
            password='testpass',
            role='user'
        )
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_superuser)