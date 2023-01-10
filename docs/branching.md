# Ansible OpenStack Collection and its branches

Our codebase has been split into two separate release series, `2.x.x` and `1.x.x`:

* `2.x.x` releases of Ansible OpenStack collection are compatible with [OpenStack SDK][openstacksdk] `1.x.x` and its
  release candidates `0.99.0` and later *only* (OpenStack Zed and later). Our [`master` branch][a-c-o-branch-master]
  tracks our `2.x.x` releases.
* `1.x.x` releases of Ansible OpenStack collection are compatible with [OpenStack SDK][openstacksdk] `0.x.x` prior to
  `0.99.0` *only* (OpenStack Yoga and earlier). Our [`stable/1.0.0` branch][a-c-o-branch-stable-1-0-0] tracks our
  `1.x.x` releases.
* `2.x.x` releases of Ansible OpenStack collection are not backward compatible to `1.x.x` releases ⚠️

Both branches will be developed in parallel for the time being. Patches from `master` will be backported to
`stable/1.0.0` on a best effort basis but expect new features to be introduced in our `master` branch only.
Contributions are welcome for both branches!

Our decision to break backward compatibility was not taken lightly. OpenStack SDK's first major release (`1.0.0` and its
release candidates >=`0.99.0`) has streamlined and improved large parts of its codebase. For example, its Connection
interface now consistently uses the Resource interfaces under the hood. [This required breaking changes from older SDK
releases though][openstacksdk-release-notes-zed]. The Ansible OpenStack collection is heavily based on OpenStack SDK.
With OpenStack SDK becoming backward incompatible, so does our Ansible OpenStack collection. For example, with
openstacksdk `>=0.99.0` most Ansible modules return dictionaries instead `Munch` objects and many of their keys have
been renamed. We simply lack the development resources to maintain a backward compatible interface in Ansible OpenStack
collection across several SDK releases.

[a-c-o-branch-master]: https://opendev.org/openstack/ansible-collections-openstack/src/branch/master
[a-c-o-branch-stable-1-0-0]: https://opendev.org/openstack/ansible-collections-openstack/src/branch/stable/1.0.0
[ansible-tags]: https://docs.ansible.com/ansible/latest/user_guide/playbooks_tags.html
[openstacksdk-cloud-layer-stays]: https://meetings.opendev.org/irclogs/%23openstack-sdks/%23openstack-sdks.2022-04-27.log.html
[openstacksdk-release-notes-zed]: https://docs.openstack.org/releasenotes/openstacksdk/zed.html
[openstacksdk-to-dict]: https://opendev.org/openstack/openstacksdk/src/branch/master/openstack/resource.py
[openstacksdk]: https://opendev.org/openstack/openstacksdk

## Notable changes between release series 2.x.x and 1.x.x

When we ported our collection to [openstacksdk][openstacksdk] `>=0.99.0`, a series of changes were applied to our
`master` branch. We went through each module in our collection and did the following:

