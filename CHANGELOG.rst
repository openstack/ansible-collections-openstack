=============================================
Openstack Cloud Ansilbe modules Release Notes
=============================================

.. contents:: Topics


v1.2.1
======

Release Summary
---------------

Porting modules to new OpenstackModule class and fixes.

Minor Changes
-------------

- dns_zone - Migrating dns_zone from AnsibleModule to OpenStackModule
- dns_zone, recordset - Enable update for recordset and add tests for dns and recordset module
- endpoint - Do not fail when endpoint state is absent
- ironic - Refactor ironic authentication into a new module_utils module
- loadbalancer - Refactor loadbalancer module
- network - Migrating network from AnsibleModule to OpenStackModule
- networks_info - Migrating networks_info from AnsibleModule to OpenStackModule
- openstack - Add galaxy.yml to support install from git
- openstack - Fix docs-args mismatch in modules
- openstack - OpenStackModule Support defining a minimum version of the SDK
- router - Migrating routers from AnsibleModule to OpenStackModule
- routers_info - Added deprecated_names for router_info module
- routers_info - Migrating routers_info from AnsibleModule to OpenStackModule
- security_group.py - Migrating security_group from AnsibleModule to OpenStackModule
- security_group_rule - Refactor TCP/UDP port check
- server.py - Improve "server" module with OpenstackModule class
- server_volume - Migrating server_volume from AnsibleModule to OpenStackModule
- subnet - Fix subnets update and idempotency
- subnet - Migrating subnet module from AnsibleModule to OpenStackModule
- subnets_info - Migrating subnets_info from AnsibleModule to OpenStackModule
- volume.py - Migrating volume from AnsibleModule to OpenStackModule
- volume_info - Fix volume_info arguments for SDK 0.19

v1.2.0
======

Release Summary
---------------

New volume backup modules.

Minor Changes
-------------

- lb_health_monitor - Make it possible to create a health monitor to a pool

New Modules
-----------

- openstack.cloud.volume_backup module - Add/Delete Openstack volumes backup.
- openstack.cloud.volume_backup_info module - Retrieve information about Openstack volume backups.
- openstack.cloud.volume_snapshot_info module - Retrieve information about Openstack volume snapshots.

v1.1.0
======

Release Summary
---------------

Starting redesign modules and bugfixes.

Minor Changes
-------------

- A basic module subclass was introduced and a few modules moved to inherit from it.
- Add more useful information from exception
- Added pip installation option for collection.
- Added template for generation of artibtrary module.
- baremetal modules - Do not require ironic_url if cloud or auth.endpoint is provided
- inventory_openstack - Add openstack logger and Ansible display utility
- loadbalancer - Add support for setting the Flavor when creating a load balancer

Bugfixes
--------

- Fix non existing attribuites in SDK exception
- security_group_rule - Don't pass tenant_id for remote group

New Modules
-----------

- openstack.cloud.volume_info - Retrieve information about Openstack volumes.

v1.0.1
======

Release Summary
---------------

Bugfix for server_info

Bugfixes
--------

- server_info - Fix broken server_info module and add tests

v1.0.0
======

Release Summary
---------------

Initial release of collection.

Minor Changes
-------------

- Renaming all modules and removing "os" prefix from names.
- baremetal_node_action - Support json type for the ironic_node config_drive parameter
- config - Update os_client_config to use openstacksdk
- host_aggregate - Add support for not 'purging' missing hosts
- project - Add properties for os_project
- server_action - pass imageRef to rebuild
- subnet - Updated allocation pool checks

Bugfixes
--------

- baremetal_node - Correct parameter name
- coe_cluster - Retrive id/uuid correctly
- federation_mapping - Fixup some minor nits found in followup reviews
- inventory_openstack - Fix constructed compose
- network - Bump minimum openstacksdk version when using os_network/dns_domain
- role_assignment - Fix os_user_role for groups in multidomain context
- role_assignment - Fix os_user_role issue to grant a role in a domain

New Modules
-----------

- openstack.cloud.federation_idp - Add support for Keystone Identity Providers
- openstack.cloud.federation_idp_info - Add support for fetching the information about federation IDPs
- openstack.cloud.federation_mapping - Add support for Keystone mappings
- openstack.cloud.federation_mapping_info - Add support for fetching the information about Keystone mappings
- openstack.cloud.keystone_federation_protocol - Add support for Keystone federation Protocols
- openstack.cloud.keystone_federation_protocol_info - Add support for getting information about Keystone federation Protocols
- openstack.cloud.routers_info - Retrieve information about one or more OpenStack routers.
