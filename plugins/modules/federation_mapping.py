#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: federation_mapping
short_description: Manage a federation mapping
author: OpenStack Ansible SIG
description:
  - Manage a federation mapping.
options:
  name:
    description:
      - The name of the mapping to manage.
    required: true
    type: str
    aliases: ['id']
  state:
    description:
      - Whether the mapping should be C(present) or C(absent).
    choices: ['present', 'absent']
    default: present
    type: str
  rules:
    description:
      - The rules that comprise the mapping.  These are pairs of I(local) and
        I(remote) definitions.  For more details on how these work please see
        the OpenStack documentation
        U(https://docs.openstack.org/keystone/latest/admin/federation/mapping_combinations.html).
      - Required if I(state=present)
    type: list
    elements: dict
    suboptions:
      local:
        description:
        - Information on what local attributes will be mapped.
        required: true
        type: list
        elements: dict
      remote:
        description:
        - Information on what remote attributes will be mapped.
        required: true
        type: list
        elements: dict
requirements:
  - "python >= 3.6"
  - "openstacksdk >= 0.44"
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Create a new mapping
  openstack.cloud.federation_mapping:
    cloud: example_cloud
    name: example_mapping
    rules:
    - local:
      - user:
          name: '{0}'
      - group:
          id: '0cd5e9'
      remote:
      - type: UserName
      - type: orgPersonType
        any_one_of:
        - Contractor
        - SubContractor

- name: Delete a mapping
  openstack.cloud.federation_mapping:
    name: example_mapping
    state: absent
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_full_argument_spec
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_module_kwargs
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_cloud_from_module


def normalize_mapping(mapping):
    """
    Normalizes the mapping definitions so that the outputs are consistent with
    the parameters

    - "name" (parameter) == "id" (SDK)
    """
    if mapping is None:
        return None

    _mapping = mapping.to_dict()
    _mapping['name'] = mapping['id']
    return _mapping


def create_mapping(module, sdk, cloud, name):
    """
    Attempt to create a Mapping

    returns: A tuple containing the "Changed" state and the created mapping
    """

    if module.check_mode:
        return (True, None)

    rules = module.params.get('rules')

    try:
        mapping = cloud.identity.create_mapping(id=name, rules=rules)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to create mapping: {0}'.format(str(ex)))
    return (True, mapping)


def delete_mapping(module, sdk, cloud, mapping):
    """
    Attempt to delete a Mapping

    returns: the "Changed" state
    """
    if mapping is None:
        return False

    if module.check_mode:
        return True

    try:
        cloud.identity.delete_mapping(mapping)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to delete mapping: {0}'.format(str(ex)))
    return True


def update_mapping(module, sdk, cloud, mapping):
    """
    Attempt to delete a Mapping

    returns: The "Changed" state and the the new mapping
    """

    current_rules = mapping.rules
    new_rules = module.params.get('rules')

    # Nothing to do
    if current_rules == new_rules:
        return (False, mapping)

    if module.check_mode:
        return (True, None)

    try:
        new_mapping = cloud.identity.update_mapping(mapping, rules=new_rules)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to update mapping: {0}'.format(str(ex)))
    return (True, new_mapping)


def main():
    """ Module entry point """

    argument_spec = openstack_full_argument_spec(
        name=dict(required=True, aliases=['id']),
        state=dict(default='present', choices=['absent', 'present']),
        rules=dict(type='list', elements='dict', options=dict(
            local=dict(required=True, type='list', elements='dict'),
            remote=dict(required=True, type='list', elements='dict')
        )),
    )
    module_kwargs = openstack_module_kwargs(
        required_if=[('state', 'present', ['rules'])]
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    name = module.params.get('name')
    state = module.params.get('state')
    changed = False

    sdk, cloud = openstack_cloud_from_module(module, min_version="0.44")

    try:
        mapping = cloud.identity.get_mapping(name)
    except sdk.exceptions.ResourceNotFound:
        mapping = None
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to fetch mapping: {0}'.format(str(ex)))

    if state == 'absent':
        if mapping is not None:
            changed = delete_mapping(module, sdk, cloud, mapping)
        module.exit_json(changed=changed)

    # state == 'present'
    else:
        if len(module.params.get('rules')) < 1:
            module.fail_json(msg='At least one rule must be passed')

        if mapping is None:
            (changed, mapping) = create_mapping(module, sdk, cloud, name)
            mapping = normalize_mapping(mapping)
            module.exit_json(changed=changed, mapping=mapping)
        else:
            (changed, new_mapping) = update_mapping(module, sdk, cloud, mapping)
            new_mapping = normalize_mapping(new_mapping)
            module.exit_json(mapping=new_mapping, changed=changed)


if __name__ == '__main__':
    main()
