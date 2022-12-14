#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2013, Benno Joy <benno@ansible.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: security_group_rule
short_description: Add/Delete rule from an existing security group
author: OpenStack Ansible SIG
description:
   - Add or Remove rule from an existing security group
options:
   security_group:
      description:
        - Name or ID of the security group
      required: true
      type: str
   protocol:
      description:
        - IP protocols ANY TCP UDP ICMP and others, also number in range 0-255
      type: str
   port_range_min:
      description:
        - Starting port
      type: int
   port_range_max:
      description:
        - Ending port
      type: int
   remote_ip_prefix:
      description:
        - Source IP address(es) in CIDR notation (exclusive with remote_group)
      type: str
   remote_group:
      description:
        - Name or ID of the Security group to link (exclusive with
          remote_ip_prefix)
      type: str
   ether_type:
      description:
        - Must be IPv4 or IPv6, and addresses represented in CIDR must
          match the ingress or egress rules. Not all providers support IPv6.
      choices: ['IPv4', 'IPv6']
      default: IPv4
      type: str
      aliases: [ethertype]
   direction:
      description:
        - The direction in which the security group rule is applied. Not
          all providers support egress.
      choices: ['egress', 'ingress']
      default: ingress
      type: str
   state:
      description:
        - Should the resource be present or absent.
      choices: [present, absent]
      default: present
      type: str
   project:
     description:
        - Unique name or ID of the project.
     required: false
     type: str
   description:
     required: false
     description:
       - Description of the rule.
     type: str
requirements:
    - "python >= 3.6"
    - "openstacksdk"

extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
# Create a security group rule
- openstack.cloud.security_group_rule:
    cloud: mordred
    security_group: foo
    protocol: tcp
    port_range_min: 80
    port_range_max: 80
    remote_ip_prefix: 0.0.0.0/0

# Create a security group rule for ping
- openstack.cloud.security_group_rule:
    cloud: mordred
    security_group: foo
    protocol: icmp
    remote_ip_prefix: 0.0.0.0/0

# Another way to create the ping rule
- openstack.cloud.security_group_rule:
    cloud: mordred
    security_group: foo
    protocol: icmp
    port_range_min: -1
    port_range_max: -1
    remote_ip_prefix: 0.0.0.0/0

# Create a TCP rule covering all ports
- openstack.cloud.security_group_rule:
    cloud: mordred
    security_group: foo
    protocol: tcp
    port_range_min: 1
    port_range_max: 65535
    remote_ip_prefix: 0.0.0.0/0

# Another way to create the TCP rule above (defaults to all ports)
- openstack.cloud.security_group_rule:
    cloud: mordred
    security_group: foo
    protocol: tcp
    remote_ip_prefix: 0.0.0.0/0

# Create a rule for VRRP with numbered protocol 112
- openstack.cloud.security_group_rule:
    security_group: loadbalancer_sg
    protocol: 112
    remote_group: loadbalancer-node_sg

# Create a security group rule for a given project
- openstack.cloud.security_group_rule:
    cloud: mordred
    security_group: foo
    protocol: icmp
    remote_ip_prefix: 0.0.0.0/0
    project: myproj

# Remove the default created egress rule for IPv4
- openstack.cloud.security_group_rule:
   cloud: mordred
   security_group: foo
   protocol: any
   remote_ip_prefix: 0.0.0.0/0
'''

RETURN = '''
rule:
  description: Representation of the security group rule
  type: dict
  returned: when I(state) is present
  contains:
    created_at:
      description: Timestamp when the resource was created
      type: str
      returned: always
    description:
      description: Description of the resource
      type: str
      returned: always
    direction:
      description: The direction in which the security group rule is applied.
      type: str
      sample: 'egress'
      returned: always
    ether_type:
      description: Either IPv4 or IPv6
      type: str
      returned: always
    id:
      description: Unique rule UUID.
      type: str
      returned: always
    name:
      description: Name of the resource.
      type: str
      returned: always
    port_range_max:
      description: The maximum port number in the range that is matched by
                   the security group rule.
      type: int
      sample: 8000
      returned: always
    port_range_min:
      description: The minimum port number in the range that is matched by
                   the security group rule.
      type: int
      sample: 8000
      returned: always
    project_id:
      description: ID of the project the resource belongs to.
      type: str
      returned: always
    protocol:
      description: The protocol that is matched by the security group rule.
      type: str
      sample: 'tcp'
      returned: always
    remote_address_group_id:
      description: The remote address group ID to be associated with this
                   security group rule.
      type: str
      sample: '0.0.0.0/0'
      returned: always
    remote_group_id:
      description: The remote security group ID to be associated with this
                   security group rule.
      type: str
      sample: '0.0.0.0/0'
      returned: always
    remote_ip_prefix:
      description: The remote IP prefix to be associated with this security
                   group rule.
      type: str
      sample: '0.0.0.0/0'
      returned: always
    revision_number:
      description: Revision number
      type: int
      sample: 0
      returned: always
    security_group_id:
      description: The security group ID to associate with this security group
                   rule.
      type: str
      returned: always
    tags:
      description: Tags associated with resource.
      type: list
      elements: str
      returned: always
    tenant_id:
      description: ID of the project the resource belongs to. Deprecated.
      type: str
      returned: always
    updated_at:
      description: Timestamp when the security group rule was last updated.
      type: str
      returned: always
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule)


