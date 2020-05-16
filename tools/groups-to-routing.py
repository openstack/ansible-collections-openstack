import os
import yaml

overrides = dict(
    os_client_config='config',
    os_endpoint='catalog_endpoint',
    os_flavor_info='compute_flavor_info',
    os_flavor='compute_flavor',
    os_group_info='identity_group_info',
    os_group='identity_group',
    os_ironic_node='baremetal_node_action',
    os_ironic_inspect='baremetal_inspect',
    os_ironic='baremetal_node',
    os_keystone_domain_info='identity_domain_info',
    os_keystone_domain='identity_domain',
    os_keystone_endpoint='endpoint',
    os_keystone_identity_provider_info='federation_idp_info',
    os_keystone_identity_provider='federation_idp',
    os_keystone_mapping_info='federation_mapping_info',
    os_keystone_mapping='federation_mapping',
    os_keystone_role='identity_role',
    os_keystone_service='catalog_service',
    os_listener='lb_listener',
    os_member='lb_member',
    os_nova_flavor='compute_flavor',
    os_nova_host_aggregate='host_aggregate',
    os_pool='lb_pool',
    os_user_group='group_assignment',
    os_user_info='identity_user_info',
    os_user_role='role_assignment',
    os_user='identity_user',
    os_zone='dns_zone',
)

old_list = []
new_list = []
module_runtime = dict()
mapping = dict()
os.system('git checkout HEAD^1 meta/action_groups.yml plugins ci')
groups = yaml.safe_load(open('meta/action_groups.yml', 'r'))
# Do override keys first so that they're done in sequence
for module in list(overrides.keys()) + groups['os']:
    old_list.append(module)
    new_name = overrides.get(module, module.replace('os_', ''))
    new_list.append(new_name)
    mapping[module] = new_name
    module_runtime[module] = dict(
        deprecation=dict(
            removal_date='TBD',
            warning_text=(
                'os_ prefixed module names are deprecated, use'
                f' openstack.cloud.{new_name}'
            ),
        ),
        redirect=f'openstack.cloud.{new_name}',
    )

groups['os'] = sorted(new_list) + sorted(old_list)
groups['openstack'] = sorted(new_list)

yaml.dump(groups, open('meta/action_groups.yml', 'w'))

runtime = dict(plugin_runtime=dict(modules=module_runtime))

yaml.dump(runtime, open('meta/runtime.yml', 'w'))


def replace_content(content):
    for old, new in mapping.items():
        content = content.replace(
            f'modules import {old}',
            f'modules import {new}',
        )
        content = content.replace(
            f'modules.{old}',
            f'modules.{new}',
        )
        content = content.replace(
            f'self.module = {old}',
            f'self.module = {new}',
        )
        content = content.replace(
            f'test_{old}',
            f'test_{new}',
        )
        content = content.replace(
            f'openstack.cloud.{old}',
            f'openstack.cloud.{new}',
        )
        content = content.replace(
            old,
            f'openstack.cloud.{new}',
        )
        content = content.replace(
            'module: openstack.cloud.',
            'module: ',
        )
    return content


for todo_path in ('ci', 'plugins', 'tests'):
    for (dirpath, dirnames, filenames) in os.walk(todo_path):
        for filename in filenames:
            contents = None
            oldfile = os.path.join(dirpath, filename)
            with open(oldfile, 'r') as infile:
                contents = replace_content(infile.read())
            with open(oldfile, 'w') as outfile:
                outfile.write(contents)
            if filename.endswith('.py'):
                old_file_base = os.path.splitext(filename)[0]
                if old_file_base in mapping:
                    new_file_base = mapping[old_file_base]
                    newfile = os.path.join(dirpath, f'{new_file_base}.py')
                    os.system(f'git mv {oldfile} {newfile}')
                    os.system(f'ln -s {new_file_base}.py {oldfile}')
                    os.system(f'git add {oldfile}')
                    continue
                if not filename.startswith('test_'):
                    continue
                old_file_module_base = old_file_base[5:]
                new_file_base = mapping.get(old_file_module_base)
                if not new_file_base:
                    continue
                newfile = os.path.join(dirpath, f'test_{new_file_base}.py')
                os.system(f'git mv {oldfile} {newfile}')

print("Edit tests/unit/modules/cloud/openstack/test_server.py by hand")
