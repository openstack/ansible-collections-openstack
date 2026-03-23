#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 British Broadcasting Corporation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: network_segment
short_description: Creates/removes network segments from OpenStack
author: OpenStack Ansible SIG
description:
   - Add, update or remove network segments from OpenStack.
options:
   name:
     description:
        - Name to be assigned to the segment. Although Neutron allows for
          non-unique segment names, this module enforces segment name
          uniqueness.
     required: true
     type: str
   description:
     description:
        - Description of the segment
     type: str
   network:
     description:
        - Name or id of the network to which the segment should be attached
     type: str
   network_type:
     description:
        - The type of physical network that maps to this segment resource.
     type: str
   physical_network:
     description:
        - The physical network where this segment object is implemented.
     type: str
   segmentation_id:
     description:
        - An isolated segment on the physical network. The I(network_type)
          attribute defines the segmentation model. For example, if the
          I(network_type) value is vlan, this ID is a vlan identifier. If
          the I(network_type) value is gre, this ID is a gre key.
     type: int
   state:
     description:
        - Indicate desired state of the resource.
     choices: ['present', 'absent']
     default: present
     type: str
extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
# Create a VLAN type network segment named 'segment1'.
- openstack.cloud.network_segment:
    cloud: mycloud
    name: segment1
    network: my_network
    network_type: vlan
    segmentation_id: 2000
    physical_network: my_physnet
    state: present
'''

RETURN = '''
id:
    description: Id of segment
    returned: On success when segment exists.
    type: str
network_segment:
    description: Dictionary describing the network segment.
    returned: On success when network segment exists.
    type: dict
    contains:
        description:
            description: Description
            type: str
        id:
            description: Id
            type: str
        name:
            description: Name
            type: str
        network_id:
            description: Network Id
            type: str
        network_type:
            description: Network type
            type: str
        physical_network:
            description: Physical network
            type: str
        segmentation_id:
            description: Segmentation Id
            type: int
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class NetworkSegmentModule(OpenStackModule):

    argument_spec = dict(
        name=dict(required=True),
        description=dict(),
        network=dict(),
        network_type=dict(),
        physical_network=dict(),
        segmentation_id=dict(type='int'),
        state=dict(default='present', choices=['absent', 'present'])
    )

    def run(self):

        state = self.params['state']
        name = self.params['name']
        network_name_or_id = self.params['network']

        kwargs = {}
        filters = {}
        for arg in ('description', 'network_type', 'physical_network', 'segmentation_id'):
            if self.params[arg] is not None:
                kwargs[arg] = self.params[arg]

        for arg in ('network_type', 'physical_network'):
            if self.params[arg] is not None:
                filters[arg] = self.params[arg]

        if network_name_or_id:
            network = self.conn.network.find_network(network_name_or_id,
                                                     ignore_missing=False,
                                                     **filters)
            kwargs['network_id'] = network.id
            filters['network_id'] = network.id

        segment = self.conn.network.find_segment(name, **filters)

        if state == 'present':
            if not segment:
                segment = self.conn.network.create_segment(name=name, **kwargs)
                changed = True
            else:
                changed = False
                update_kwargs = {}

                # As the name is required and all other attributes cannot be
                # changed (and appear in filters above), we only need to handle
                # updates to the description here.
                for arg in ["description"]:
                    if (
                        arg in kwargs
                        # ensure user wants something specific
                        and kwargs[arg] is not None
                        # and this is not what we have right now
                        and kwargs[arg] != segment[arg]
                    ):
                        update_kwargs[arg] = kwargs[arg]

                if update_kwargs:
                    segment = self.conn.network.update_segment(
                        segment.id, **update_kwargs
                    )
                    changed = True

            segment = segment.to_dict(computed=False)
            self.exit(changed=changed, network_segment=segment, id=segment['id'])
        elif state == 'absent':
            if not segment:
                self.exit(changed=False)
            else:
                self.conn.network.delete_segment(segment['id'])
                self.exit(changed=True)


def main():
    module = NetworkSegmentModule()
    module()


if __name__ == '__main__':
    main()
