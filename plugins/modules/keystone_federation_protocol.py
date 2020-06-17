#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: keystone_federation_protocol
short_description: manage a federation Protocol
author: OpenStack Ansible SIG
description:
  - Manage a federation Protocol.
options:
  name:
    description:
      - The name of the Protocol.
    type: str
    required: true
    aliases: ['id']
  state:
    description:
      - Whether the protocol should be C(present) or C(absent).
    choices: ['present', 'absent']
    default: present
    type: str
  idp_id:
    description:
      - The name of the Identity Provider this Protocol is associated with.
    aliases: ['idp_name']
    required: true
    type: str
  mapping_id:
    description:
      - The name of the Mapping to use for this Protocol.'
      - Required when creating a new Protocol.
    type: str
    aliases: ['mapping_name']
requirements:
  - "python >= 3.6"
  - "openstacksdk >= 0.44"
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Create a protocol
  openstack.cloud.keystone_federation_protocol:
    cloud: example_cloud
    name: example_protocol
    idp_id: example_idp
    mapping_id: example_mapping

- name: Delete a protocol
  openstack.cloud.keystone_federation_protocol:
    cloud: example_cloud
    name: example_protocol
    idp_id: example_idp
    state: absent
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_full_argument_spec
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_module_kwargs
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_cloud_from_module


def normalize_protocol(protocol):
    """
    Normalizes the protocol definitions so that the outputs are consistent with the
    parameters

    - "name" (parameter) == "id" (SDK)
    """
    if protocol is None:
        return None

    _protocol = protocol.to_dict()
    _protocol['name'] = protocol['id']
    # As of 0.44 SDK doesn't copy the URI parameters over, so let's add them
    _protocol['idp_id'] = protocol['idp_id']
    return _protocol


def delete_protocol(module, sdk, cloud, protocol):
    """
    Delete an existing Protocol

    returns: the "Changed" state
    """

    if protocol is None:
        return False

    if module.check_mode:
        return True

    try:
        cloud.identity.delete_federation_protocol(None, protocol)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to delete protocol: {0}'.format(str(ex)))
    return True


def create_protocol(module, sdk, cloud, name):
    """
    Create a new Protocol

    returns: the "Changed" state and the new protocol
    """

    if module.check_mode:
        return True, None

    idp_name = module.params.get('idp_id')
    mapping_id = module.params.get('mapping_id')

    attributes = {
        'idp_id': idp_name,
        'mapping_id': mapping_id,
    }

    try:
        protocol = cloud.identity.create_federation_protocol(id=name, **attributes)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to create protocol: {0}'.format(str(ex)))
    return (True, protocol)


def update_protocol(module, sdk, cloud, protocol):
    """
    Update an existing Protocol

    returns: the "Changed" state and the new protocol
    """

    mapping_id = module.params.get('mapping_id')

    attributes = {}

    if (mapping_id is not None) and (mapping_id != protocol.mapping_id):
        attributes['mapping_id'] = mapping_id

    if not attributes:
        return False, protocol

    if module.check_mode:
        return True, None

    try:
        new_protocol = cloud.identity.update_federation_protocol(None, protocol, **attributes)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to update protocol: {0}'.format(str(ex)))
    return (True, new_protocol)


def main():
    """ Module entry point """

    argument_spec = openstack_full_argument_spec(
        name=dict(required=True, aliases=['id']),
        state=dict(default='present', choices=['absent', 'present']),
        idp_id=dict(required=True, aliases=['idp_name']),
        mapping_id=dict(aliases=['mapping_name']),
    )
    module_kwargs = openstack_module_kwargs(
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    name = module.params.get('name')
    state = module.params.get('state')
    idp = module.params.get('idp_id')
    changed = False

    sdk, cloud = openstack_cloud_from_module(module, min_version="0.44")

    try:
        protocol = cloud.identity.get_federation_protocol(idp, name)
    except sdk.exceptions.ResourceNotFound:
        protocol = None
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to get protocol: {0}'.format(str(ex)))

    if state == 'absent':
        if protocol is not None:
            changed = delete_protocol(module, sdk, cloud, protocol)
        module.exit_json(changed=changed)

    # state == 'present'
    else:
        if protocol is None:
            if module.params.get('mapping_id') is None:
                module.fail_json(msg='A mapping_id must be passed when creating'
                                 ' a protocol')
            (changed, protocol) = create_protocol(module, sdk, cloud, name)
            protocol = normalize_protocol(protocol)
            module.exit_json(changed=changed, protocol=protocol)

        else:
            (changed, new_protocol) = update_protocol(module, sdk, cloud, protocol)
            new_protocol = normalize_protocol(new_protocol)
            module.exit_json(changed=changed, protocol=new_protocol)


if __name__ == '__main__':
    main()
