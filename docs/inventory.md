# Crucible | Inventory

> ❗ _Red Hat does not provide commercial support for the content of this repo. Any assistance is purely on a best-effort basis, as resource permits._

---

```bash
##############################################################################
DISCLAIMER: THE CONTENT OF THIS REPO IS EXPERIMENTAL AND PROVIDED "AS-IS"

THE CONTENT IS PROVIDED AS REFERENCE WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
##############################################################################
```

---

## Inventory Validation

### Cluster config checks:

#### Highly Available OpenShift cluster node checks

- 3 or more master nodes
- 2 or more, or 0 worker nodes

#### Single Node OpenShift cluster node checks

- 1 master node
- 0 worker nodes

Single Node OpenShift requires the API and Ingress VIPs to be set to the IP address (`ansible_host`) of the master node.

In addition to that, the following checks must be met for both HA and SNO deployments:

- every node has required vars:
  - `bmc_address`
  - `bmc_password`
  - `bmc_user`
  - `vendor`
  - `role`
  - `mac`
- required vars are correctly typed
- all values of `vendor` are supported
- all values of `role` are supported
- If any nodes are virtual (vendor = KVM) then a vm_host is defined

There three possible groups of nodes are `masters`, `workers` and `day2_workers`.

#### Day 2 nodes

Day 2 nodes are added to an existing cluster. The reason why the installation of day 2 nodes is built into the main path of our automation is that for assisted installer day 2 nodes can be on a different L2 network which the main flow does not allow.

Add a second iso name parameter to the inventory to avoid conflict with the original:

```yaml
# day2 workers require custom parameter
day2_discovery_iso_name: "discovery/day2_discovery-image.iso"
```

Then add the stanza for day2 workers:

```yaml
day2_workers:
  vars:
    role: worker
    vendor: HPE
  hosts:
    worker3: # Ensure this does not conflict with any existing workers
      ansible_host: 10.60.0.106
      bmc_address: 172.28.11.26
      mac: 3C:FD:FE:78:AB:05
```

### Network checks

- All node `bmc_address`es are reachable
- All prerequisite services `ansible_host`s are reachable
- If `setup_ntp_service` is disabled then the configured `ntp_server` must be reachable.

Note that checks on DNS, registry, and HTTP Store are completed later in the playbooks.

> :warning: **If you have dhcp entries already specified then the host name must match the hostname in the dhcp entry. If not procedures will fail**

### VM spec config

The specs of VMs created by the playbooks are configured for every node group. The parameters of the VMs can be specified by adding `vm_spec` to the node definition in the inventory.
A basic example is as follows:

```yaml
vm_spec:
  cpu_cores: 4
  ram_mib: 6144
  disk_size_gb: 20
```

If you wish to configure extra disks then you can add the `extra_disks` keyword:

```yaml
vm_spec:
  cpu_cores: 4
  ram_mib: 6144
  disk_size_gb: 20
  extra_disks:
    my_extra_disk: 100
    my_other_extra_disk: 150
```

Here we specify 2 extra disks of size `100` and `150GB` respectively.

### Required secrets

#### Prerequisite services

The Container Registry service requires the following variables to be set. Set the appropriate values in the inventory vault file.

- `REGISTRY_HTTP_SECRET`

For Restricted Network installations, additional credentials for the registry need to be provided.

- `disconnected_registry_user`
- `disconnected_registry_password`

#### Nodes

All nodes must have credentials set for the BMCs.

- `bmc_user`
- `bmc_password`

It is possible to specify different credentials for individual nodes.
See the sample inventory file (`inventory.yml.sample`) and the sample inventory vault file (`inventory.vault.yml.sample`) for more information.

## Configurations

### Network configuration

