#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: server_info
short_description: Retrieve information about one or more compute instances
author: OpenStack Ansible SIG
description:
    - Retrieve information about server instances from OpenStack.
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

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class ServerInfoModule(OpenStackModule):

    argument_spec = dict(
        server=dict(),
        detailed=dict(type='bool', default=False),
        filters=dict(type='dict'),
        all_projects=dict(type='bool', default=False),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):

        kwargs = self.check_versioned(
            detailed=self.params['detailed'],
            filters=self.params['filters'],
            all_projects=self.params['all_projects']
        )
        if self.params['server']:
            kwargs['name_or_id'] = self.params['server']
        openstack_servers = self.conn.search_servers(**kwargs)
        self.exit(changed=False, openstack_servers=openstack_servers)


def main():
    module = ServerInfoModule()
    module()


if __name__ == '__main__':
    main()
