#!/usr/bin/python

# Copyright (c) 2018 Catalyst IT Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: coe_cluster_template
short_description: Manage COE cluster template in OpenStack Cloud
author: OpenStack Ansible SIG
description:
  - Add or remove a COE (Container Orchestration Engine) cluster template
    via OpenStack's Magnum aka Container Infrastructure Management API.
options:
  coe:
    description:
      - The Container Orchestration Engine for this cluster template
      - Required if I(state) is C(present).
    choices: [kubernetes, swarm, mesos]
    type: str
  dns_nameserver:
    description:
      - The DNS nameserver address.
      - Magnum's default value for I(dns_nameserver) is C(8.8.8.8).
    type: str
  docker_storage_driver:
    description:
      - Docker storage driver.
    choices: [devicemapper, overlay, overlay2]
    type: str
  docker_volume_size:
    description:
      - The size in GB of the docker volume.
    type: int
  external_network_id:
    description:
      - The external network to attach to the cluster.
      - When I(floating_ip_enabled) is set to C(true), then
        I(external_network_id) must be defined.
    type: str
  fixed_network:
    description:
      - The fixed network name or id to attach to the cluster.
    type: str
  fixed_subnet:
    description:
      - The fixed subnet name or id to attach to the cluster.
    type: str
  flavor_id:
    description:
      - The flavor of the minion node for this cluster template.
    type: str
  floating_ip_enabled:
    description:
      - Indicates whether created clusters should have a floating ip or not.
      - When I(floating_ip_enabled) is set to C(true), then
        I(external_network_id) must be defined.
    type: bool
    default: true
  keypair_id:
    description:
      - Name or ID of the keypair to use.
    type: str
  image_id:
    description:
      - Image id the cluster will be based on.
      - Required if I(state) is C(present).
    type: str
  labels:
    description:
      - One or more key/value pairs.
    type: raw
  http_proxy:
    description:
      - Address of a proxy that will receive all HTTP requests and relay them.
      - The format is a URL including a port number.
    type: str
  https_proxy:
    description:
      - Address of a proxy that will receive all HTTPS requests and relay them.
      - The format is a URL including a port number.
    type: str
  master_flavor_id:
    description:
      - The flavor of the master node for this cluster template.
    type: str
  master_lb_enabled:
    description:
      - Indicates whether created clusters should have a load balancer
        for master nodes or not.
      - Magnum's default value for I(master_lb_enabled) is C(true),
        ours is C(false).
    type: bool
    default: false
  name:
    description:
      - Name that has to be given to the cluster template.
    required: true
    type: str
  network_driver:
    description:
      - The name of the driver used for instantiating container networks.
    choices: [flannel, calico, docker]
    type: str
  no_proxy:
    description:
      - A comma separated list of IPs for which proxies should not be
        used in the cluster.
    type: str
  public:
    description:
      - Indicates whether the cluster template is public or not.
      - Magnum's default value for I(public) is C(false).
    type: bool
  registry_enabled:
    description:
      - Indicates whether the docker registry is enabled.
      - Magnum's default value for I(registry_enabled) is C(false).
    type: bool
  server_type:
    description:
      - Server type for this cluster template.
      - Magnum's default value for I(server_type) is C(vm).
    choices: [vm, bm]
    type: str
  state:
    description:
      - Indicate desired state of the resource.
    choices: [present, absent]
    default: present
    type: str
  tls_disabled:
    description:
      - Indicates whether the TLS should be disabled.
      - Magnum's default value for I(tls_disabled) is C(false).
    type: bool
  volume_driver:
    description:
      - The name of the driver used for instantiating container volumes.
    choices: [cinder, rexray]
    type: str
notes:
  - Return values of this module are preliminary and will most likely change
    when openstacksdk has finished its transition of cloud layer functions to
    resource proxies.
requirements:
  - "python >= 3.6"
  - "openstacksdk"
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

