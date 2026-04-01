#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Boehringer Ingelheim
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: compute_service
short_description: Update OpenStack Compute (Nova) services
author: OpenStack Ansible SIG
description:
  - Update OpenStack Compute (Nova) service properties.
options:
  host:
    description:
      - Compute host name
    type: str
    required: true
  binary:
    description:
      - Binary name of the service (e.g. C(nova-compute)).
    type: str
    required: true
  status:
    description:
      - Desired status of the service.
    type: str
    choices: ['enabled', 'disabled']
    default: enabled
  disabled_reason:
    description:
      - Reason for disabling the service. Should be used with state `disabled`.
    type: str
version_added: 2.6.0
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = r'''
- name: Disable nova-compute on node1
  openstack.cloud.compute_service:
    cloud: awesomecloud
    host: node1
    binary: nova-compute
    status: disabled

- name: Enable nova-compute on node1
  openstack.cloud.compute_service:
    cloud: awesomecloud
    host: node1
    binary: nova-compute
    status: enabled
'''

RETURN = r'''
compute_services:
  description: List of dictionaries describing Compute (Nova) services.
  returned: always
  type: list
  elements: dict
  contains:
    availability_zone:
      description: The availability zone name.
      type: str
    binary:
      description: The binary name of the service.
      type: str
    disabled_reason:
      description: The reason why the service is disabled
      type: str
    id:
      description: Unique UUID.
      type: str
    is_forced_down:
      description: If the service has been forced down or nova-compute
      type: bool
    host:
      description: The name of the host.
      type: str
    name:
      description: Service name
      type: str
    state:
      description: The state of the service. One of up or down.
      type: str
    status:
      description: The status of the service. One of enabled or disabled.
      type: str
    update_at:
      description: The date and time when the resource was updated
      type: str
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class ComputeServiceModule(OpenStackModule):
    argument_spec = dict(
        host=dict(required=True),
        binary=dict(required=True),
        status=dict(default="enabled", choices=['enabled', 'disabled']),
        disabled_reason=dict(default=None)
    )

    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        changed = False

        kwargs = {k: self.params[k]
                  for k in ['binary', 'host']
                  if self.params[k] is not None}

        # retrieve current state of service(s)
        compute_services = self.conn.compute.services(**kwargs)

        # extract desired status
        desired_status = self.params['status']
        disabled_reason = self.params['disabled_reason']

        # apply updates to diverging status
        for service in compute_services:

            current_status = service.status

            if current_status != desired_status:
                changed = True
                if not self.check_mode:

                    if desired_status == 'disabled':
                        self.conn.compute.disable_service(service=service, host=service.host, binary=service.binary, disabled_reason=disabled_reason)
                    else:
                        self.conn.compute.enable_service(service=service, host=service.host, binary=service.binary)

        # retrieve final state of the service(s)
        compute_services = self.conn.compute.services(**kwargs)

        self.exit_json(changed=changed,
                       compute_services=[s.to_dict(computed=False)
                                         for s in compute_services],)


def main():
    module = ComputeServiceModule()
    module()


if __name__ == '__main__':
    main()
