=============================================
Openstack Cloud Ansilbe modules Release Notes
=============================================

.. contents:: Topics


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

Deprecated Features
-------------------

- foo - The bar option has been deprecated. Use the username option instead.
- send_request - The quic option has been deprecated. Use the protocol option instead.

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
