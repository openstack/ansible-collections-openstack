#!/usr/bin/python
# coding: utf-8 -*-

# Copyright 2019 Red Hat, Inc.
# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2013, Benno Joy <benno@ansible.com>
# Copyright (c) 2013, John Dewey <john@dewey.ws>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: server
short_description: Create/Delete Compute Instances from OpenStack
author: OpenStack Ansible SIG
description:
   - Create or Remove compute instances from OpenStack.
options:
   name:
     description:
        - Name that has to be given to the instance. It is also possible to
          specify the ID of the instance instead of its name if I(state) is I(absent).
     required: true
     type: str
   image:
     description:
        - The name or id of the base image to boot.
        - Required when I(boot_from_volume=true)
     type: str
   image_exclude:
     description:
        - Text to use to filter image names, for the case, such as HP, where
          there are multiple image names matching the common identifying
          portions. image_exclude is a negative match filter - it is text that
          may not exist in the image name.
     type: str
     default: "(deprecated)"
   flavor:
     description:
        - The name or id of the flavor in which the new instance has to be
          created.
        - Exactly one of I(flavor) and I(flavor_ram) must be defined when
          I(state=present).
     type: str
   flavor_ram:
     description:
        - The minimum amount of ram in MB that the flavor in which the new
          instance has to be created must have.
        - Exactly one of I(flavor) and I(flavor_ram) must be defined when
          I(state=present).
     type: int
   flavor_include:
     description:
        - Text to use to filter flavor names, for the case, such as Rackspace,
          where there are multiple flavors that have the same ram count.
          flavor_include is a positive match filter - it must exist in the
          flavor name.
     type: str
   key_name:
     description:
        - The key pair name to be used when creating a instance
     type: str
   security_groups:
     description:
        - Names of the security groups to which the instance should be
          added. This may be a YAML list or a comma separated string.
     type: list
     default: ['default']
     elements: str
   network:
     description:
        - Name or ID of a network to attach this instance to. A simpler
          version of the nics parameter, only one of network or nics should
          be supplied.
     type: str
   nics:
     description:
        - A list of networks to which the instance's interface should
          be attached. Networks may be referenced by net-id/net-name/port-id
          or port-name.
        - 'Also this accepts a string containing a list of (net/port)-(id/name)
          Eg: nics: "net-id=uuid-1,port-name=myport"
          Only one of network or nics should be supplied.'
     type: list
     elements: raw
     default: []
     suboptions:
       tag:
         description:
            - 'A "tag" for the specific port to be passed via metadata.
              Eg: tag: test_tag'
   auto_ip:
     description:
        - Ensure instance has public ip however the cloud wants to do that
     type: bool
     default: 'yes'
     aliases: ['auto_floating_ip', 'public_ip']
   floating_ips:
     description:
        - list of valid floating IPs that pre-exist to assign to this node
     type: list
     elements: str
   floating_ip_pools:
     description:
        - Name of floating IP pool from which to choose a floating IP
     type: list
     elements: str
   meta:
     description:
        - 'A list of key value pairs that should be provided as a metadata to
          the new instance or a string containing a list of key-value pairs.
          Eg:  meta: "key1=value1,key2=value2"'
     type: raw
   wait:
     description:
        - If the module should wait for the instance to be created.
     type: bool
     default: 'yes'
   timeout:
     description:
        - The amount of time the module should wait for the instance to get
          into active state.
     default: 180
     type: int
   config_drive:
     description:
        - Whether to boot the server with config drive enabled
     type: bool
     default: 'no'
   userdata:
     description:
        - Opaque blob of data which is made available to the instance
     type: str
     aliases: ['user_data']
   boot_from_volume:
     description:
        - Should the instance boot from a persistent volume created based on
          the image given. Mutually exclusive with boot_volume.
     type: bool
     default: 'no'
   volume_size:
     description:
        - The size of the volume to create in GB if booting from volume based
          on an image.
     type: int
   boot_volume:
     description:
        - Volume name or id to use as the volume to boot from. Implies
          boot_from_volume. Mutually exclusive with image and boot_from_volume.
     aliases: ['root_volume']
     type: str
   terminate_volume:
     description:
        - If C(yes), delete volume when deleting instance (if booted from volume)
     type: bool
     default: 'no'
   volumes:
     description:
       - A list of preexisting volumes names or ids to attach to the instance
     default: []
     type: list
     elements: str
   scheduler_hints:
     description:
        - Arbitrary key/value pairs to the scheduler for custom use
     type: dict
   state:
     description:
       - Should the resource be present or absent.
     choices: [present, absent]
     default: present
     type: str
   delete_fip:
     description:
       - When I(state) is absent and this option is true, any floating IP
         associated with the instance will be deleted along with the instance.
     type: bool
     default: 'no'
   reuse_ips:
     description:
       - When I(auto_ip) is true and this option is true, the I(auto_ip) code
         will attempt to re-use unassigned floating ips in the project before
         creating a new one. It is important to note that it is impossible
         to safely do this concurrently, so if your use case involves
         concurrent server creation, it is highly recommended to set this to
         false and to delete the floating ip associated with a server when
         the server is deleted using I(delete_fip).
     type: bool
     default: 'yes'
   availability_zone:
     description:
       - Availability zone in which to create the server.
     type: str
   description:
     description:
       - Description of the server.
     type: str
extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Create a new instance and attaches to a network and passes metadata to the instance
  openstack.cloud.server:
       state: present
       auth:
         auth_url: https://identity.example.com
         username: admin
         password: admin
         project_name: admin
       name: vm1
       image: 4f905f38-e52a-43d2-b6ec-754a13ffb529
       key_name: ansible_key
       timeout: 200
       flavor: 4
       nics:
         - net-id: 34605f38-e52a-25d2-b6ec-754a13ffb723
         - net-name: another_network
       meta:
         hostname: test1
         group: uge_master

# Create a new instance in HP Cloud AE1 region availability zone az2 and
# automatically assigns a floating IP
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        state: present
        auth:
          auth_url: https://identity.example.com
          username: username
          password: Equality7-2521
          project_name: username-project1
        name: vm1
        region_name: region-b.geo-1
        availability_zone: az2
        image: 9302692b-b787-4b52-a3a6-daebb79cb498
        key_name: test
        timeout: 200
        flavor: 101
        security_groups: default
        auto_ip: yes

# Create a new instance in named cloud mordred availability zone az2
# and assigns a pre-known floating IP
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        state: present
        cloud: mordred
        name: vm1
        availability_zone: az2
        image: 9302692b-b787-4b52-a3a6-daebb79cb498
        key_name: test
        timeout: 200
        flavor: 101
        floating_ips:
          - 12.34.56.79

# Create a new instance with 4G of RAM on Ubuntu Trusty, ignoring
# deprecated images
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        name: vm1
        state: present
        cloud: mordred
        region_name: region-b.geo-1
        image: Ubuntu Server 14.04
        image_exclude: deprecated
        flavor_ram: 4096

# Create a new instance with 4G of RAM on Ubuntu Trusty on a Performance node
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        name: vm1
        cloud: rax-dfw
        state: present
        image: Ubuntu 14.04 LTS (Trusty Tahr) (PVHVM)
        flavor_ram: 4096
        flavor_include: Performance

# Creates a new instance and attaches to multiple network
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance with a string
      openstack.cloud.server:
        auth:
           auth_url: https://identity.example.com
           username: admin
           password: admin
           project_name: admin
        name: vm1
        image: 4f905f38-e52a-43d2-b6ec-754a13ffb529
        key_name: ansible_key
        timeout: 200
        flavor: 4
        nics: "net-id=4cb08b20-62fe-11e5-9d70-feff819cdc9f,net-id=542f0430-62fe-11e5-9d70-feff819cdc9f..."

- name: Creates a new instance and attaches to a network and passes metadata to the instance
  openstack.cloud.server:
       state: present
       auth:
         auth_url: https://identity.example.com
         username: admin
         password: admin
         project_name: admin
       name: vm1
       image: 4f905f38-e52a-43d2-b6ec-754a13ffb529
       key_name: ansible_key
       timeout: 200
       flavor: 4
       nics:
         - net-id: 34605f38-e52a-25d2-b6ec-754a13ffb723
         - net-name: another_network
       meta: "hostname=test1,group=uge_master"

- name:  Creates a new instance and attaches to a specific network
  openstack.cloud.server:
    state: present
    auth:
      auth_url: https://identity.example.com
      username: admin
      password: admin
      project_name: admin
    name: vm1
    image: 4f905f38-e52a-43d2-b6ec-754a13ffb529
    key_name: ansible_key
    timeout: 200
    flavor: 4
    network: another_network

# Create a new instance with 4G of RAM on a 75G Ubuntu Trusty volume
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        name: vm1
        state: present
        cloud: mordred
        region_name: ams01
        image: Ubuntu Server 14.04
        flavor_ram: 4096
        boot_from_volume: True
        volume_size: 75

