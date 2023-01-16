# Development Guide for Ansible OpenStack Collection

Ansible OpenStack collection is a set of Ansible modules for interacting with the OpenStack API as either an admin or an
end user.

We, and the OpenStack community in general, use OpenDev for its development. Patches are submitted to [OpenDev Gerrit][
opendev-gerrit]. Pull requests submitted through GitHub will be ignored. Please read OpenStack's [Developer Workflow][
openstack-developer-workflow] for details.

For hacking on the Ansible OpenStack collection it helps to [prepare a DevStack environment](devstack.md) first.

## Hosting

* [Bug tracker][storyboard]
* [Mailing list `openstack-discuss@lists.openstack.org`][openstack-discuss].
  Prefix subjects with `[aoc]` or `[aco]` for faster responses.
* [Code Hosting][opendev-a-c-o]
* [Code Review][gerrit-a-c-o]

## Branches

For rationale behind our `master` and `stable/1.0.0` branches and details on our relation to [openstacksdk][
openstacksdk], please read our [branching docs](branching.md).

## Examples

* For an example on how to write a `*_info` module, have a look at modules [`openstack.cloud.identity_role_info`](
  ../plugins/modules/identity_role_info.py) or [`openstack.cloud.neutron_rbac_policies_info`](
  ../plugins/modules/neutron_rbac_policies_info.py).
* For an example on how to write a regular non-`*_info` module, have a look at module
  [`openstack.cloud.federation_idp`](../plugins/modules/federation_idp.py) or any other module which uses
  [`class StateMachine`](../plugins/module_utils/resource.py).
* Do NOT use modules which define a `_system_state_change` function as examples, because they often do not properly
  define Ansible's check mode, idempotency and/or updates. Refer to modules which use [`class StateMachine`](
  ../plugins/module_utils/resource.py). In cases where using `class StateMachine` would cause code bloat, it might help
  to look at modules which define a `_will_change` function instead.

## Naming

* This collection is named `openstack.cloud`. There is no need for further namespace prefixing.
* Name any module that a cloud consumer would expect from [openstackclient (OSC)][openstackclient], for example `server`
  instead of `nova`. This naming convention acknowledges that the end user does not care which service manages the
  resource - that is a deployment detail. For example, cloud consumers may not know whether their floating ip address
  are managed by Nova or Neutron.

## Interface

* If the resource being managed has an `id`, it should be returned.
* If the resource being managed has an associated object more complex than an `id`, that should be returned instead of
  the `id`.
