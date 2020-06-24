#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: federation_mapping_info
short_description: Get the information about the available federation mappings
author: OpenStack Ansible SIG
description:
  - Fetch a federation mapping.
options:
  name:
    description:
      - The name of the mapping to fetch.
      - If I(name) is specified, the module will return failed if the mapping
        doesn't exist.
    type: str
    aliases: ['id']
requirements:
  - "python >= 3.6"
  - "openstacksdk >= 0.44"
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Fetch a specific mapping
  openstack.cloud.federation_mapping_info:
    cloud: example_cloud
    name: example_mapping

- name: Fetch all mappings
  openstack.cloud.federation_mapping_info:
    cloud: example_cloud
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_full_argument_spec
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_module_kwargs
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_cloud_from_module


def normalize_mapping(mapping):
    """
    Normalizes the mapping definitions so that the outputs are consistent with the
    parameters

    - "name" (parameter) == "id" (SDK)
    """
    if mapping is None:
        return None

    _mapping = mapping.to_dict()
    _mapping['name'] = mapping['id']
    return _mapping


def main():
    """ Module entry point """

    argument_spec = openstack_full_argument_spec(
        name=dict(aliases=['id']),
    )
    module_kwargs = openstack_module_kwargs(
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    name = module.params.get('name')

    sdk, cloud = openstack_cloud_from_module(module, min_version="0.44")

    if name:
        try:
            mapping = normalize_mapping(cloud.identity.get_mapping(name))
        except sdk.exceptions.ResourceNotFound:
            module.fail_json(msg='Failed to find mapping')
        except sdk.exceptions.OpenStackCloudException as ex:
            module.fail_json(msg='Failed to get mapping: {0}'.format(str(ex)))
        module.exit_json(changed=False, mappings=[mapping])

    else:
        try:
            mappings = list(map(normalize_mapping, cloud.identity.mappings()))
        except sdk.exceptions.OpenStackCloudException as ex:
            module.fail_json(msg='Failed to list mappings: {0}'.format(str(ex)))
        module.exit_json(changed=False, mappings=mappings)


if __name__ == '__main__':
    main()
