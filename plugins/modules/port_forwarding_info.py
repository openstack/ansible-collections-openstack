# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: port_forwarding_info
short_description: Retrieve port forwarding resources from OpenStack.
description:
  - Retrieve Neutron floating IP port forwarding resources from OpenStack.
author: OpenStack Ansible SIG
options:
  external_port:
    description:
      - The external port number on the floating IP that will be forwarded.
    type: int
  floating_ip:
    description:
      - The address or ID of a floating IP that contains a port forwarding.
    type: str
  internal_port_id:
    description:
      - The Neutron port ID.
    type: str
  port_forwarding_id:
    description:
      - ID of an existing port forwarding resource.
    type: str
  protocol:
    description:
      - The IP protocol for the port forwarding resource.
    type: str

extends_documentation_fragment:
  - openstack.cloud.openstack

'''

EXAMPLES = r'''
# Getting all port forwardings
- openstack.cloud.port_forwarding_info:
  register: pfwds

# Getting port forwardings by associated floating ip
- openstack.cloud.port_forwarding_info:
  floating_ip: 192.168.42.67
  register: pfwds

# Getting port forwarding by port forwarding id
- openstack.cloud.port_forwarding_info:
  port_forwarding_id: d09f88d6-bb20-4268-9139-27c1b82c51d0
  register: pfwd
'''

RETURN = r'''
port_forwardings:
  description: The port forwarding objects list.
  type: list
  elements: dict
  returned: success
  contains:
    description:
      description: The description of the port forwarding.
      type: str
    external_port:
      description: The external port number.
      type: int
    floatingip_id:
      description: The floating IP id associated with the port forwarding.
      type: str
    id:
      description: The id of the port forwarding.
      type: str
    internal_ip_address:
      description: The internal IP address associated with the port forwarding.
      type: str
    internal_port:
      description: The internal port number.
      type: int
    internal_port_id:
      description: The ID of the network port associated with the port forwarding.
      type: str
    protocol:
      description: The IP protocol used for port forwarding.
      type: str
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule
)


class PortForwardingInfoModule(OpenStackModule):
    argument_spec = dict(
        external_port=dict(type='int'),
        floating_ip=dict(),
        internal_port_id=dict(),
        port_forwarding_id=dict(),
        protocol=dict(),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def _find_port_forwardings(self):
        port_forwarding_id = self.params['port_forwarding_id']
        floating_ip = self.params['floating_ip']
        query_kwargs = {k: self.params[k]
                        for k in ['external_port',
                                  'internal_port_id',
                                  'protocol']
                        if self.params[k] is not None}

        floating_ips = None
        if floating_ip:
            fip = self.conn.network.find_ip(floating_ip)
            floating_ips = [fip] if fip else []
        else:
            floating_ips = self.conn.network.ips()

        port_forwardings = []
        if port_forwarding_id is None:
            for fip in floating_ips:
                pfwds = self.conn.network.port_forwardings(fip.id, **query_kwargs)
                port_forwardings.extend(list(pfwds))

        else:
            for fip in floating_ips:
                pfwd = self.conn.network.find_port_forwarding(
                    port_forwarding_id, fip.id, query_kwargs)
                if pfwd:
                    return [pfwd]

        return port_forwardings

    def run(self):
        port_forwardings = [pfwd.to_dict(computed=False)
                            for pfwd in self._find_port_forwardings()]

        self.exit(changed=False, port_forwardings=port_forwardings)


def main():
    module = PortForwardingInfoModule()
    module()


if __name__ == '__main__':
    main()
