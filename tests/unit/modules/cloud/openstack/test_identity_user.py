import unittest
from unittest import mock

from ansible_collections.openstack.cloud.plugins.modules import identity_user
from ansible_collections.openstack.cloud.tests.unit.modules.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    set_module_args,
)


class FakeUser(dict):
    '''A dict-like stand-in for an openstacksdk identity.v3.user.User.'''

    def to_dict(self, computed=False):
        return dict(self)


class FakeSDK(object):
    class exceptions:
        class OpenStackCloudException(Exception):
            pass


class TestIdentityUser(ModuleTestCase):

    def _run_module(self, module_args, identity):
        set_module_args(module_args)
        conn = mock.Mock()
        conn.identity = identity
        with mock.patch.object(
            identity_user.IdentityUserModule,
            'openstack_cloud_from_module',
            return_value=(FakeSDK(), conn),
        ):
            identity_user.main()

    def _new_identity(self, existing_user=None):
        identity = mock.Mock()
        if existing_user is None:
            identity.find_user.return_value = None
        else:
            identity.find_user.return_value = existing_user
            identity.get_user.return_value = existing_user
        return identity

    # -- create -----------------------------------------------------------

    def test_create_user_with_options(self):
        identity = self._new_identity(existing_user=None)
        identity.create_user.return_value = FakeUser(
            id='1', name='demouser', is_enabled=True,
            options={'ignore_password_expiry': True,
                     'ignore_change_password_upon_first_use': True},
        )

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({
                'name': 'demouser',
                'options': {
                    'ignore_password_expiry': True,
                    'ignore_change_password_upon_first_use': True,
                },
            }, identity)

        result = ex.exception.args[0]
        self.assertTrue(result['changed'])
        identity.create_user.assert_called_once()
        _, kwargs = identity.create_user.call_args
        self.assertEqual(
            {'ignore_password_expiry': True,
             'ignore_change_password_upon_first_use': True},
            kwargs['options'])
        identity.update_user.assert_not_called()

    def test_create_user_without_options(self):
        identity = self._new_identity(existing_user=None)
        identity.create_user.return_value = FakeUser(
            id='1', name='demouser', is_enabled=True, options={})

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({'name': 'demouser'}, identity)

        result = ex.exception.args[0]
        self.assertTrue(result['changed'])
        identity.create_user.assert_called_once()
        _, kwargs = identity.create_user.call_args
        self.assertNotIn('options', kwargs)

    # -- update -----------------------------------------------------------

    def _existing_user(self, **options):
        return FakeUser(
            id='1', name='demouser', is_enabled=True, options=options)

    def test_update_user_options_idempotent(self):
        user = self._existing_user(
            ignore_password_expiry=True,
            ignore_change_password_upon_first_use=True,
        )
        identity = self._new_identity(existing_user=user)

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({
                'name': 'demouser',
                'options': {
                    'ignore_password_expiry': True,
                    'ignore_change_password_upon_first_use': True,
                },
            }, identity)

        result = ex.exception.args[0]
        self.assertFalse(result['changed'])
        identity.update_user.assert_not_called()

    def test_update_user_options_change(self):
        user = self._existing_user(ignore_password_expiry=False)
        identity = self._new_identity(existing_user=user)
        identity.update_user.return_value = FakeUser(
            id='1', name='demouser', is_enabled=True,
            options={'ignore_password_expiry': True})

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({
                'name': 'demouser',
                'options': {'ignore_password_expiry': True},
            }, identity)

        result = ex.exception.args[0]
        self.assertTrue(result['changed'])
        identity.update_user.assert_called_once_with(
            '1', options={'ignore_password_expiry': True})

    def test_update_user_options_merge_preserves_existing(self):
        user = self._existing_user(
            lock_password=True,
            ignore_password_expiry=False,
        )
        identity = self._new_identity(existing_user=user)
        identity.update_user.return_value = FakeUser(
            id='1', name='demouser', is_enabled=True,
            options={'lock_password': True, 'ignore_password_expiry': True})

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({
                'name': 'demouser',
                'options': {'ignore_password_expiry': True},
            }, identity)

        result = ex.exception.args[0]
        self.assertTrue(result['changed'])
        identity.update_user.assert_called_once_with(
            '1',
            options={'lock_password': True, 'ignore_password_expiry': True})

    def test_update_user_without_options_preserves_existing(self):
        # When no options are specified, existing options must not be touched.
        user = self._existing_user(ignore_password_expiry=True)
        identity = self._new_identity(existing_user=user)

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({'name': 'demouser'}, identity)

        result = ex.exception.args[0]
        self.assertFalse(result['changed'])
        identity.update_user.assert_not_called()


if __name__ == '__main__':
    unittest.main()