RETURN = r'''
id:
  description: The cluster UUID.
  returned: On success when I(state) is C(present).
  type: str
  sample: "39007a7e-ee4f-4d13-8283-b4da2e037c69"
cluster_template:
  description: Dictionary describing the template.
  returned: On success when I(state) is C(present).
  type: complex
  contains:
    apiserver_port:
      description: The exposed port of COE API server.
      type: int
    cluster_distro:
      description: Display the attribute os_distro defined as appropriate
                   metadata in image for the bay/cluster driver.
      type: str
    coe:
      description: The Container Orchestration Engine for this cluster
                   template.
      type: str
      sample: kubernetes
    created_at:
      description: The date and time when the resource was created.
      type: str
    dns_nameserver:
      description: The DNS nameserver address
      type: str
      sample: '8.8.8.8'
    docker_volume_size:
      description: The size in GB of the docker volume
      type: int
      sample: 5
    external_network_id:
      description: The external network to attach to the cluster
      type: str
      sample: public
    fixed_network:
      description: The fixed network name to attach to the cluster
      type: str
      sample: 07767ec6-85f5-44cb-bd63-242a8e7f0d9d
    fixed_subnet:
      description: The fixed subnet name to attach to the cluster.
      type: str
      sample: 05567ec6-85f5-44cb-bd63-242a8e7f0d9d
    flavor_id:
      description: The flavor of the minion node for this cluster template.
      type: str
      sample: c1.c1r1
    floating_ip_enabled:
      description: Indicates whether created clusters should have a
                   floating ip or not.
      type: bool
      sample: true
    http_proxy:
      description: Address of a proxy that will receive all HTTP requests
                   and relay them. The format is a URL including a port
                   number.
      type: str
      sample: http://10.0.0.11:9090
    https_proxy:
      description: Address of a proxy that will receive all HTTPS requests
                   and relay them. The format is a URL including a port
                   number.
      type: str
      sample: https://10.0.0.10:8443
    id:
      description: The UUID of the cluster template.
      type: str
    image_id:
      description: Image id the cluster will be based on.
      type: str
      sample: 05567ec6-85f5-44cb-bd63-242a8e7f0e9d
    insecure_registry:
      description: "The URL pointing to users's own private insecure docker
                    registry to deploy and run docker containers."
      type: str
    is_public:
      description: Access to a baymodel/cluster template is normally limited to
                   the admin, owner or users within the same tenant as the
                   owners. Setting this flag makes the baymodel/cluster
                   template public and accessible by other users. The default
                   is not public.
      type: bool
    is_registry_enabled:
      description: "Docker images by default are pulled from the public Docker
                    registry, but in some cases, users may want to use a
                    private registry. This option provides an alternative
                    registry based on the Registry V2: Magnum will create a
                    local registry in the bay/cluster backed by swift to host
                    the images. The default is to use the public registry."
      type: bool
    is_tls_disabled:
      description: Transport Layer Security (TLS) is normally enabled to secure
                   the bay/cluster. In some cases, users may want to disable
                   TLS in the bay/cluster, for instance during development or
                   to troubleshoot certain problems. Specifying this parameter
                   will disable TLS so that users can access the COE endpoints
                   without a certificate. The default is TLS enabled.
      type: bool
    keypair_id:
      description: Name or ID of the keypair to use.
      type: str
      sample: mykey
    labels:
      description: One or more key/value pairs.
      type: dict
      sample: {'key1': 'value1', 'key2': 'value2'}
    location:
      description: The OpenStack location of this resource.
      type: str
    master_flavor_id:
      description: The flavor of the master node for this cluster template.
      type: str
      sample: c1.c1r1
    master_lb_enabled:
      description: Indicates whether created clusters should have a load
                   balancer for master nodes or not.
      type: bool
      sample: true
    name:
      description: Name that has to be given to the cluster template.
      type: str
      sample: k8scluster
    network_driver:
      description:
        - The name of the driver used for instantiating container networks
      type: str
      sample: calico
    no_proxy:
      description: A comma separated list of IPs for which proxies should
                   not be used in the cluster.
      type: str
      sample: 10.0.0.4,10.0.0.5
    properties:
      description: Additional properties of the cluster template.
      type: dict
      sample: |
        {
          "docker_storage_driver": null,
          "hidden": false,
          "master_lb_enabled": false,
          "project_id": "8fb245a1bd714d9a82e419f2b7bb69dd",
          "tags": null,
          "user_id": "51510ce12e294d5d9c7391bececcd1e8"
        }
    public:
      description: Access to a baymodel/cluster template is normally limited
                   to the admin, owner or users within the same tenant as the
                   owners. Setting this flag makes the baymodel/cluster
                   template public and accessible by other users. The default
                   is not public.
      type: bool
      sample: false
    registry_enabled:
      description: "Docker images by default are pulled from the public Docker
                    registry, but in some cases, users may want to use a
                    private registry. This option provides an alternative
                    registry based on the Registry V2: Magnum will create a
                    local registry in the bay/cluster backed by swift to host
                    the images. The default is to use the public registry."
      type: bool
      sample: false
    server_type:
      description: Server type for this cluster template.
      type: str
      sample: vm
    tls_disabled:
      description: Transport Layer Security (TLS) is normally enabled to secure
                   the bay/cluster. In some cases, users may want to disable
                   TLS in the bay/cluster, for instance during development or
                   to troubleshoot certain problems. Specifying this parameter
                   will disable TLS so that users can access the COE endpoints
                   without a certificate. The default is TLS enabled.
      type: bool
      sample: false
    updated_at:
      description: The date and time when the resource was updated.
      type: str
    uuid:
      description: The UUID of the cluster template.
      type: str
    volume_driver:
      description: The name of the driver used for instantiating container
                   volumes.
      type: str
      sample: cinder
'''