def _ports_match(protocol, module_min, module_max, rule_min, rule_max):
    """
    Capture the complex port matching logic.

    The port values coming in for the module might be -1 (for ICMP),
    which will work only for Nova, but this is handled by sdk. Likewise,
    they might be None, which works for Neutron, but not Nova. This too is
    handled by sdk. Since sdk will consistently return these port
    values as None, we need to convert any -1 values input to the module
    to None here for comparison.

    For TCP and UDP protocols, None values for both min and max are
    represented as the range 1-65535 for Nova, but remain None for
    Neutron. sdk returns the full range when Nova is the backend (since
    that is how Nova stores them), and None values for Neutron. If None
    values are input to the module for both values, then we need to adjust
    for comparison.
    """

    # Check if the user is supplying -1 for ICMP.
    if protocol in ['icmp', 'ipv6-icmp']:
        if module_min and int(module_min) == -1:
            module_min = None
        if module_max and int(module_max) == -1:
            module_max = None

    # Rules with 'any' protocol do not match ports
    if protocol == 'any':
        return True

    # Check if the user is supplying -1, 1 to 65535 or None values for full TPC/UDP port range.
    if protocol in ['tcp', 'udp'] or protocol is None:
        if (
            not module_min and not module_max
            or (int(module_min) in [-1, 1]
                and int(module_max) in [-1, 65535])
        ):
            if (
                not rule_min and not rule_max
                or (int(rule_min) in [-1, 1]
                    and int(rule_max) in [-1, 65535])
            ):
                # (None, None) == (1, 65535) == (-1, -1)
                return True

    # Sanity check to make sure we don't have type comparison issues.
    if module_min:
        module_min = int(module_min)
    if module_max:
        module_max = int(module_max)
    if rule_min:
        rule_min = int(rule_min)
    if rule_max:
        rule_max = int(rule_max)

    return module_min == rule_min and module_max == rule_max


class SecurityGroupRuleModule(OpenStackModule):

    argument_spec = dict(
        security_group=dict(required=True),
        protocol=dict(),
        port_range_min=dict(type='int'),
        port_range_max=dict(type='int'),
        remote_ip_prefix=dict(),
        remote_group=dict(),
        ether_type=dict(default='IPv4',
                        choices=['IPv4', 'IPv6'],
                        aliases=['ethertype']),
        direction=dict(default='ingress',
                       choices=['egress', 'ingress']),
        state=dict(default='present',
                   choices=['absent', 'present']),
        description=dict(),
        project=dict(),
    )

    module_kwargs = dict(
        mutually_exclusive=[
            ['remote_ip_prefix', 'remote_group'],
        ]
    )

    def _build_kwargs(self, secgroup, remote_group, project):
        kwargs = dict(
            security_group_id=secgroup.id,
            description=self.params['description'],
            port_range_max=self.params['port_range_max'],
            port_range_min=self.params['port_range_min'],
            protocol=self.params['protocol'],
            remote_ip_prefix=self.params['remote_ip_prefix'],
            direction=self.params['direction'],
            ether_type=self.params['ether_type'],
        )
        if self.params['port_range_min'] != -1:
            kwargs['port_range_min'] = self.params['port_range_min']
        if self.params['port_range_max'] != -1:
            kwargs['port_range_max'] = self.params['port_range_max']
        if project:
            kwargs['project_id'] = project.id
        if remote_group:
            kwargs['remote_group_id'] = remote_group.id
        return {k: v for k, v in kwargs.items() if v is not None}

    def _find_matching_rule(self, kwargs, secgroup):
        """
        Find a rule in the group that matches the module parameters.
        :returns: The matching rule dict, or None if no matches.
        """
        fields = ('protocol', 'remote_ip_prefix', 'direction',
                  'remote_group_id')
        for rule in secgroup['security_group_rules']:
            if ('ether_type' in kwargs
               and rule['ethertype'] != kwargs['ether_type']):
                continue
            if any(field in kwargs and rule[field] != kwargs[field]
                   for field in fields):
                continue
            if _ports_match(
                    self.params['protocol'],
                    self.params['port_range_min'],
                    self.params['port_range_max'],
                    rule['port_range_min'],
                    rule['port_range_max']
            ):
                return rule
        return None

    def _system_state_change(self, secgroup, rule):
        state = self.params['state']
        if not secgroup:
            return False

        if state == 'present' and not rule:
            return True
        if state == 'absent' and rule:
            return True
        return False

    def run(self):
        state = self.params['state']
        security_group = self.params['security_group']
        remote_group_name_or_id = self.params['remote_group']
        project_name_or_id = self.params['project']

        project = None
        if project_name_or_id:
            project = self.conn.identity.find_project(project_name_or_id,
                                                      ignore_missing=False)

        filters = {}
        if project and not remote_group_name_or_id:
            filters = {'project_id': project.id}

        secgroup = self.conn.network.find_security_group(
            security_group, ignore_missing=(state == 'absent'), **filters)

        remote_group = None
        if remote_group_name_or_id:
            remote_group = self.conn.network.find_security_group(
                remote_group_name_or_id, ignore_missing=False, filters=filters)

        kwargs = self._build_kwargs(secgroup, remote_group, project)

        rule = None
        if secgroup:
            # TODO: Replace with self.conn.network.find_security_group_rule()?
            rule = self._find_matching_rule(kwargs, secgroup)
            if rule:
                rule = self.conn.network.get_security_group_rule(rule['id'])

        if self.ansible.check_mode:
            self.exit_json(changed=self._system_state_change(secgroup, rule))

        changed = False
        if state == 'present':
            if self.params['protocol'] == 'any':
                self.params['protocol'] = None

            if not rule:
                rule = self.conn.network.create_security_group_rule(**kwargs)
                changed = True

            rule = rule.to_dict(computed=False)
            self.exit_json(changed=changed, rule=rule)

        if state == 'absent' and rule:
            self.conn.network.delete_security_group_rule(rule['id'])
            changed = True

        self.exit_json(changed=changed)


def main():
    module = SecurityGroupRuleModule()
    module()


if __name__ == '__main__':
    main()
