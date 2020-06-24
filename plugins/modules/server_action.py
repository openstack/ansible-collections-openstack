#!/usr/bin/python
# coding: utf-8 -*-

# Copyright (c) 2015, Jesse Keating <jlk@derpops.bike>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: server_action
short_description: Perform actions on Compute Instances from OpenStack
author: OpenStack Ansible SIG
description:
    - Perform server actions on an existing compute instance from OpenStack.
        This module does not return any data other than changed true/false.
        When I(action) is 'rebuild', then I(image) parameter is required.
options:
    server:
        description:
        - Name or ID of the instance
        required: true
        type: str
    wait:
        description:
        - If the module should wait for the instance action to be performed.
        type: bool
        default: 'yes'
    timeout:
        description:
        - The amount of time the module should wait for the instance to perform
            the requested action.
        default: 180
        type: int
    action:
        description:
        - Perform the given action. The lock and unlock actions always return
            changed as the servers API does not provide lock status.
        choices: [stop, start, pause, unpause, lock, unlock, suspend, resume,
                rebuild]
        type: str
        required: true
    image:
        description:
        - Image the server should be rebuilt with
        type: str
    admin_password:
        description:
        - Admin password for server to rebuild
        type: str

requirements:
    - "python >= 3.6"
    - "openstacksdk"

extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
# Pauses a compute instance
- openstack.cloud.server_action:
      action: pause
      auth:
        auth_url: https://identity.example.com
        username: admin
        password: admin
        project_name: admin
      server: vm1
      timeout: 200
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


_action_map = {'stop': 'SHUTOFF',
               'start': 'ACTIVE',
               'pause': 'PAUSED',
               'unpause': 'ACTIVE',
               'lock': 'ACTIVE',  # API doesn't show lock/unlock status
               'unlock': 'ACTIVE',
               'suspend': 'SUSPENDED',
               'resume': 'ACTIVE',
               'rebuild': 'ACTIVE'}

_admin_actions = ['pause', 'unpause', 'suspend', 'resume', 'lock', 'unlock']


class ServerActionModule(OpenStackModule):
    deprecated_names = ('os_server_action', 'openstack.cloud.os_server_action')

    argument_spec = dict(
        server=dict(required=True, type='str'),
        action=dict(required=True, type='str',
                    choices=['stop', 'start', 'pause', 'unpause',
                             'lock', 'unlock', 'suspend', 'resume',
                             'rebuild']),
        image=dict(required=False, type='str'),
        admin_password=dict(required=False, type='str'),
    )
    module_kwargs = dict(
        required_if=[('action', 'rebuild', ['image'])],
        supports_check_mode=True,
    )

    def run(self):
        os_server = self._preliminary_checks()
        self._execute_server_action(os_server)
        # for some reason we don't wait for lock and unlock before exit
        if self.params['action'] not in ('lock', 'unlock'):
            if self.params['wait']:
                self._wait(os_server)
        self.exit_json(changed=True)

    def _preliminary_checks(self):
        # Using Munch object for getting information about a server
        os_server = self.conn.get_server(self.params['server'])
        if not os_server:
            self.fail_json(msg='Could not find server %s' % self.params['server'])
        # check mode
        if self.ansible.check_mode:
            self.exit_json(changed=self.__system_state_change(os_server))
        # examine special cases
        # lock, unlock and rebuild don't depend on state, just do it
        if self.params['action'] not in ('lock', 'unlock', 'rebuild'):
            if not self.__system_state_change(os_server):
                self.exit_json(changed=False)
        return os_server

    def _execute_server_action(self, os_server):
        if self.params['action'] == 'rebuild':
            return self._rebuild_server(os_server)
        action_name = self.params['action'] + "_server"
        try:
            func_name = getattr(self.conn.compute, action_name)
        except AttributeError:
            self.fail_json(
                msg="Method %s wasn't found in OpenstackSDK compute" % action_name)
        func_name(os_server)

    def _rebuild_server(self, os_server):
        # rebuild should ensure images exists
        try:
            image = self.conn.get_image(self.params['image'])
        except Exception as e:
            self.fail_json(
                msg="Can't find the image %s: %s" % (self.params['image'], e))
        if not image:
            self.fail_json(msg="Image %s was not found!" % self.params['image'])
        # admin_password is required by SDK, but not required by Nova API
        if self.params['admin_password']:
            self.conn.compute.rebuild_server(
                server=os_server,
                name=os_server['name'],
                image=image['id'],
                admin_password=self.params['admin_password']
            )
        else:
            self.conn.compute.post(
                '/servers/{server_id}/action'.format(
                    server_id=os_server['id']),
                json={'rebuild': {'imageRef': image['id']}})

    def _wait(self, os_server):
        """Wait for the server to reach the desired state for the given action."""
        # Using Server object for wait_for_server function
        server = self.conn.compute.find_server(self.params['server'])
        self.conn.compute.wait_for_server(
            server,
            status=_action_map[self.params['action']],
            wait=self.params['timeout'])

    def __system_state_change(self, os_server):
        """Check if system state would change."""
        return os_server.status != _action_map[self.params['action']]


def main():
    module = ServerActionModule()
    module()


if __name__ == '__main__':
    main()