EXAMPLES = r'''
- name: Create a new Kubernetes cluster template
  openstack.cloud.coe_cluster_template:
    cloud: devstack
    coe: kubernetes
    image_id: 2a8c9888-9054-4b06-a1ca-2bb61f9adb72
    keypair_id: mykey
    name: k8s
    public: no
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class COEClusterTemplateModule(OpenStackModule):
    argument_spec = dict(
        coe=dict(choices=['kubernetes', 'swarm', 'mesos']),
        dns_nameserver=dict(),
        docker_storage_driver=dict(choices=['devicemapper', 'overlay',
                                            'overlay2']),
        docker_volume_size=dict(type='int'),
        external_network_id=dict(),
        fixed_network=dict(),
        fixed_subnet=dict(),
        flavor_id=dict(),
        floating_ip_enabled=dict(type='bool', default=True),
        http_proxy=dict(),
        https_proxy=dict(),
        image_id=dict(),
        keypair_id=dict(),
        labels=dict(type='raw'),
        master_flavor_id=dict(),
        master_lb_enabled=dict(type='bool', default=False),
        name=dict(required=True),
        network_driver=dict(choices=['flannel', 'calico', 'docker']),
        no_proxy=dict(),
        public=dict(type='bool'),
        registry_enabled=dict(type='bool'),
        server_type=dict(choices=['vm', 'bm']),
        state=dict(default='present', choices=['absent', 'present']),
        tls_disabled=dict(type='bool'),
        volume_driver=dict(choices=['cinder', 'rexray']),
    )
    module_kwargs = dict(
        required_if=[
            ('state', 'present', ('coe', 'image_id')),
        ],
        supports_check_mode=True,
    )

    def run(self):
        state = self.params['state']

        cluster_template = self._find()

        if self.ansible.check_mode:
            self.exit_json(changed=self._will_change(state, cluster_template))

        if state == 'present' and not cluster_template:
            # Create cluster_template
            cluster_template = self._create()
            self.exit_json(
                changed=True,
                # for backward compatibility
                id=cluster_template['id'],
                cluster_template=cluster_template)

        elif state == 'present' and cluster_template:
            # Update cluster_template
            update = self._build_update(cluster_template)
            if update:
                cluster_template = self._update(cluster_template, update)

            self.exit_json(
                changed=bool(update),
                # for backward compatibility
                id=cluster_template['id'],
                cluster_template=cluster_template)

        elif state == 'absent' and cluster_template:
            # Delete cluster_template
            self._delete(cluster_template)
            self.exit_json(changed=True)

        elif state == 'absent' and not cluster_template:
            # Do nothing
            self.exit_json(changed=False)

    def _build_update(self, cluster_template):
        update = {}

        if self.params['floating_ip_enabled'] \
           and self.params['external_network_id'] is None:
            raise ValueError('floating_ip_enabled is True'
                             ' but external_network_id is missing')

        # TODO: Implement support for updates.
        non_updateable_keys = [k for k in ['coe', 'dns_nameserver',
                                           'docker_storage_driver',
                                           'docker_volume_size',
                                           'external_network_id',
                                           'fixed_network',
                                           'fixed_subnet', 'flavor_id',
                                           'floating_ip_enabled',
                                           'http_proxy', 'https_proxy',
                                           'image_id', 'keypair_id',
                                           'master_flavor_id',
                                           'master_lb_enabled', 'name',
                                           'network_driver', 'no_proxy',
                                           'public', 'registry_enabled',
                                           'server_type', 'tls_disabled',
                                           'volume_driver']
                               if self.params[k] is not None
                               and k in cluster_template
                               and self.params[k] != cluster_template[k]]

        labels = self.params['labels']
        if labels is not None:
            if isinstance(labels, str):
                labels = dict([tuple(kv.split(":"))
                               for kv in labels.split(",")])
            if labels != cluster_template['labels']:
                non_updateable_keys.append('labels')

        if non_updateable_keys:
            self.fail_json(msg='Cannot update parameters {0}'
                               .format(non_updateable_keys))

        attributes = dict((k, self.params[k])
                          for k in []
                          if self.params[k] is not None
                          and self.params[k] != cluster_template[k])

        if attributes:
            update['attributes'] = attributes

        return update

    def _create(self):
        if self.params['floating_ip_enabled'] \
           and self.params['external_network_id'] is None:
            raise ValueError('floating_ip_enabled is True'
                             ' but external_network_id is missing')

        # TODO: Complement *_id parameters with find_* functions to allow
        #       specifying names in addition to IDs.
        kwargs = dict((k, self.params[k])
                      for k in ['coe', 'dns_nameserver',
                                'docker_storage_driver', 'docker_volume_size',
                                'external_network_id', 'fixed_network',
                                'fixed_subnet', 'flavor_id',
                                'floating_ip_enabled', 'http_proxy',
                                'https_proxy', 'image_id', 'keypair_id',
                                'master_flavor_id', 'master_lb_enabled',
                                'name', 'network_driver', 'no_proxy', 'public',
                                'registry_enabled', 'server_type',
                                'tls_disabled', 'volume_driver']
                      if self.params[k] is not None)

        labels = self.params['labels']
        if labels is not None:
            if isinstance(labels, str):
                labels = dict([tuple(kv.split(":"))
                               for kv in labels.split(",")])
            kwargs['labels'] = labels

        return self.conn.create_cluster_template(**kwargs)

    def _delete(self, cluster_template):
        self.conn.delete_cluster_template(cluster_template.name)

    def _find(self):
        name = self.params['name']
        filters = {}

        image_id = self.params['image_id']
        if image_id is not None:
            filters['image_id'] = image_id

        coe = self.params['coe']
        if coe is not None:
            filters['coe'] = coe

        return self.conn.get_cluster_template(name_or_id=name,
                                              filters=filters,
                                              detail=True)

    def _update(self, cluster_template, update):
        attributes = update.get('attributes')
        if attributes:
            # TODO: Implement support for updates.
            # cluster_template = self.conn.update_cluster_template(...)
            pass

        return cluster_template

    def _will_change(self, state, cluster_template):
        if state == 'present' and not cluster_template:
            return True
        elif state == 'present' and cluster_template:
            return bool(self._build_update(cluster_template))
        elif state == 'absent' and cluster_template:
            return True
        else:
            # state == 'absent' and not cluster_template:
            return False


def main():
    module = COEClusterTemplateModule()
    module()


if __name__ == "__main__":
    main()