* Modules should return a value of type `dict`, `list` or other primitive data types. For example, `floating_ips` in
  `self.exit_json(changed=False, floating_ips=floating_ips)` should to be a list of `dict`s. Use `to_dict()` on
  [openstacksdk][openstacksdk] objects to convert resources to dictionaries. Setting its parameters such as `computed`
  to `False` will drop computed attributes from the resulting dict. Read [`to_dict`'s docstring][openstacksdk-to-dict]
  for more parameters.
* Module results have to be documented in `RETURN` docstring.
* We should document which attribute cannot be updated in `DOCUMENTATION` variable. For example, insert
  `'This attribute cannot be updated.'` to `DOCUMENTATION` like we did for the `server` module and others.
* Sorting module options in `DOCUMENTATION`, attributes in `RETURN`, entries in `argument_spec` and expected fields in
  integration tests will make reviewing easier and faster.

## Interoperability

* It should be assumed that the cloud consumer does not know details about the deployment choices their cloud provider
  made. A best effort should be made to present one sane interface to the Ansible user regardless of deployer choices.
* It should be assumed that a user may have more than one cloud account that they wish to combine as part of a single
  Ansible-managed infrastructure.
* All modules should work appropriately against all existing versions of OpenStack regardless of upstream EOL status.
  The reason for this is that the Ansible modules are for consumers of cloud APIs who are not in a position to impact
  what version of OpenStack their cloud provider is running. It is known that there are OpenStack Public Clouds running
  rather old versions of OpenStack, but from a user point of view the Ansible modules can still support these users
  without impacting use of more modern versions.

## Coding Guidelines

* Modules should
  + be idempotent (not being idempotent requires a solid reason),
  + return whether something has `changed`,
  + support `check mode`,
  + be based on (be subclasses of) `OpenStackModule` in
    `ansible_collections.openstack.cloud.plugins.module_utils.openstack`,
  + should include `extends_documentation_fragment: openstack` in their  `DOCUMENTATION` docstring,
  + be registered in `meta/action_groups.yml` for enabling the variables to be set in
    [group level][ansible-module-defaults].
* Complex functionality, cloud interaction or interoperability code should be moved to [openstacksdk][openstacksdk].
* OpenStack API interactions should happen via [openstacksdk][openstacksdk] and not via OpenStack component libraries.
  The OpenStack component libraries do no have end users as a primary audience, they are for intra-server communication.
* When a resource exist and should be deleted (absent), then pass the resource to the `delete_*` function, not its name.
  Passing a name requires openstacksdk to find that resource again, doing a unnecessary api call, because we queried the
  resource before.
* `*_info` modules never raise exceptions when resources cannot be found. When resources cannot be found, then a
  `*_info` module returns an empty list instead. For example, module `openstack.cloud.neutron_rbac_policies_info` will
  return an empty list when no project with name given in module parameter `project` can be found.
* When a id is given in `*_info` modules, then we do not need nor want extra code to handle that. Instead most
  [openstacksdk][openstacksdk] resources allow to pass ids as query arguments to OpenStack API. For example,
  `identity.identity_providers()` can be used for both cases: Where an id is given and where no id is given. No need to
  call `get_identity_provider()`.
* `EXAMPLES` docstring in modules (and Ansible's own modules) consist of a list of tasks. They do not contain YAML
  directives end marker line (---) and do not define playbooks (e.g. hosts keyword). They shall be simple, e.g. do not
  do fancy loops, heavy use of variables or use Ansible directives for no apparent reason such as ignore_errors or
  register.
* `self.params.get('...')` can be replaced with `self.params['...']` because parameters from `argument_spec` will always
  be in `self.params`. If not defined differently, they have a default value of `None`.
* Writing code to check that some options cannot be updated and to fail if user still tries to update that value is most
  often not worth it. It would require much more code to catch all cases where updates are impossible and we would have
  to implement it consistently across modules. Atm we are fine with documenting which attribute cannot be updated in
  `DOCUMENTATION` variable. We could simply drop these checks and insert `'This attribute cannot be updated.'` to
  `DOCUMENTATION` like we did for the server module and others.
* [openstacksdk][openstacksdk] functions often accept IDs but no names, e.g. `find_address_scope()` and
  `create_address_scope()` accept a `project_id` parameter. Most modules in our collection use names for finding
  resources, so we want to support the same for resources attributes such as `project_id` in `AddressScope`.
* Constraints for module parameters and error handling can often be implemented in `argument_spec` or `module_kwargs`
  `module_kwargs` allows to define dependencies between module options such as [`mutually_exclusive`,
  `required_together`, `required_if` etc.][ansible-argument-spec-dependencies].
* When using [openstacksdk][openstacksdk]'s `find_*` functions (`self.conn.*.find_*`), then pass `ignore_missing=False`
  instead of checking its return value and failing with `self.fail_json()` if it is `None`.
* Use module option names which match attribute names used in [openstacksdk][openstacksdk], e.g. use `is_shared` instead
  of `shared`. When refactoring modules, keep old option names as aliases to keep backward compatibility. Using
  openstacksdk names provides two benefits:
  - The module inputs and outputs do match, are consistent and thus the module is easier to use.
  - Most code for filters and query arguments can be replaced with loops. [This patch for floating_ip_info has some
    ideas for how to write loops](https://review.opendev.org/c/openstack/ansible-collections-openstack/+/828613).
* Use functions from [openstacksdk][openstacksdk]'s proxy layer instead of its cloud layer, if possible. For example,
  use `self.conn.network.find_network()`, not `self.conn.get_network()`. As a guideline use this decision tree:
  - If a functionality requires a single api call (to the OpenStack API), then use functions from openstacksdk's proxy
    layer.
  - If a functionality requires several api calls (to the OpenStack API), e.g. when creating and attaching a floating ip
    to a server, then use functions from openstacksdk's cloud layer.
  - When unsure which of openstacksdk's layers to use, then first go to proxy layer, then to its cloud layer and if this
    is not sufficient, then use its resource layer. Mainly, this applies to functions retrieving information, i.e. all
    calls where we get info about cloud resources should be changed to openstacksdk functions which return proxy
    resources.
  - It is perfectly fine to use openstacksdk's cloud layer for functionality which is not provided by openstacksdk's
    proxy layer. [SDK's cloud layer is not going away][openstacksdk-cloud-layer-stays].
    For example, `list_*` functions from openstacksdk's cloud layer such as `search_users()` allow to filter retrieved
    results with function parameter `filters`. openstacksdk's proxy layer does not provide an equivalent and thus the
    use of `search_users()` is perfectly fine.

## Testing

* Modules have to be tested with CI integration tests (if possible).
* Each module has a corresponding Ansible role containing integration tests in [`ci/roles`](../ci/roles) directory.
* Ensure role names of integration tests in [`ci/roles`](../ci/roles) match the module names.
  Only exception are `*_info` modules: Their integration tests are located in the same Ansible roles as their
  non-`*_info` equivalents (to reduce redundant code). For example, tests for both modules `federation_mapping` and
  `federation_mapping_info` can be found in role `federation_mapping`.
* Zuul CI jobs are defined in [`.zuul.yaml`](../.zuul.yaml).
* Add assertions on return values from Ansible modules in integration tests. For an example, refer to
  [`ci/roles/floating_ip/tasks/main.yml`](../ci/roles/floating_ip/tasks/main.yml).
  We need those checks to validate return values from [openstacksdk][openstacksdk], which might change across releases.
  Adding those assertions will be done in minutes, while checking the output manually during code reviews takes much
  more time.
* Our Zuul CI jobs will run `ansible-test` for sanity checking.
* Use `tox -elinters_latest` to run various linters against your code.

## Upload

* Study our [Review Guidelines](reviewing.md) before submitting a patch.
* Use Gerrit's work-in-progress feature to mark the status of the patch. A minus workflow (-w) will be reset when a new
  patchset is uploaded and hence easy to miss.
* When you edit a patch, first rebase your patch on top of the current branch. Sometimes we replace code in all modules
  which might cause merge conflicts for you otherwise. For example, we dropped all options with default values from
  `argument_spec` such as `required=False`.

## Release

Read [Release Guide](releasing.md) on how to publish new releases.

## Permissions

* Only [members of group `ansible-collections-openstack-core`][group-a-c-o-core] are allowed to merge patches.
* Only [members of group `ansible-collections-openstack-release`][group-a-c-o-release] are allowed to push tags and
  trigger our release job `ansible-collections-openstack-release` in [galaxy.yml](../galaxy.yml).
* Only members of `openstack` namespace in Ansible Galaxy are allowed to apply changes to meta properties of Ansible
  collection [`openstack.cloud`][ansible-galaxy-openstack-cloud] on Ansible Galaxy.

[ansible-argument-spec-dependencies]: https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html#argument-spec-dependencies
[ansible-galaxy-openstack-cloud]: https://galaxy.ansible.com/openstack/cloud
[ansible-module-defaults]: https://docs.ansible.com/ansible/latest/user_guide/playbooks_module_defaults.html
[gerrit-a-c-o]: https://review.opendev.org/q/status:open+project:openstack/ansible-collections-openstack
[group-a-c-o-core]: https://review.opendev.org/admin/groups/0e01228e912733e8b9a8d957631e41665aa0ffbd,members
[group-a-c-o-release]: https://review.opendev.org/admin/groups/8bca2018f3710f94374aee4b3c9771b9ff0a2254,members
[opendev-a-c-o]: https://opendev.org/openstack/ansible-collections-openstack
[opendev-gerrit]: https://review.opendev.org/
[openstack-developer-workflow]: https://docs.openstack.org/infra/manual/developers.html#development-workflow
[openstack-discuss]: http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-discuss
[openstackclient]: https://docs.openstack.org/python-openstackclient/latest/
[openstacksdk-cloud-layer-stays]: https://meetings.opendev.org/irclogs/%23openstack-sdks/%23openstack-sdks.2022-04-27.log.html
[openstacksdk-to-dict]: https://opendev.org/openstack/openstacksdk/src/branch/master/openstack/resource.py
[openstacksdk]: https://opendev.org/openstack/openstacksdk
[storyboard]: https://storyboard.openstack.org/#!/project/openstack/ansible-collections-openstack