# Creates a new instance with 2 volumes attached
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        name: vm1
        state: present
        cloud: mordred
        region_name: ams01
        image: Ubuntu Server 14.04
        flavor_ram: 4096
        volumes:
        - photos
        - music

# Creates a new instance with provisioning userdata using Cloud-Init
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        name: vm1
        state: present
        image: "Ubuntu Server 14.04"
        flavor: "P-1"
        network: "Production"
        userdata: |
          #cloud-config
          chpasswd:
            list: |
              ubuntu:{{ default_password }}
            expire: False
          packages:
            - ansible
          package_upgrade: true

# Creates a new instance with provisioning userdata using Bash Scripts
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        name: vm1
        state: present
        image: "Ubuntu Server 14.04"
        flavor: "P-1"
        network: "Production"
        userdata: |
          {%- raw -%}#!/bin/bash
          echo "  up ip route add 10.0.0.0/8 via {% endraw -%}{{ intra_router }}{%- raw -%}" >> /etc/network/interfaces.d/eth0.conf
          echo "  down ip route del 10.0.0.0/8" >> /etc/network/interfaces.d/eth0.conf
          ifdown eth0 && ifup eth0
          {% endraw %}

# Create a new instance with server group for (anti-)affinity
# server group ID is returned from openstack.cloud.server_group module.
- name: launch a compute instance
  hosts: localhost
  tasks:
    - name: launch an instance
      openstack.cloud.server:
        state: present
        name: vm1
        image: 4f905f38-e52a-43d2-b6ec-754a13ffb529
        flavor: 4
        scheduler_hints:
          group: f5c8c61a-9230-400a-8ed2-3b023c190a7f

# Create an instance with "tags" for the nic
- name: Create instance with nics "tags"
  openstack.cloud.server:
    state: present
    auth:
        auth_url: https://identity.example.com
        username: admin
        password: admin
        project_name: admin
    name: vm1
    image: 4f905f38-e52a-43d2-b6ec-754a13ffb529
    key_name: ansible_key
    flavor: 4
    nics:
      - port-name: net1_port1
        tag: test_tag
      - net-name: another_network

# Deletes an instance via its ID
- name: remove an instance
  hosts: localhost
  tasks:
    - name: remove an instance
      openstack.cloud.server:
        name: abcdef01-2345-6789-0abc-def0123456789
        state: absent

'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    openstack_find_nova_addresses, OpenStackModule)


def _parse_nics(nics):
    for net in nics:
        if isinstance(net, str):
            for nic in net.split(','):
                yield dict((nic.split('='),))
        else:
            yield net


def _parse_meta(meta):
    if isinstance(meta, str):
        metas = {}
        for kv_str in meta.split(","):
            k, v = kv_str.split("=")
            metas[k] = v
        return metas
    if not meta:
        return {}
    return meta


