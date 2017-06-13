
import unittest
from app.models import Role, Permission, User, AnonymousUser


class UserModelTestCase(unittest.TestCase): # ...
    def setUp(self):
        self.role = Role(name='test')

    def test_role_is_default_false(self):
        self.assertFalse(self.role.is_default)

    def tearDown(self):
        pass

    def test_roles_permissions_is_list(self):
        self.assertTrue(isinstance(self.role.permissions, list))

    def test_roles_and_permissions(self):
        u = User(password='cat')
        self.assertTrue(u.can(['read']))
        self.assertFalse(u.can(['admin']))

    def test_anonymous_can_not_admin(self):
        u = AnonymousUser()
        self.assertFalse(u.can(['admin']))

    # @unittest.skip('WIP')
    def test_set_url_raises_error(self):
        with self.assertRaises(AttributeError):
            self.role.url = 'some_url'

