# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: port_forwarding
short_description: Create/Update/Delete port forwarding resources from OpenStack
description:
  - Create, Update and Remove Neutron floating IP port forwarding resources from OpenStack
  - Port forwarding allows external traffic to reach instances behind a floating IP
author: OpenStack Ansible SIG
options:
  external_protocol_port:
    description:
      - The external port number on the floating IP that will be forwarded
      - Must be between 1 and 65535
      - Required if C(port_forwarding_id) is set
    type: int
    aliases: ['external_port']
  floating_ip:
    description:
      - The floating IP address or ID to create port forwarding on
    type: str
    required: true
    aliases: ['floating_ip_address']
  internal_ip:
    description:
      - The internal IP address to forward traffic to
      - Must be one of the fixed IPs on the specified port
      - If not specified, uses the first fixed IP of the port
      - Requires C(network_port)
    type: str
    aliases: ['internal_ip_address']
  internal_protocol_port:
    description:
      - The internal port number to forward traffic to
      - Must be between 1 and 65535
      - Required if C(port_forwarding_id) is set
    type: int
    aliases: ['internal_port']
  network_port:
    description:
      - The Neutron port name or ID that contains the internal IP
      - Required if C(port_forwarding_id) is set
    type: str
  port_forwarding_id:
    description:
      - ID of an existing port forwarding resource
      - Used for updates and deletions when ID is known
    type: str
  protocol:
    description:
      - The IP protocol for the port forwarding resource
      - Supports tcp and udp protocols
      - Required if C(port_forwarding_id) is set
    type: str
  state:
    description:
      - Whether the port forwarding resource should exist or not
    type: str
    choices: ['present', 'absent']
    default: present

extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = r'''
- name: Create new port fowarding
  openstack.cloud.port_forwarding:
  state: present
  floating_ip: 192.168.150.67
  external_protocol_port: 80
  internal_protocol_port: 8080
  network_port: example_http_port
  protocol: tcp

- name: Update previously created port forwarding
  openstack.cloud.port_forwarding:
  state: present
  port_forwarding_id: existing_port_forwarding
  floating_ip: 192.168.150.67
  internal_protocol_port: 9090

- name: Delete port forwarding
  openstack.cloud.port_forwarding:
  state: absent
  port_forwarding_id: "resource-id"
  floating_ip: "203.0.113.100"
'''

RETURN = r'''
port_forwarding:
  description: Dictionary describing the port forwarding resource.
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


class PortForwardingModule(OpenStackModule):
    argument_spec = dict(
        external_protocol_port=dict(type='int', aliases=['external_port']),
        floating_ip=dict(required=True, aliases=['floating_ip_address']),
        internal_ip=dict(aliases=['internal_ip_address']),
        internal_protocol_port=dict(type='int', aliases=['internal_port']),
        network_port=dict(),
        port_forwarding_id=dict(),
        protocol=dict(),
        state=dict(default='present', choices=['present', 'absent']),
    )

    module_kwargs = dict(
        required_if=[
            ['port_forwarding_id', None, ['external_protocol_port',
                                          'internal_protocol_port',
                                          'network_port',
                                          'protocol'], False],
        ],
        required_by={
            'internal_ip': ['network_port'],
        },
    )

    def run(self):
        port_forwarding_id = self.params['port_forwarding_id']
        floating_ip = self.conn.network.find_ip(self.params['floating_ip'],
                                                ignore_missing=False)
        port = self.conn.network.find_port(self.params['network_port']) \
            if self.params['network_port'] else None
        internal_ip = self._find_internal_ip(port) if port else None
        external_port = self.params['external_protocol_port']
        internal_port = self.params['internal_protocol_port']
        protocol = self.params['protocol']
        state = self.params['state']

        attrs = {}
        if port is not None:
            attrs['internal_port_id'] = port.id

        if internal_ip is not None:
            attrs['internal_ip_address'] = internal_ip

        if external_port is not None:
            attrs['external_port'] = external_port

        if protocol is not None:
            attrs['protocol'] = protocol

        port_forwarding = self._find_port_forwarding(floating_ip.id,
                                                     port_forwarding_id,
                                                     attrs)

        if internal_port is not None:
            attrs['internal_port'] = internal_port

        changed = False
        if state == 'present':
            if port_forwarding:
                # found valid pfwd_id or pfwd with matching attributes
                new_attrs = {k: v for k, v in attrs.items() if port_forwarding[k] != v}
                if new_attrs:
                    port_forwarding = self.conn.network.update_port_forwarding(
                        port_forwarding.id, floating_ip.id, **new_attrs)
                    changed = True

            elif not port_forwarding_id:
                # pfwd_id not given, so create new pfwd
                attrs['floatingip_id'] = floating_ip.id
                port_forwarding = self.conn.network.create_port_forwarding(**attrs)
                changed = True

            self.exit_json(changed=changed, port_forwarding=port_forwarding)

        else:
            if port_forwarding:
                self.conn.network.delete_port_forwarding(port_forwarding.id, floating_ip.id)
                changed = True

            self.exit_json(changed=changed)

    def _find_internal_ip(self, port):
        internal_ip = self.params['internal_ip']
        if internal_ip:
            for fixed_ip in port.fixed_ips:
                if fixed_ip['ip_address'] == internal_ip:
                    return internal_ip

            self.fail_json(
                msg='Internal IP %s not found in port %s fixed IPs' % (internal_ip, port.id))

        else:
            if port.fixed_ips:
                return port.fixed_ips[0]['ip_address']

            else:
                self.fail_json(msg='Port %s has no fixed IPs available' % port.id)

    def _find_port_forwarding(self, fip_id, pf_id, attrs):
        try:
            if pf_id:
                return self.conn.network.find_port_forwarding(pf_id, fip_id, ignore_missing=False)

            port_forwardings = list(self.conn.network.port_forwardings(fip_id, **attrs))
            if len(port_forwardings) > 1:
                self.fail_json(
                    msg='Found more than one port forwarding resources with matching attributes')

            return port_forwardings[0] if len(port_forwardings) == 1 else None
        except self.sdk.exceptions.NotFoundException:
            return None


def main():
    module = PortForwardingModule()
    module()


if __name__ == '__main__':
    main()
