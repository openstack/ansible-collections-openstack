#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 OpenStack Ansible SIG
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: host_aggregate_info
short_description: Fetch OpenStack host aggregates
author: OpenStack Ansible SIG
description:
  - Fetch OpenStack host aggregates.
options:
  name:
    description:
      - Name or ID of the aggregate.
      - Returns only the matching aggregate when set.
    type: str
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = r'''
- name: Fetch all host aggregates
  openstack.cloud.host_aggregate_info:
    cloud: mycloud

- name: Fetch a specific host aggregate by name
  openstack.cloud.host_aggregate_info:
    cloud: mycloud
    name: db_aggregate
'''

RETURN = r'''
aggregates:
  description: List of dictionaries describing host aggregates.
  returned: always
  type: list
  elements: dict
  contains:
    availability_zone:
      description: Availability zone of the aggregate.
      type: str
    created_at:
      description: The date and time when the resource was created.
      type: str
    deleted_at:
      description: The date and time when the resource was deleted.
      type: str
    hosts:
      description: List of hosts belonging to the aggregate.
      type: list
      elements: str
    id:
      description: The UUID of the aggregate.
      type: str
    is_deleted:
      description: Whether or not the resource is deleted.
      type: bool
    metadata:
      description: Metadata attached to the aggregate.
      type: dict
    name:
      description: Name of the aggregate.
      type: str
    updated_at:
      description: The date and time when the resource was updated.
      type: str
    uuid:
      description: UUID of the aggregate.
      type: str
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class ComputeHostAggregateInfoModule(OpenStackModule):
    argument_spec = dict(
        name=dict(),
    )

    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        name = self.params['name']

        if name:
            aggregate = self.conn.compute.find_aggregate(name)
            aggregates = [aggregate] if aggregate else []
        else:
            aggregates = list(self.conn.compute.aggregates())

        self.exit_json(changed=False,
                       aggregates=[a.to_dict(computed=False)
                                   for a in aggregates])


def main():
    module = ComputeHostAggregateInfoModule()
    module()


if __name__ == '__main__':
    main()
