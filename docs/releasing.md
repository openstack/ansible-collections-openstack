# Release process for Ansible OpenStack collection

## Publishing to Ansible Galaxy

1. Create entry in [changelog.yaml](../changelogs/changelog.yaml) with commits since last release.
   * Modules should be in a separate section `modules`
   * Bugfixes and minor changes in their sections
2. Change version in [galaxy.yml](../galaxy.yml). Apply [Semantic Versioning](https://semver.org/):
   * Increase major version for breaking changes or modules were removed
   * Increase minor version when modules were added
   * Increase patch version for bugfixes
3. Run `antsibull-changelog release` command (run `pip install antsibull` before) to generate [CHANGELOG.rst](
   ../CHANGELOG.rst) and verify correctness of generated files.
4. Commit changes to `changelog.yaml` and `galaxy.yml`, submit patch and wait until it has been merged
5. Tag the release with version as it's described in [OpenStack docs](
   https://docs.opendev.org/opendev/infra-manual/latest/drivers.html#tagging-a-release):
    * [Make sure you have a valid GnuPG key pair](
      https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key)
    * `git checkout <your_branch>`
    * `git pull --ff-only`
    * `git tag -s <version number>` where `<version number>` is your tag
    * `git push gerrit <version number>`
6. When your tag has been pushed in the previous step, our release job `ansible-collections-openstack-release`, defined
   in [galaxy.yml](../galaxy.yml), will run automatically and publish a new release with your tag to [Ansible Galaxy](
   https://galaxy.ansible.com/openstack/cloud). When it has finished, its status and logs can be accessed on [Zuul CI's
   builds page](https://zuul.opendev.org/t/openstack/builds?job_name=ansible-collections-openstack-release).
7. When release job `ansible-collections-openstack-release` has failed, you can manually build the collection locally
   and publish your release to Ansible Galaxy:
   * `git checkout <version number>` where `<version number>` is your tag
   * Delete untracked files and directories with `git clean -n; git clean -fd`
   * Build collection with `ansible-galaxy`, for example:
    ```sh
    ansible-galaxy collection build --force --output-path /path/to/collection/dir
    ```
   * On success you will find a `*.tar.gz` file in `/path/to/collection/dir`, e.g. `openstack-cloud-1.5.0.tar.gz`
   * Go to [your content page on Ansible Galaxy](https://galaxy.ansible.com/my-content/namespaces), open namespace
     `openstack`, click on `Upload New Version` and upload your release `*.tar.gz`, e.g. `openstack-cloud-1.5.0.tar.gz`.
     Push collection tarballs to the `openstack.cloud` namespace requires membership in `openstack` namespace on Ansible
     Galaxy.
   * Instead of using Ansible Galaxy web interface, you could also upload your release from cli. For example:
     ```sh
     ansible-galaxy collection publish --token $API_GALAXY_TOKEN -v /path/to/openstack-cloud-1.5.0.tar.gz
     ```
     where `$API_GALAXY_TOKEN` is your API key from [Ansible Galaxy](https://galaxy.ansible.com/me/preferences).
   * [Monitor import progress on Ansible Galaxy](https://galaxy.ansible.com/my-imports/) and act accordingly to issues.
8. Announce new release to [The Bullhorn](https://github.com/ansible/community/wiki/News#the-bullhorn): Join
   [Ansible Social room on Matrix](https://matrix.to/#/#social:ansible.com) and mention [newsbot](
   https://matrix.to/#/@newsbot:ansible.im) to have your news item tagged for review for the next issue!

## Publishing to Fedora

**NOTE:** Before publishing an updated RPM for Fedora or RDO, contact Alfredo Moralejo Alonso <amoralej@redhat.com>
(amoralej) or Joel Capitao <jcapitao@redhat.com> (jcapitao[m]) in `#rdo` on [OFTC IRC](https://www.oftc.net/) about the
latest release process.

**NOTE:** If your username is in Fedora's `admins` group, you can push your commit directly to Fedora's repository for
Ansible OpenStack collection. Otherwise you will have to open pull requests to sent changes.

1. Get familiar with packaging for Fedora. Useful resources are:
   * [Fedora's Package Update Guide](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Update_Guide/)
   * [Fedora package source for Ansible OpenStack collection](
     https://src.fedoraproject.org/rpms/ansible-collections-openstack)
   * [Koji page for `ansible-collections-openstack`](https://koji.fedoraproject.org/koji/packageinfo?packageID=33611)
   * [Bodhi's page `Create New Update`](https://bodhi.fedoraproject.org/updates/new)
2. Install all necessary packaging tools, mainly `fedpkg`.
3. Create a scratch space with `mkdir fedora-scm`.
4. Fork Fedora repository [rpms/ansible-collections-openstack](
   https://src.fedoraproject.org/rpms/ansible-collections-openstack).
5. Clone [rpms/ansible-collections-openstack](https://src.fedoraproject.org/rpms/ansible-collections-openstack) with
   `fedpkg clone rpms/ansible-collections-openstack`. Or clone your forked repository (something like
   `https://src.fedoraproject.org/fork/sshnaidm/rpms/ansible-collections-openstack`) with
   `fedpkg clone forks/sshnaidm/rpms/ansible-collections-openstack` where `sshnaidm` has to be replaced with your
   username.
6. `cd ansible-collections-openstack` and go to branch `rawhide` with `fedpkg switch-branch rawhide`.
7. Download new collection sources from Ansible Galaxy using
   `wget https://galaxy.ansible.com/download/openstack-cloud-<version_tag>.tar.gz` where `<version_tag>` is a your new
   version, e.g. `1.10.0`. Or run `spectool -g *.spec` *after* having changed the `*.spec` file in the next step.
8. Bump version in `*.spec` file as in this [example for `1.9.4`](
   https://src.fedoraproject.org/rpms/ansible-collection-containers-podman/c/6dc5eb79a3aa082e062768993bed66675ff9d520):
   ```diff
   +Version:        <version-tag>
   +Release:        1%{?dist}
   ```
  and add changelog, sort of:
  ```diff
  +* Tue Jun 08 2021 Sagi Shnaidman <sshnaidm@redhat.com> - <version-tag>-1
  +- Bump to <version-tag>-1
  ```
9. Upload sources you downloaded before with `fedpkg new-sources <version-tag>.tar.gz`.
10. Optionally check build with `fedpkg mockbuild`.
11. Verify and commit updated `*.spec` file with:
    ```sh
    fedpkg diff
    fedpkg lint # run linters against your changes
    fedpkg commit # with message such as 'Bumped Ansible OpenStack collection to <version-tag>'
    ```
12. Push changes for `rawhide` with `fedpkg push`.
13. Ask Koji to build your package with `fedpkg build`.
14. Optionally check [Koji's page for `ansible-collections-openstack`](
    https://koji.fedoraproject.org/koji/packageinfo?packageID=33611).
15. Repeat release process for older Fedora branches such as Fedora 36 aka `f36`:
    ```sh
    fedpkg switch-branch f36
    git merge rawhide
    fedpkg push
    fedpkg build
    fedpkg update # or use Bodhi's page "Create New Update" at https://bodhi.fedoraproject.org/updates/new
    ```

## Publishing to RDO

**NOTE:** Before publishing an updated RPM for Fedora or RDO, contact Alfredo Moralejo Alonso <amoralej@redhat.com>
(amoralej) or Joel Capitao <jcapitao@redhat.com> (jcapitao[m]) in `#rdo` on [OFTC IRC](https://www.oftc.net/) about the
latest release process.

[All `master` branches on RDO trunk](https://trunk.rdoproject.org) consume code from the `master` branch of the Ansible
OpenStack collection. Its RPM is (re)build whenever a new patch has been merged to the collection repository. Afterwards
[it is promoted as any other TripleO components in `client` component CI](
https://docs.openstack.org/tripleo-docs/latest/ci/stages-overview.html).

To update stable RDO branches such as [`CentOS 9 Zed`](https://trunk.rdoproject.org/centos9-zed/), patches have to be
submitted to CentOS Cloud SIG repositories. In this case, create a patch for stable branches such as `wallaby-rdo`, and
`ussuri-rdo` at [ansible-collections-openstack-distgit](
https://github.com/rdo-packages/ansible-collections-openstack-distgit). [Example](
https://review.rdoproject.org/r/c/openstack/ansible-collections-openstack-distgit/+/34282).
