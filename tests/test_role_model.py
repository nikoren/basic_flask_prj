
import unittest
from app.models import Role, Permission, User, AnonymousUser


class UserModelTestCase(unittest.TestCase): # ...

    def test_roles_and_permissions(self):
        Role.insert_cfg_roles()
        u = User(password='cat')
        self.assertTrue(u.can(['read']))
        self.assertFalse(u.can(['admin']))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(['admin']))