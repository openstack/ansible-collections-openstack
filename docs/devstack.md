# Preparing a DevStack environment for Ansible collection development

For developing on the Ansible OpenStack collection, it helps to install DevStack and two Python [`virtualenv`][
virtualenv]s, one with [openstacksdk][openstacksdk] `<0.99.0` and one with [openstacksdk][openstacksdk] `>=1.0.0` (or
one of its release candidates `>=0.99.0`). The first is for patches against our `stable/1.0.0` branch of the collection,
while the newer openstacksdk is for patches against our `master` branch.

First, [follow DevStack's guide][devstack] to set up DevStack on a virtual machine. An Ansible inventory and a playbook
to set up your own local DevStack as a libvirt domain can be found in Ansible collection [`jm1.cloudy`][jm1-cloudy],
look for host `lvrt-lcl-session-srv-200-devstack`.

**Beware:** DevStack's purpose is to be set up quickly and destroyed after development or testing is done. It cannot
be rebooted safely or upgraded easily.

Some Ansible modules and unit tests in the Ansible OpenStack collection require additional DevStack plugins which
are not enabled by default. [Plugins are enabled in DevStack's `local.conf`][devstack-plugins]. Examples:

- Use the DevStack configuration which the Zuul CI jobs are applying when testing the Ansible OpenStack collection. For
  example, go to the logs of job [`ansible-collections-openstack-functional-devstack`][devstack-jobs] and use file
  `controller/logs/local_conf.txt` as your `local.conf` for DevStack.
- https://gist.github.com/sshnaidm/43ca23c3f23bd6015d18868ac7405a13
- https://paste.opendev.org/show/812460/

For a list of plugins refer to [DevStack's plugin registry][devstack-plugin-registry].

Next, prepare two Python [`virtualenv`][virtualenv]s, one with [openstacksdk][openstacksdk] `<0.99.0` and one with
[openstacksdk][openstacksdk] `>=1.0.0` (or one of its release candidates `>=0.99.0`):

```sh
# DevStack is presumed to be installed on the development machine
# and its configuration file available at ~/devstack/openrc

git clone https://opendev.org/openstack/ansible-collections-openstack.git
mkdir -p ~/.ansible/collections/ansible_collections/openstack/
ln -s ansible-collections-openstack ~/.ansible/collections/ansible_collections/openstack/cloud

# Prepare environment for developing patches against
# Ansible OpenStack collection 2.x.x and openstacksdk>=0.99.0
cd ansible-collections-openstack/
git checkout master
virtualenv -p python3 ~/.local/share/virtualenv/ansible-openstacksdk-1
source ~/.local/share/virtualenv/ansible-openstacksdk-1/bin/activate
pip install -r test-requirements.txt
pip install git+https://opendev.org/openstack/openstacksdk
pip install ipython
source ~/devstack/openrc admin admin
ipython

cd ..

# Prepare environment for developing patches against
# Ansible OpenStack collection 1.x.x and openstacksdk<0.99.0
virtualenv -p python3 ~/.local/share/virtualenv/ansible-openstacksdk-0
source ~/.local/share/virtualenv/ansible-openstacksdk-0/bin/activate
cd ansible-collections-openstack/
git checkout stable/1.0.0
pip install -r test-requirements.txt
pip install 'openstacksdk<0.99.0'
pip install ipython
source ~/devstack/openrc admin admin
ipython
```

The first IPython instance uses openstacksdk >=0.99.0 and is for developing at the 2.x.x series of the Ansible OpenStack
collection. The second IPython instance uses openstacksdk <0.99.0 and is suited for the 1.x.x series of the collection.
For example, type in each IPython instance:

```python
import openstack
conn = openstack.connect()

# optional
openstack.enable_logging(debug=True)

# and start hacking..
list(conn.network.ips())[0].to_dict(computed=False)
```

To run the unit tests of the collection, run this in a Bash shell:

```sh
SDK_VER=$(python -c "import openstack; print(openstack.version.__version__)")
ansible-playbook -vvv ci/run-collection.yml -e "sdk_version=${SDK_VER} cloud=devstack-admin cloud_alt=devstack-alt"
```

Use `ansible-playbook`'s `--tags` and `--skip-tags` parameters to skip CI tests. For a list of available tags, refer to
[`ci/run-collection.yml`](../ci/run-collection.yml).

Or run Ansible modules individually:

```sh
ansible localhost -m openstack.cloud.floating_ip -a 'server=ansible_server1 wait=true' -vvv
```

When submitting a patch with `git review`, our Zuul CI jobs will test your changes against different versions of
openstacksdk, Ansible and DevStack. Refer to [`.zuul.yaml`](../.zuul.yaml) for a complete view of all CI jobs. To
trigger experimental jobs, write a comment in Gerrit which contains `check experimental`.

Happy hacking!

[devstack-jobs]: https://zuul.opendev.org/t/openstack/builds?job_name=ansible-collections-openstack-functional-devstack&project=openstack/ansible-collections-openstack
[devstack-plugin-registry]: https://docs.openstack.org/devstack/latest/plugin-registry.html
[devstack-plugins]: https://docs.openstack.org/devstack/latest/plugins.html
[devstack]: https://docs.openstack.org/devstack/latest/
[jm1-cloudy]: https://github.com/JM1/ansible-collection-jm1-cloudy
[openstacksdk]: https://opendev.org/openstack/openstacksdk/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
