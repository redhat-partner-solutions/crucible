# Crucible: OpenShift 4 Management Cluster Seed Playbooks

> ❗ _Red Hat does not provide commercial support for the content of this repo.
Any assistance is purely on a best-effort basis, as resource permits._

```bash
#############################################################################
DISCLAIMER: THE CONTENT OF THIS REPO IS EXPERIMENTAL AND PROVIDED **"AS-IS"**

THE CONTENT IS PROVIDED AS REFERENCE WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#############################################################################
```

This repository contains playbooks for automating the creation of an OpenShift Container Platform cluster on premise using the Developer Preview version of the OpenShift Assisted Installer. The playbooks require only minimal infrastructure configuration and do not require any pre-existing cluster. Virtual and Bare Metal deployments have been tested in restricted network environments where nodes do not have direct access to the Internet.

These playbooks assume a prior working knowledge of [Ansible](http://www.ansible.com). They are intended to be run from a `bastion` host, running a subscribed installation of RHEL 8.4, inside the target environment. Pre-requisites can be installed manually or automatically, as appropriate.

See [how the playbooks are intended to be run](docs/connecting_to_hosts.md) and understand [what steps the playbooks take](docs/pipeline_into_the_details.md).


## Software Versions Supported
Crucible targets versions of Python and Ansible that ship with RHEL. At the moment the supported versions are:

- RHEL 8.3
- Python 3.6.8
- Ansible 2.9.27


## OpenShift Versions Tested

- 4.6
- 4.7
- 4.8


## Assisted Installer versions Tested

- v2.1.0
- v2.1.1
- v2.1.2


### Dependencies

Requires the following to be installed on the deployment host:

- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-specific-operating-systems)
- [netaddr](https://github.com/netaddr/netaddr)
- [jmespath](https://github.com/jmespath)
- [skopeo](https://github.com/containers/skopeo)
- [podman](https://github.com/containers/podman/)
- [kubectl + oc](https://docs.openshift.com/container-platform/4.9/cli_reference/openshift_cli/getting-started-cli.html)
- [pyghmi](https://pypi.org/project/pyghmi/) #For PXE deployment
- [ipmitool](https://github.com/ipmitool/ipmitool) #For PXE deployment


**Important Note** The `openshift-clients` package is part of the (Red Hat OpenShift Container Platform Subscription
)[https://access.redhat.com/downloads/content/290/]. The repo [must be activated on the bastion host](https://docs.openshift.com/container-platform/4.9/cli_reference/openshift_cli/getting-started-cli.html#cli-installing-cli-rpm_cli-developer-commands) before the dependency installation. It is used for the post-installation cluster validation steps.


```bash
dnf install ansible python3-netaddr skopeo podman openshift-clients ipmitool python3-pyghmi python3-jmespath
```

There's also some required Ansible modules that can be installed with the following command:

```bash
ansible-galaxy collection install -r requirements.yml
```


## Before Running The Playbook

- Configure NTP time sync on the BMCs and confirm the system clock among the master nodes is synchronized within a second. The installation fails when system time does not match among nodes because etcd database will not be able to converge.
- Modify the provided inventory file `inventory.yml.sample`. Fill in the appropriate values that suit your environment and deployment requirements. See the sample file and [docs/inventory.md](docs/inventory.md) for more details.
- Modify the provided inventory vault file `inventory.vault.yml.sample`. Fill in the corresponding secret values according to the configuration of the inventory file. See the sample file and [docs/inventory.md#required-secrets](docs/inventory.md#required-secrets) for more details.
- Place the following prerequisites in this directory:
  - OpenShift pull secret stored as `pull-secret.txt` (can be downloaded from [here](https://console.redhat.com/openshift/install/metal/installer-provisioned))
  - SSH Public Key stored as `ssh_public_key.pub`
  - If `deploy_prerequisites.yml` is NOT being used; SSL self-signed certificate stored as `mirror_certificate.txt`


### Inventory Vault File Management

The inventory vault files should be encrypted and protected at all times, as they may contain secret values and sensitive information. 

To encrypt a vault file named `inventory.vault.yml`, issue the following command.

```bash
ansible-vault encrypt inventory.vault.yml 
```

An encrypted vault file can be referenced when executing the playbooks with the `ansible-playbook` command.  
To that end, provide the option `-e "@{PATH_TO_THE_VAULT_FILE}"`.

To allow Ansible to read values from an encrypted vault file, a password for decrypting the vault must be provided. Provide the `--ask-vault-pass` flag to force Ansible to ask for a password to the vault before the selected playbook is executed.

A complete command to execute a playbook that takes advantage of both options can look like this:
```bash
ansible-playbook -i inventory.yml ${SELECTED_PLAYBOOK} -e "@inventory.vault.yml" --ask-vault-pass
```

If a need arises to decrypt an encrypted vault file, issue the following command.

```bash
ansible-vault decrypt inventory.vault.yml
```

For more information on working with vault files, see the [Ansible Vault documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html#encrypting-content-with-ansible-vault).


### Pre-Deployment Validation

Some utility playbooks are provided to perform some validation before attempting a deployment:

```bash
ansible-playbook -i inventory.yml prereq_facts_check.yml -e "@inventory.vault.yml" --ask-vault-pass
ansible-playbook -i inventory.yml playbooks/validate_inventory.yml -e "@inventory.vault.yml" --ask-vault-pass
```


## Running The Playbooks

There are a few main playbooks provided in this repository:

- `deploy_prerequisites.yml`: sets up the services required by Assisted Installer, and an Assisted Installer configured to use them.
- `deploy_cluster.yml`: uses Assisted Installed to deploy a cluster
- `post_install.yml`: fetches the `kubeconfig` for the deployed cluster and places it on the bastion host.
- `site.yml` simply runs all three in order.

Each of the playbooks requires an inventory and an inventory vault file, and can be run like this:

```bash
ansible-playbook -i inventory.yml site.yml -e "@inventory.vault.yml" --ask-vault-pass
```

When performing a full deployment, Crucible may first present you with a deployment plan containing all the key configuration details. Please review the deployment plan carefully to ensure that the right inventory file has been provided. To confirm the plan and proceed with the deployment, type `yes` when prompted.

In order to skip interactive prompts in environments where user input cannot be given, extend the command with the `-e skip_interactive_prompts=true` option.  
If this option is enabled, the generation of a deployment plan is omitted, and the deployment process starts immediately after the command is run.

```bash
# Careful: this command will start the deployment right away, and will not ask for manual confirmation.
ansible-playbook -i inventory.yml site.yml -e "@inventory.vault.yml" --ask-vault-pass \
  -e skip_interactive_prompts=true
```

### Priviledge Escalation

For simplicity we suggest that passwordless sudo is set up on all machines. If this is not desirable or possible in your environment then there are two options:

1. Use the same sudo password for all hosts, and use the `-K` flag on `ansible-playbook`. This will cause Ansible to [prompt for the sudo password](https://docs.ansible.com/ansible/2.9/user_guide/become.html#become-command-line-options). The password provided is then used for *all* hosts.
1. Set the `ansible_become_password` variable for each host that needs a [sudo password](https://docs.ansible.com/ansible/2.9/user_guide/become.html#become-connection-variables). The passwords can be securely stored in an encrypted Ansible vault.


## Prerequisite Services

Crucible can automatically set up the services required to deploy and run a cluster. Some are required for the Assisted Installer tool to run, and some are needed for the resulting cluster.

- NTP - The NTP service helps to ensure clocks are synchronised across the resulting cluster which is a requirement for the cluster to function.
- Container Registry Local Mirror - Provides a local container registry within the target environment. The Crucible playbooks automatically populates the registry with required images for cluster installation. The registry will continue to be used by the resulting cluster.
- HTTP Store - Used to serve the Assisted Installer discovery ISO and allow it to be used as Virtual Media for nodes to boot from.
- DNS - Optionally set up DNS records for the required cluster endpoints, and nodes. If not automatically set up then the existing configuration will be validated.
- Assisted Installer - A pod running the Assisted Installer service, database store and UI. It will be configured for the target environment and is used by the cluster deployment playbook to coordinate the cluster deployment.
- TFTP Host - A server that stores all the file mounted from the discovery image (required only for PXE deployments).

While setup of each of these can be disabled if you wish to manually configure them, but it's highly recommended to use the automatic setup of all prerequisites.


## Outputs

Note that the exact changes made depend on which playbooks or roles are run, and the specific configuration.


### Cluster

The obvious output from these playbooks is a clean OCP cluster with minimal extra configuration. Each node that has been added to the resulting cluster will have:

- CoreOS installed and configured
- The configured SSH public key as an authorised key for `root` to allow debugging


### Prerequisite Services

Various setup is done on the prerequisite services. These are informational and are not needed unless you encounter issues with deployment.
The following are defaults for a full setup:

- Registry Host

  - `opt/registry` contains the files for the registry, including the certificates.
  - `tmp/wip` is used during the playbook execution as a temporary file store.

- DNS Host

  - Using dnsmasq: `/etc/dnsmasq.d/dnsmasq.<clustername>.conf`
  - using Network Manager: `/etc/NetworkManager/dnsmasq.d/dnsmasq.<clustername>.conf` and `/etc/NetworkManager/conf.d/dnsmasq.conf`

- Assisted Installer

  - A running pod containing the Assisted Installer service.
  - `/opt/assisted-installer` contains all the files used by the Assisted Installer container

- HTTP Store
  - A running pod containing the `httpd` service
  - The discovery image from Assisted Installer will be placed in and served from `/opt/http_store/data`

- TFTP Host
  - The discovery image will be mounted to this server and do the PXE boot with TFTP 


### Bastion

As well as deploying prerequisites and a cluster, the playbooks create or update various local artifacts in the repository root and the `fetched/` directory (configured with `fetched_dest` var in the inventory).

- An updated `pull-secret.txt` containing an additional secret to authenticate with the deployed registry.
- The self-signed certificate created for the registry host as `registry.crt`.
- The SSH public and private keys generated for access to the nodes, if any, at `/home/redhat/ssh_keys` (temporarily stored in `/tmp/ssh_key_pair`)
- Any created CoreOS ignition files.

When doing multiple runs ensure you retain any authentication artefacts you need between deploys.


## Testing

Existing tests can be run from `tests` directory using

```bash
ansible-playbook run_tests.yml
```


## Related Documentation


### General

- [How the playbooks are intended to be run](docs/connecting_to_hosts.md)
- [How to configure the inventory file](docs/inventory.md)
- [Steps the playbooks take when executed](docs/pipeline_into_the_details.md)


### Troubleshooting

Some useful help for troubleshooting if you find any issues can be found in [docs/troubleshooting](docs/troubleshooting)

- [Discovery ISO not booting](docs/troubleshooting/discovery_iso_not_booting.md)


## References

This software was adapted from [sonofspike/cluster_mgnt_roles](https://github.com/sonofspike/cluster_mgnt_roles)
