#!/usr/bin/python

# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: server_info
short_description: Retrieve information about one or more compute instances
author: Monty (@emonty)
description:
    - Retrieve information about server instances from OpenStack.
    - This module was called C(openstack.cloud.server_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(openstack.cloud.server_info) module no longer returns C(ansible_facts)!
notes:
    - The result contains a list of servers.
options:
   server:
     description:
       - restrict results to servers with names or UUID matching
         this glob expression (e.g., <web*>).
     type: str
   detailed:
     description:
        - when true, return additional detail about servers at the expense
          of additional API calls.
     type: bool
     default: 'no'
   filters:
     description:
        - restrict results to servers matching a dictionary of
          filters
     type: dict
   all_projects:
     description:
       - Whether to list servers from all projects or just the current auth
         scoped project.
     type: bool
     default: 'no'
requirements:
    - "python >= 3.6"
    - "openstacksdk"

extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
# Gather information about all servers named <web*> that are in an active state:
- openstack.cloud.server_info:
    cloud: rax-dfw
    server: web*
    filters:
      vm_state: active
  register: result
- debug:
    msg: "{{ result.openstack_servers }}"
'''

import fnmatch

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class ServerInfoModule(OpenStackModule):

    argument_spec = dict(
        server=dict(required=False),
        detailed=dict(required=False, type='bool', default=False),
        filters=dict(required=False, type='dict', default=None),
        all_projects=dict(required=False, type='bool', default=False),
    )

    def run(self):
        is_old_facts = self._name == 'openstack.cloud.server_facts'
        if is_old_facts:
            self.deprecate("The 'openstack.cloud.server_facts' module has been renamed to 'openstack.cloud.server_info', "
                           "and the renamed one no longer returns ansible_facts", version='2.13')
        openstack_servers = self.conn.search_servers(
            detailed=self.params['detailed'], filters=self.params['filters'],
            all_projects=self.params['all_projects'])

        if self.params['server']:
            # filter servers by name
            pattern = self.params['server']
            # TODO(mordred) This is handled by sdk now
            openstack_servers = [server for server in openstack_servers
                                 if fnmatch.fnmatch(server['name'], pattern)
                                 or fnmatch.fnmatch(server['id'], pattern)]
        if is_old_facts:
            self.exit_json(changed=False, ansible_facts=dict(
                openstack_servers=openstack_servers))
        else:
            self.exit_json(changed=False, openstack_servers=openstack_servers)


def main():
    module = ServerInfoModule()
    module()


if __name__ == '__main__':
    main()