* Identify function calls which use [openstacksdk][openstacksdk]'s cloud layer, e.g. `self.conn.get_network()`. Change
  these calls to functions from openstacksdk's resource proxies, e.g. `self.conn.network.find_network()`, if possible.
  As a guideline use this decision tree:
  - If a functionality requires a single api call (to the OpenStack API), then use functions from openstacksdk's
    resource proxies.
  - If a functionality requires multiple api calls (to the OpenStack API), e.g. when creating and attaching a floating
    ip to a server, then use functions from openstacksdk's cloud layer.
  - When unsure which of openstacksdk's layers to use, then first go to resource proxies and then to its cloud layer.
    Mainly this applies to functions retrieving information, i.e. all calls where we get info about cloud resources
    should be changed to openstacksdk functions which return proxy resources.
  **Note**: Using openstacksdk's cloud layer for functionality which is not provided by openstacksdk's proxy layer is
  acceptable. [openstacksdk's cloud layer is not going away][openstacksdk-cloud-layer-stays]. For example, listing
  functions in openstacksdk's cloud layer such as `search_users()` often allow to filter results with function parameter
  `filters`. openstacksdk's proxy layer does not provide an equivalent and thus using `search_users()` is fine.
* Functions in openstacksdk's cloud layer often have different return values then pre-0.99.0 releases. When return
  values have changed in any of the functions which a module uses, update `RETURN` variable. If a module has no `RETURN`
  variable, define it.
* Only return data types such as lists or dictionaries to Ansible. For example, the return statement
  `self.exit_json(changed=False, floating_ips=floating_ips)` in module [`floating_ip_info`](
  ../plugins/modules/floating_ip_info.py) shall return a list of `dict`'s. Use openstacksdk's `to_dict` function to
  convert resources to dictionaries. Setting its parameters such as `computed` to `False` will drop computed attributes
  from the resulting dict. Read [`to_dict`'s docstring][openstacksdk-to-dict] for more parameters. Using `to_dict` might
  change the return values of your Ansible module. Please document changes to return values in `RETURN`.
* Older openstacksdk releases did not provide the `to_dict` function. We decided to allow breaking backward
  compatibility with release `2.x.x`, so workarounds such as `(o.to_dict() if hasattr(o, 'to_dict') else dict(o))` are
  not required anymore and shall be avoided.
* Manually dropping attributes such as `location` or `link` from openstacksdk resources is no longer necessary.
  Workarounds such as
  ```Python
  for raw in self.conn.block_storage.backups(**attrs):
    dt = raw.to_dict()
    dt.pop('location')
    data.append(dt)
  ```
  are no longer necessary and can be removed.
* Add tests to [ci/run-collection.yml](../ci/run-collection.yml) and [ci/roles](../ci/roles). Each module has a
  dedicated Ansible role with tests in `ci/roles`. Create one if no such directory exist.
* With release of openstacksdk 0.99.0 most of our CI tests in [ci/](../ci/) failed. To prove that module patches
  actually fix issues all CI tests for unrelated broken modules have to be skipped. To run CI tests for patched modules
  only, temporarily list the [Ansible tags][ansible-tags] of all CI tests which should run in
  `vars: { tox_extra_args: ... }` of job `ansible-collections-openstack-functional-devstack-ansible` in `.zuul.yaml`
  ([example](https://review.opendev.org/c/openstack/ansible-collections-openstack/+/825291/16/.zuul.yaml)) and send the
  patch for review. Once all CI tests are passing in Zuul CI, undo changes to [`.zuul.yaml`](../.zuul.yaml), i.e. revert
  changes to `tox_extra_args` and submit final patch for review.
* ~~Cherry-pick or backport patches for `master` branch to `stable/1.0.0` branch. Both branches should divert only if
  necessary in order to keep maintainence of two separate branches simple. When applying patches to the `stable/1.0.0`
  branch, it is often necessary to make changes to not break backward compatibility on the `stable/1.0.0` branch. On
  `master` we use `.to_dict(computed=False)` which we have to change to `.to_dict(computed=True)` on `stable/1.0.0`. For
  example, this [patch for `master` branch](
  https://review.opendev.org/c/openstack/ansible-collections-openstack/+/828108) has been [tweaked and cherry-picked to
  `stable/1.0.0` branch](https://review.opendev.org/c/openstack/ansible-collections-openstack/+/836312).~~
  Backporting patches from `master` to `stable/1.0.0` branch have been abandoned due to lack of time and resources ⚠️
* Version checks in modules are no longer necessary because we require openstacksdk >=0.99.0 globally. For example,
  drop `min_ver`/`max_ver` constraints on module arguments.
* Rename module parameter names to the attribute names that openstacksdk uses, e.g. `shared` becomes `is_shared`. Keep
  old names as aliases for input backward compatibility.
* Some modules have if-else branches for handling cases where a `name` is given. For most modules these can be dropped
  safely because names can be passed as a query parameter.
* Some modules do not use `name` as module parameters for resource names. For example, `port` module had an attribute
  called `port` instead of `name`. Rename those attributes to `name` to be consistent with other modules and because
  openstacksdk is doing the same. Add old attribute names as aliases to keep input backward compatibility.
* Replacing `self.conn.get_*` with `self.conn.*.find_*` functions provide a `ignore_missing=False` parameter. This
  allows to drop `self.fail_json()` calls in modules. Less code means less to maintain.
* Some modules pass `ignore_missing=True` to `self.conn.*.find_*` functions and then fail if the return value is `None`.
  Often this code can be simplified by changing `ignore_missing` to `False` and dropping the if-else branches.
* When module attribute that have choices, always doubt its values. The module code was probably written long ago and
  the choices given might be outdated. It might also make sense to drop the `choices` parameter completely when choices
  are to narrow and might soon be outdated again.
* Check comments whether they are still relevant.
* Sanity check existing integration tests. For example, return values of module calls should be tested else running a
  test could be useless in the first place.
* Most functions in openstacksdk's cloud layer no longer return `Munch` objects. Instead they return resources which
  should be converted to dictionaries. Update `RETURN` docs in modules, e.g. change from `type: complex` to
  `type: dict`.
* Move list of expected module results to role defaults, e.g. define a variable `expected_fields`. This enables easier
  reuse.
* Following and applying our [development guide](contributing.md) and [review guide](reviewing.md)
