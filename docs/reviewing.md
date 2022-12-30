# Reviews

How to do a review? What to look for when reviewing patches?

* Should functionality be implemented in Ansible modules or in openstacksdk? Ansible modules should only be "wrappers"
  for functionality in openstacksdk. Big code chunks are a good indicator that functionality should better be moved to
  openstacksdk.
* For each function call(s) and code section which has been refactored, does the new code return the same results?
  Pay special attention whenever a function from openstacksdk's cloud layer has been replaced because those functions
  often have different semantics than functions of SDK's proxy layer.
* Can API calls (to OpenStack API, not openstacksdk API) be reduced any further to improve performance?
* Can calls to OpenStack API be tweaked to return less data?
  For example, listing calls such as `image.images()` or `network.networks()` provide filters to reduce the number of
  returned values.
* Sanity check `argument_spec` and `module_kwargs`. Some modules try to be clever and add checks to fail early instead
  of letting `openstacksdk` or OpenStack API handle incompatible arguments.
* Are `choices` in module attributes apropriate? Sometimes it makes sense to get rid of the choices because the choices
  are simply to narrow and might soon be outdated again.
* Are `choices` in module attributes still valid? Module code might be written long ago and thus the choices might be
  horrible outdated.
* Does a module use `name` as module options for resource names instead of e.g. `port` in `port` module? Rename those
  attributes to `name` to be consistent with other modules and with openstacksdk. When refactoring a module, then add
  the old attribute as an alias to keep backward compatibility.
* Does the module have integration tests in `ci/roles`?
* Is documentation in `DOCUMENTATION`, `RETURN` and `EXAMPLES` up to date?
* Does `RETURN` list all values which are returned by the module?
* Are descriptions, keys, names, types etc. in `RETURN` up to date and sorted?
  - For example, [`type: complex` often can be changed to `type: list` / `elements: dict`](
    https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_documenting.html).
  - `returned: always, but can be null` often has to be changed to `returned: always, but can be empty` or shorter
    `returned: always`.
  - Are there any values in `RETURN` which are not returned by OpenStack SDK any longer?
  - Module return value documentation can be found in [OpenStack SDK docs](
    https://docs.openstack.org/openstacksdk/latest/), e.g. [Identity v3 API](
    https://docs.openstack.org/openstacksdk/latest/user/proxies/identity_v3.html).
    For more detailed descriptions on return values refer to [OpenStack API](https://docs.openstack.org/api-ref/).
* Do integration tests have assertions of module's return values?
* Does `RETURN` documentation and assertions in integration tests match?
* Does `RETURN` documentation and `self.exit_json()` statements match?
* Do all modules use `to_dict(computed=False)` before returning values?
* Because `id` is already part of most resource dictionaries returned from modules, we can safely drop dedicated `id`
  attributes in `self.exit_json()` calls. We will not loose data and we break backward compatibility anyway.
* Is `EXAMPLES` documentation up to date?
  When module arguments have been changed, examples have to be updated as well.
* Do integration tests execute successfully in your local dev environment? \
  Example:
  ```sh
  ansible-playbook -vvv ci/run-collection.yml \
      -e "sdk_version=1.0.0 cloud=devstack-admin cloud_alt=devstack-alt" \
      --tags floating_ip_info
  ```
* Does a patch remove any functionality or break backwards compatibility? The author must give a good explanation for
  both.
  - One valid reason is that a functionality has never worked before.
  - Not a valid reason for dropping functionality or backwards compatibility is that functions from openstacksdk's proxy
    layer do not support the functionality from openstacksdk's cloud layer. [SDK's cloud layer is not going away](
    https://meetings.opendev.org/irclogs/%23openstack-sdks/%23openstack-sdks.2022-04-27.log.html) and can be used for
    functionality which openstacksdk's proxy layer does not support. For example, `list_*` functions from openstacksdk's
    cloud layer such as `search_users()` allow to filter retrieved results with function parameter `filters`.
    openstacksdk's proxy layer does not provide an equivalent and thus the use of `search_users()` is perfectly fine.
* Try to look at the patch from user perspective:
  - Will users understand and approve the change(s)?
  - Will the patch break their code?
    **Note**: For operators / administrators, a stable and reliable and bug free API is more important than the number
    of features.
  - If a change breaks or changes the behavior of their code, will it be easy to spot the difference?
