#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: keystone_federation_protocol_info
short_description: get information about federation Protocols
author: OpenStack Ansible SIG
description:
  - Get information about federation Protocols.
options:
  name:
    description:
      - The name of the Protocol.
    type: str
    aliases: ['id']
  idp_id:
    description:
      - The name of the Identity Provider this Protocol is associated with.
    aliases: ['idp_name']
    required: true
    type: str
requirements:
  - "python >= 3.6"
  - "openstacksdk >= 0.44"
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Describe a protocol
  openstack.cloud.keystone_federation_protocol_info:
    cloud: example_cloud
    name: example_protocol
    idp_id: example_idp
    mapping_name: example_mapping

- name: Describe all protocols attached to an IDP
  openstack.cloud.keystone_federation_protocol_info:
    cloud: example_cloud
    idp_id: example_idp
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


def main():
    """ Module entry point """

    argument_spec = openstack_full_argument_spec(
        name=dict(aliases=['id']),
        idp_id=dict(required=True, aliases=['idp_name']),
    )
    module_kwargs = openstack_module_kwargs(
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    name = module.params.get('name')
    idp = module.params.get('idp_id')

    sdk, cloud = openstack_cloud_from_module(module, min_version="0.44")

    if name:
        try:
            protocol = cloud.identity.get_federation_protocol(idp, name)
            protocol = normalize_protocol(protocol)
        except sdk.exceptions.ResourceNotFound:
            module.fail_json(msg='Failed to find protocol')
        except sdk.exceptions.OpenStackCloudException as ex:
            module.fail_json(msg='Failed to get protocol: {0}'.format(str(ex)))
        module.exit_json(changed=False, protocols=[protocol])

    else:
        try:
            protocols = list(map(normalize_protocol, cloud.identity.federation_protocols(idp)))
        except sdk.exceptions.OpenStackCloudException as ex:
            module.fail_json(msg='Failed to list protocols: {0}'.format(str(ex)))
        module.exit_json(changed=False, protocols=protocols)


if __name__ == '__main__':
    main()