class ServerModule(OpenStackModule):
    deprecated_names = ('os_server', 'openstack.cloud.os_server')

    argument_spec = dict(
        name=dict(required=True),
        image=dict(default=None),
        image_exclude=dict(default='(deprecated)'),
        flavor=dict(default=None),
        flavor_ram=dict(default=None, type='int'),
        flavor_include=dict(default=None),
        key_name=dict(default=None),
        security_groups=dict(default=['default'], type='list', elements='str'),
        network=dict(default=None),
        nics=dict(default=[], type='list', elements='raw'),
        meta=dict(default=None, type='raw'),
        userdata=dict(default=None, aliases=['user_data']),
        config_drive=dict(default=False, type='bool'),
        auto_ip=dict(default=True, type='bool', aliases=['auto_floating_ip', 'public_ip']),
        floating_ips=dict(default=None, type='list', elements='str'),
        floating_ip_pools=dict(default=None, type='list', elements='str'),
        volume_size=dict(default=None, type='int'),
        boot_from_volume=dict(default=False, type='bool'),
        boot_volume=dict(default=None, aliases=['root_volume']),
        terminate_volume=dict(default=False, type='bool'),
        volumes=dict(default=[], type='list', elements='str'),
        scheduler_hints=dict(default=None, type='dict'),
        state=dict(default='present', choices=['absent', 'present']),
        delete_fip=dict(default=False, type='bool'),
        reuse_ips=dict(default=True, type='bool'),
        description=dict(default=None, type='str'),
    )
    module_kwargs = dict(
        mutually_exclusive=[
            ['auto_ip', 'floating_ips'],
            ['auto_ip', 'floating_ip_pools'],
            ['floating_ips', 'floating_ip_pools'],
            ['flavor', 'flavor_ram'],
            ['image', 'boot_volume'],
            ['boot_from_volume', 'boot_volume'],
            ['nics', 'network'],
        ],
        required_if=[
            ('boot_from_volume', True, ['volume_size', 'image']),
        ],
    )

    def run(self):

        state = self.params['state']
        image = self.params['image']
        boot_volume = self.params['boot_volume']
        flavor = self.params['flavor']
        flavor_ram = self.params['flavor_ram']

        if state == 'present':
            if not (image or boot_volume):
                self.fail(
                    msg="Parameter 'image' or 'boot_volume' is required "
                        "if state == 'present'"
                )
            if not flavor and not flavor_ram:
                self.fail(
                    msg="Parameter 'flavor' or 'flavor_ram' is required "
                        "if state == 'present'"
                )

        if state == 'present':
            self._get_server_state()
            self._create_server()
        elif state == 'absent':
            self._get_server_state()
            self._delete_server()

    def _exit_hostvars(self, server, changed=True):
        hostvars = self.conn.get_openstack_vars(server)
        self.exit(
            changed=changed, server=server, id=server.id, openstack=hostvars)

    def _get_server_state(self):
        state = self.params['state']
        server = self.conn.get_server(self.params['name'])
        if server and state == 'present':
            if server.status not in ('ACTIVE', 'SHUTOFF', 'PAUSED', 'SUSPENDED'):
                self.fail(
                    msg="The instance is available but not Active state: " + server.status)
            (ip_changed, server) = self._check_ips(server)
            (sg_changed, server) = self._check_security_groups(server)
            (server_changed, server) = self._update_server(server)
            self._exit_hostvars(server, ip_changed or sg_changed or server_changed)
        if server and state == 'absent':
            return True
        if state == 'absent':
            self.exit(changed=False, result="not present")
        return True

    def _create_server(self):
        flavor = self.params['flavor']
        flavor_ram = self.params['flavor_ram']
        flavor_include = self.params['flavor_include']

        image_id = None
        if not self.params['boot_volume']:
            image_id = self.conn.get_image_id(
                self.params['image'], self.params['image_exclude'])
            if not image_id:
                self.fail(
                    msg="Could not find image %s" % self.params['image'])

        if flavor:
            flavor_dict = self.conn.get_flavor(flavor)
            if not flavor_dict:
                self.fail(msg="Could not find flavor %s" % flavor)
        else:
            flavor_dict = self.conn.get_flavor_by_ram(flavor_ram, flavor_include)
            if not flavor_dict:
                self.fail(msg="Could not find any matching flavor")

        nics = self._network_args()

        self.params['meta'] = _parse_meta(self.params['meta'])

        bootkwargs = self.check_versioned(
            name=self.params['name'],
            image=image_id,
            flavor=flavor_dict['id'],
            nics=nics,
            meta=self.params['meta'],
            security_groups=self.params['security_groups'],
            userdata=self.params['userdata'],
            config_drive=self.params['config_drive'],
        )
        for optional_param in (
                'key_name', 'availability_zone', 'network',
                'scheduler_hints', 'volume_size', 'volumes',
                'description'):
            if self.params[optional_param]:
                bootkwargs[optional_param] = self.params[optional_param]

        server = self.conn.create_server(
            ip_pool=self.params['floating_ip_pools'],
            ips=self.params['floating_ips'],
            auto_ip=self.params['auto_ip'],
            boot_volume=self.params['boot_volume'],
            boot_from_volume=self.params['boot_from_volume'],
            terminate_volume=self.params['terminate_volume'],
            reuse_ips=self.params['reuse_ips'],
            wait=self.params['wait'], timeout=self.params['timeout'],
            **bootkwargs
        )

        self._exit_hostvars(server)

    def _update_server(self, server):
        changed = False

        self.params['meta'] = _parse_meta(self.params['meta'])

        # self.conn.set_server_metadata only updates the key=value pairs, it doesn't
        # touch existing ones
        update_meta = {}
        for (k, v) in self.params['meta'].items():
            if k not in server.metadata or server.metadata[k] != v:
                update_meta[k] = v

        if update_meta:
            self.conn.set_server_metadata(server, update_meta)
            changed = True
            # Refresh server vars
            server = self.conn.get_server(self.params['name'])

        return (changed, server)

    def _delete_server(self):
        try:
            self.conn.delete_server(
                self.params['name'], wait=self.params['wait'],
                timeout=self.params['timeout'],
                delete_ips=self.params['delete_fip'])
        except Exception as e:
            self.fail(msg="Error in deleting vm: %s" % e)
        self.exit(changed=True, result='deleted')

    def _network_args(self):
        args = []
        nics = self.params['nics']

        if not isinstance(nics, list):
            self.fail(msg='The \'nics\' parameter must be a list.')

        for num, net in enumerate(_parse_nics(nics)):
            if not isinstance(net, dict):
                self.fail(
                    msg='Each entry in the \'nics\' parameter must be a dict.')

            if net.get('net-id'):
                args.append(net)
            elif net.get('net-name'):
                by_name = self.conn.get_network(net['net-name'])
                if not by_name:
                    self.fail(
                        msg='Could not find network by net-name: %s' %
                        net['net-name'])
                resolved_net = net.copy()
                del resolved_net['net-name']
                resolved_net['net-id'] = by_name['id']
                args.append(resolved_net)
            elif net.get('port-id'):
                args.append(net)
            elif net.get('port-name'):
                by_name = self.conn.get_port(net['port-name'])
                if not by_name:
                    self.fail(
                        msg='Could not find port by port-name: %s' %
                        net['port-name'])
                resolved_net = net.copy()
                del resolved_net['port-name']
                resolved_net['port-id'] = by_name['id']
                args.append(resolved_net)

            if 'tag' in net:
                args[num]['tag'] = net['tag']
        return args

    def _detach_ip_list(self, server, extra_ips):
        for ip in extra_ips:
            ip_id = self.conn.get_floating_ip(
                id=None, filters={'floating_ip_address': ip})
            self.conn.detach_ip_from_server(
                server_id=server.id, floating_ip_id=ip_id)

    def _check_ips(self, server):
        changed = False

        auto_ip = self.params['auto_ip']
        floating_ips = self.params['floating_ips']
        floating_ip_pools = self.params['floating_ip_pools']

        if floating_ip_pools or floating_ips:
            ips = openstack_find_nova_addresses(server.addresses, 'floating')
            if not ips:
                # If we're configured to have a floating but we don't have one,
                # let's add one
                server = self.conn.add_ips_to_server(
                    server,
                    auto_ip=auto_ip,
                    ips=floating_ips,
                    ip_pool=floating_ip_pools,
                    wait=self.params['wait'],
                    timeout=self.params['timeout'],
                )
                changed = True
            elif floating_ips:
                # we were configured to have specific ips, let's make sure we have
                # those
                missing_ips = []
                for ip in floating_ips:
                    if ip not in ips:
                        missing_ips.append(ip)
                if missing_ips:
                    server = self.conn.add_ip_list(server, missing_ips,
                                                   wait=self.params['wait'],
                                                   timeout=self.params['timeout'])
                    changed = True
                extra_ips = []
                for ip in ips:
                    if ip not in floating_ips:
                        extra_ips.append(ip)
                if extra_ips:
                    self._detach_ip_list(server, extra_ips)
                    changed = True
        elif auto_ip:
            if server['interface_ip']:
                changed = False
            else:
                # We're configured for auto_ip but we're not showing an
                # interface_ip. Maybe someone deleted an IP out from under us.
                server = self.conn.add_ips_to_server(
                    server,
                    auto_ip=auto_ip,
                    ips=floating_ips,
                    ip_pool=floating_ip_pools,
                    wait=self.params['wait'],
                    timeout=self.params['timeout'],
                )
                changed = True
        return (changed, server)

    def _check_security_groups(self, server):
        changed = False

        # server security groups were added to shade in 1.19. Until then this
        # module simply ignored trying to update security groups and only set them
        # on newly created hosts.
        if not (
            hasattr(self.conn, 'add_server_security_groups')
            and hasattr(self.conn, 'remove_server_security_groups')
        ):
            return changed, server

        module_security_groups = set(self.params['security_groups'])
        server_security_groups = set(sg['name'] for sg in server.security_groups)

        add_sgs = module_security_groups - server_security_groups
        remove_sgs = server_security_groups - module_security_groups

        if add_sgs:
            self.conn.add_server_security_groups(server, list(add_sgs))
            changed = True

        if remove_sgs:
            self.conn.remove_server_security_groups(server, list(remove_sgs))
            changed = True

        return (changed, server)


def main():
    module = ServerModule()
    module()


if __name__ == '__main__':
    main()