The `network_config` entry on a node is a simplified version of the `nmstate`([nmstate.io](http://nmstate.io/)) required by the [assisted installer api](https://github.com/openshift/assisted-service/blob/3bcaca8abef5173b0e2175b5d0b722e851e39cee/docs/user-guide/restful-api-guide.md).
If you wish to use your own template you can set `network_config.template` with a path to your desired template the default can be found [here](../roles/generate_discovery_iso/templates/nmstate.yml.j2). If you wish to write the `nmstate` by hand you can use the `network_config.raw`.

#### Static IPs

To activate static IPs in the discovery iso and resulting cluster there is some configuration required in the inventory.

```yaml
network_config:
  interfaces:
    - name: "{{ interface }}"
      mac: "{{ mac }}"
      addresses:
        ipv4:
          - ip: "{{ ansible_host}}"
            prefix: "{{ mask }}"
  dns_server_ips:
    - "{{ dns }}"
    - "{{ dns2 }}"
  routes: # optional
    - destination: 0.0.0.0/0
      address: "{{ gateway }}"
      interface: "{{ interface }}"
```

where the variables are as follows:

- `ip`: The static IP is set
- `dns` & `dns2`: IPs of the DNS servers
- `gateway`: IP of the gateway
- `mask`: Length of subnet mask (e.g. 24)
- `interface`: The name of the interface you wish to configure
- `mac`: Mac address of the interface you wish to configure

#### Link Aggregation

Here is an example of how to do link aggregation of two interfaces.

```yaml
network_config:
  interfaces:
    - name: bond0
      type: bond
      state: up
      addresses:
        ipv4:
          - ip: 172.17.0.101
            prefix: 24
      link_aggregation:
        mode: active-backup
        options:
          miimon: "1500"
        slaves:
          - ens7f0
          - ens7f1
    # To avoid an interface to up, specify its status as down
    - name: ens1f0
      type: ethernet
      mac: "40:A6:B7:3D:B3:70"
      state: down 
    - name: ens1f1
      type: ethernet
      mac: "40:A6:B7:3D:B3:71"
      state: down
  dns_resolver_ip: 10.40.0.100
  routes:
    - destination: 0.0.0.0/0
      address: 172.17.0.1
      interface: bond0
```

#### IPv6

At the momment crucible doesn't configure DHCP for IPv6 entries, so you will have to roll your own or use static ips (see the above section on network configuration)

Note: Crucible doesn't require the BMC's to be on the same network as long as both are routable from the bastion. So you could have as per the example the BMC addresses as IPv4 even if the cluster is IPv6. However it should be noted that the HTTP Store has to be routeable from the BMC network.

To setup an IPv6 single stack cluster you need to change the following variables:
```yaml
all:
  vars:
    ...
    api_vip: fd00:6:6:2051::96
    ingress_vip: fd00:6:6:2051::97

    machine_network_cidr:  fd00:6:6:2051::0/64
    service_network_cidr: fd02::/112
    cluster_network_cidr: fd01::/48
    cluster_network_host_prefix: 64
    ...
...
      children:
        masters:
          vars:
            role: master
            vendor: Dell
            # Note: Crucible currently requires you to setup your own IPv6 DHCP
            # Or use static ip addresses.
            network_config:
              interfaces:
                - name: "enp1s0"
                  mac: "{{ mac }}"
                  addresses:
                    ipv6:
                      - ip: "{{ ansible_host }}"
                        prefix: "64"
              dns_server_ips:
                - "fd00:6:6:11::52"
              routes:
                - destination: "0:0:0:0:0:0:0:0/0"
                  address: "fd00:6:6:2051::1"
                  interface: "enp1s0"
          hosts:
            super1:
              ansible_host: fd00:6:6:2051::101
              bmc_address: 172.28.11.29
              mac: "40:A6:B7:3D:B3:70"
            ...
```

To enable assisted installer to communicate via IPv6 you must first have the host configured with an IPv6 then add `use_ipv6: True` to the `assisted_installer` host:
```yaml
    services:
      hosts:
        assisted_installer:
          ...
          use_ipv6: True
          # Optionallyu use these two values to configure the ipv6 network which podman will create
          # podman_ipv6_network_subnet: 'fd00::1:8:0/112'
          # podman_ipv6_network_gateway: 'fd00::1:8:1'
          ...
```

#### Dual Stack

Openshift currently only allows the ingress and API VIPs to be single stack so you must choose IPv4 or IPv6. Then crucible offers 3 variables for the extra network configuration (`extra_machine_networks`, `extra_service_networks` and `extra_cluster_networks`):

```yaml
all:
  vars:
    ...
    api_vip: 10.60.0.96
    ingress_vip: 10.60.0.97

    machine_network_cidr: 10.60.0.0/24
    service_network_cidr: 172.30.0.0/16
    cluster_network_cidr: 10.128.0.0/14
    cluster_network_host_prefix: 23

    extra_machine_networks:
      - cidr: fd00:6:6:2051::/64
    extra_service_networks:
      - cidr: fd02::/112
    extra_cluster_networks:
      - cidr: fd01::/48
        host_prefix: 64
...
      children:
        masters:
          vars:
            ...
            network_config:
              interfaces:
                - name: "enp1s0"
                  mac: "{{ mac }}"
                  addresses:
                    ipv4:
                      - ip: "{{ ansible_host }}"
                        prefix: "24"
                    ipv6:
                      - ip: "{{ ipv6_address }}"
                        prefix: "64"
              # Only one DNS server ip per protocol
              dns_server_ips:
                - "fd00:6:6:11::52"
                - "10.40.0.100"
              routes:
                - destination: "0:0:0:0:0:0:0:0/0"
                  address: "fd00:6:6:2051::1"
                  interface: "enp1s0"
                - destination: 0.0.0.0/0
                  address: "10.60.0.1"
                  interface: "enp1s0"
          hosts:
            super1:
              ansible_host: 10.60.0.101
              ipv6_address: fd00:6:6:2051::101
              bmc_address: 172.28.11.29
              mac: "40:A6:B7:3D:B3:70"
            ...

```

### Prerequisites

---

Use the following vars to control setup of prerequisites:

- `setup_ntp_service`
- `setup_registry_service`
- `setup_http_store_service`
- `setup_dns_service`
- `create_vms`
- `setup_sushy_tools`
- `setup_pxe_service`

Note that if one or more of these services is pre-existing in your environment the inventory must still be configured with information needed to access those services, even when the service is not being set up by the playbooks.

> TODO: list required vars for each service when setup automatically

> TODO: list required vars for each service when NOT setup automatically

### Virtual Nodes

---

When using one or more virtual nodes, they are identified as such by having `vendor` set to `KVM`. They still require the BMC configuration and MAC+IP addresses common to all nodes, but with a few variations:

- The BMC address of the virtual nodes must point to the `vm_host` defined on the node; `sushy-tools` will be set up on the `vm_host` to allow the VMs to be controlled identically to the baremetal hosts.
  - The BMC user and password will be set in `sushy-tools` and must therefore be the same for all virtual nodes.
- The specified MAC address will be set on the VM interface.

#### Reusable VMs

If you need VMs with static UUIDs to allow them to be reused then the UUID for a VM can be set using the `uuid` var for each VM node. e.g.

```yaml
          hosts:
            super1:
              vendor: KVM
              ansible_host: 192.168.10.11
              mac: "DE:AD:BE:EF:C0:2C"
              uuid: d36ebda0-25bf-55ef-9c69-66ad5ef0d39d
```


### SSH Key Gen

---

By default an SSH key will be generated by the `deploy_cluster.yml` playbook. This can be disabled by adding `generate_ssh_keys = False` to the inventory. It is possible to configure the task generating the SSH key (see the docs for `community.crypto.openssh_keypair`) by setting `openssh_keypair_args` with a dictionary.

### DNS and DHCP

If you to only point to the dns configure by crucible you should also provide `upstream_dns` which points to another dns server which can provide records for non-crucible queries.

You can control the ip addresses which dnsmasq listens to using the `listen_addresses` by default this will include both `127.0.0.1` and ansible's default IPv4 address for the host (`ansible_default_ipv4.address`). You may also configure the interfaces which dnsmasq responds by defining `listening_interfaces` as a list of the interfaces you which to listen to.

```yaml
dns_host:
  ...
  listen_addresses:
    - 127.0.0.1
    - 192.168.10.202
    - 30.1.1.202
    - 50.2.2.202
  listening_interfaces:
    - eth1
    - eth2
    - eth3
  ...
```

#### DHCP
If you wish to configure dnmasq to act as a dhcp server then you need to configure the following values:

```yaml
dns_host:
  ...
  use_dhcp: true
  dhcp_range_first: <first ip in your pool>
  dhcp_range_last:  <last ip in your pool>
  prefix: <subnet prefix>
  gateway: <your gateway>
  ...
```

In addition if you do not want dnsmasq to reply to dhcp request on certain interfaces you can define the list `no_dhcp_interfaces` so that dnsmasq will ignore them. For instance assuming you have 3 interfaces `eth1`, `eth2`, `eth3`, and you only wish for dhcp to listen on `eth2` you could add the following:

```yaml
dns_host:
  ...
  no_dhcp_interfaces:
    - eth1
    - eth3
  ...
```

# Examples

## Virtual Management Cluster

One of the simplest examples is a simple cluster with no workers, virtual masters on a VM Host, and all other supporting services being configured on the bastion host. The initial environment will be something like this:

![](images/simple_kvm_physical.png)

That diagram gives the following excerpt from the inventory for the `bastion` and `services`:

> **Note**: We use `ansible_connection: local` here because crucible should be executed from the bastion, the use of connection local removes the need to configure your user to be able to SSH into its self.

```yaml
# ...
  children:
    bastions:
      hosts:
        bastion:
          ansible_host: 192.168.10.5
          ansible_connection: local

    services:
      hosts:
        assisted_installer:
          ansible_host: "{{ hostvars['bastion']['ansible_host'] }}"
          ansible_connection: local

          # ...
        registry_host:
          ansible_host: "{{ hostvars['bastion']['ansible_host'] }}"
          ansible_connection: local

          # ...
        dns_host:
          ansible_host: "{{ hostvars['bastion']['ansible_host'] }}"
          ansible_connection: local

          # ...
        http_store:
          ansible_host: "{{ hostvars['bastion']['ansible_host'] }}"
          ansible_connection: local

          # ...
        ntp_host:
          ansible_host: "{{ hostvars['bastion']['ansible_host'] }}"
          ansible_connection: local

          # ...
    vm_hosts:
      hosts:
        vm_host:
          ansible_host: 192.168.10.6
          # ...
```

### VM Host in Detail

The virtual `master` nodes in their simplest case are defined in the inventory as an address they will be accessible on, and the MAC Address that will be set when creating the VM and later used by Assisted Installer to identify the machines:

```yaml
        masters:
          vars:
            role: master
            vendor: KVM
            bmc_address: 192.168.10.6:8082 # virtual BMC is setup on VM Host port 8082
          hosts:
            super1:
              ansible_host: 192.168.10.11
              mac: "DE:AD:BE:EF:C0:2C"
            super2:
              ansible_host: 192.168.10.12
              mac: "DE:AD:BE:EF:C0:2D"
            super3:
              ansible_host: 192.168.10.13
              mac: "DE:AD:BE:EF:C0:2E"
```

For the virtual bridge configuration, in this example interface `eno1` is used for accessing the VM host, the `eno2` is assigned to the virtual bridge to allow the virtual `super` nodes to connect to the Management Network. Note that these two interfaces cannot be the same. DNS on the virtual bridge is provided by the DNS `service` configured on the Bastion host.

The `vm_host` entry in the inventory becomes:

```yaml
        vm_host:
          ansible_user: root
          ansible_host: 192.168.10.6
          vm_bridge_ip: 192.168.10.7
          vm_bridge_interface: eno2
          dns: "{{ hostvars['dns_host']['ansible_host'] }}"
```

![](images/vm_host_interfaces.png)

### Resulting Cluster

Combining those pieces, along with other configuration like versions, certificates and keys, will allow Crucible to deploy a cluster like this:

![](images/simple_kvm.png)

## Bare Metal Deployment

At the other extreme to the previous example, services and nodes can be spread across multiple different machines, and a cluster with worker nodes can be deployed:

![](images/many_machines.png)

The basic network configuration of the inventory for the fully bare metal deployment environment might look like this:

```yaml
# ...
  children:
    bastions:
      hosts:
        bastion:
          ansible_host: 192.168.10.5
    services:
      hosts:
        assisted_installer:
          ansible_host: 192.168.10.200
          # ...
        registry_host:
          ansible_host: 192.168.10.201
          # ...
        dns_host:
          ansible_host: 192.168.10.202
          # ...
        http_store:
          ansible_host: 192.168.10.204
          # ...
        ntp_host:
          ansible_host: 192.168.10.203
          # ...
        # no vm_host.
    masters:
      vars:
        role: master
        vendor: SuperMicro
      hosts:
        super1:
          ansible_host: 192.168.10.11
          bmc_address: 172.30.10.1
          # ...
        super2:
          ansible_host: 192.168.10.12
          bmc_address: 172.30.10.2
          # ...
        super3:
          ansible_host: 192.168.10.13
          bmc_address: 172.30.10.3
          # ...
    workers:
      vars:
        role: worker
        vendor: Dell
      hosts:
        worker1:
          ansible_host: 192.168.10.16
          bmc_address: 172.30.10.6
          # ...
        worker2:
          ansible_host: 192.168.10.17
          bmc_address: 172.30.10.7
          # ...
```
## Additional Partition Deployment

For OCP 4.8+ deployments you can set partitions if required on the nodes. You do this by adding the snippet below to the node defination. Please ensure you provide the correct label and size(MiB) for the additional partitions you want to create. The device can either be the drive in which RHCOS image needs to be installed or it can be any additional drive on the node that requires partitioning. In the case that the device is equal to the host's `installation_disk_path` then a partition will be added defined by `disks_rhcos_root`. All additional partitions must be added under `extra_partitions` key as per the example below.

```yaml
disks:
  - device: "{{ installation_disk_path }}"
    extra_partitions:
      partition_1: 1024
      partition_2: 1024
 ```

## PXE Deployment
You must have these services when using PXE deployment
- `DHCP`
- `DNS`
- `PXE`
```
       masters:
          vars:
            role: master
            vendor: pxe # this example is a PXE control plane
          hosts:
            super1:
              ansible_host: 10.60.0.101
              mac: "DE:AD:BE:EF:C0:2C"
              bmc_address: "192.168.10.16"


            super2:
              ansible_host: 10.60.0.102
              mac: "DE:AD:BE:EF:C0:2D"
              bmc_address: "192.168.10.17"


            super3:
              ansible_host: 10.60.0.103
              mac: "DE:AD:BE:EF:C0:2E"
              bmc_address: "192.168.10.18"

        workers:
          vars:
            role: worker
          hosts:
            worker1:
              ansible_host: 10.60.0.104
              bmc_address: 192.168.10.19
              mac: 3c:fd:fe:b5:79:04
              vendor: pxe
            worker2:
              ansible_host: 10.60.0.105
              bmc_address: 192.168.10.20
              mac: "DE:AD:BE:EF:C0:2F"
              vendor: pxe
              bmc_address: "nfvpe-21.oot.lab.eng.bos.redhat.com"
              bmc_port: 8082
   
```
> **Note**: that the BMCs of the nodes in the cluster must be routable from the bastion host and the HTTP Store must be routable from the BMCs

These two examples are not the only type of clusters that can be deployed using Crucible. A hybrid cluster can be created by mixing virtual and bare metal nodes.


# Mirroring operators and index for disconnected installations

By default we do not populate the disconnected registry with operators used post install
this is because this takes a substantial amount of time and can be done post install or
even in parallel by the user by running:

```bash
$ ansible-playbook -i inventory.yml playbook playbooks/deploy_registry.yml -e populate_operator_catalog=True
```

If you wish to populate the registry as part of deploying the pre-requistes you can add `populate_operator_catalog: true` to the `registry_host`

# Automated non-node DNS entries.

## DNS Entries for Bastion, Services and VM_Hosts.

When using the crucible provided DNS, the automation will create entries for the bastion, the service hosts and, then vm hosts.
The value of `ansible_fqdn` will be used except in where `registry_fqdn` is defined as part of `registry_host`, or when `sushy_fqdn` is defined as part of `vm_hosts`.

NOTE: The DNS entries will only be created if the `ansible_host` is an _IP address_ otherwise it will be skipped.

To force the automation to skip a host you can add `dns_skip_record: true` to the host definition.

## DNS Entries for BMCs

Automatic creation of DNS records for your BMC nodes requires `setup_dns_service: true`. Crucible will create DNS A and PTR records.
For this to occur you  you are required to add `bmc_ip:` alongside `ansible_host` in your host definitions.
The addresses will be templated as `{{ inventory_hostname }}-bmc.infra.{{ base_dns_domain }}`.
If `setup_dns_service` is `false` crucible will not create any DNS records.

For example: The BMC address for host `super1` will be `"super1-bmc.infra.example.com"`.

Note: This can be useful when working with proxies as you can add `*.infra.example.com` to your no_proxy setting.

```yaml
all:
  vars:
    base_dns_domain: example.com
  ...
    masters:
      vars:
        role: master
        vendor: SuperMicro
      hosts:
        super1:
          ansible_host: 192.168.10.11
          bmc_ip: 172.30.10.1
          # ...
        super2:
          ansible_host: 192.168.10.12
          bmc_ip: 172.30.10.2
          # ...
        super3:
          ansible_host: 192.168.10.13
          bmc_ip: 172.30.10.3
          # ...
    workers:
      vars:
        role: worker
        vendor: Dell
      hosts:
        worker1:
          ansible_host: 192.168.10.16
          bmc_ip: 172.30.10.6
          # ...
        worker2:
          ansible_host: 192.168.10.17
          bmc_ip: 172.30.10.7
```
# Defining a password for the discovery iso.

If users wish to provide password for the discovery iso they must define `hashed_discovery_password` in the `all` section inventory.
The value provided in `hashed_discovery_password` can be created by using `mkpasswd --method=SHA-512 MyAwesomePassword`.


# Operators

It is possible to the install a few operators as part of the cluster installtion. These operators are local storage operator (`install_lso: True`), open data fabric (`install_odf: True`) and openshift virtualision (`install_cnv: True`)
