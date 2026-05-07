from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTestCase(TestCase):
    def test_create_admin(self):
        admin = User.objects.create_user(
            username="admin1",
            password="123456",
            role="admin"
        )
        self.assertEqual(admin.role, "admin")

    def test_create_professor(self):
        prof = User.objects.create_user(
            username="prof1",
            password="123456",
            role="prof"
        )
        self.assertEqual(prof.role, "prof")
