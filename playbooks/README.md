# Playbooks

Most playbooks here are called by the higher level playbooks (`deploy_cluster.yml`, `deploy_day2_workers.yml` and `deploy_prerequisites.yml`)
and are nominally put in the order of usage with some exceptions. This may be useful for debugging or stepping through the process however you should not where variables are overridden in the higher level playbooks for achieve the same results (e,g when using `generate_discovery_iso.yml` for a day2 cluster.

| Playbook name                          | Discription                                                                      | Required arguments    |
| -------------------------------------- | -------------------------------------------------------------------------------- | --------------------- |
| `validate_inventory.yml`               | Run checks on inventory to check for common errors                               | -                     |
| `process_kvm_nodes.yml`                | Processes KVM nodes for use in later playbooks                                   | -                     |
| `configure_vm_host_network.yml`        | Configures the network configurations on vm_hosts                                | -                     |
| `deploy_ntp.yml`                       | Deploys NTP server                                                               | -                     |
| `deploy_http_store.yml`                | Deploys HTTP server                                                              | -                     |
| `deploy_registry.yml`                  | Deploys container image registry                                                 | -                     |
| `deploy_tftp.yml`                      | Deploys tftp server                                                              | -                     |
| `deploy_dns.yml`                       | Deploys DNS and DHCP                                                             | -                     |
| `deploy_assisted_installer_onprem.yml` | Deploys podman pod with assisted service containers                              | -                     |
| `deploy_vms.yml`                       | Deploys VMs (see [1])                                                            | -                     |
|                                        |                                                                                  | -                     |
| `generate_ssh_key_pair.yml`            | Generates an ssh key pair for use in debugging installations                     | -                     |
| `create_cluster.yml`                   | Creates cluster definition in assisted installer                                 | -                     |
| `generate_discovery_iso.yml`           | Generate descovery iso                                                           | `cluster_id`          |
| `mount_discovery_iso_for_pxe.yml`      |  Mounts discovery iso, generates grub config and syncs files to the TFTP server  | -                     |
| `boot_iso.yml`                         | Reboots nodes to discovery iso                                                   | -                     |
| `install_cluster.yml`                  | Trigger install of discovered hosts                                              | `cluster_id`          |
| `monitor_hosts.yml`                    | Monitor hosts for discovery and to become ready                                  | `cluster_id`          |
| `monitor_cluster.yml`                  | Monitor cluster for installation and initalisation                               | `cluster_id`          |
|  Day2                                  | -                                                                                |                       |
| `create_day2_cluster.yml`              | Creates day 2 cluster definition in assisted installer                           | -                     |
| `add_day2_nodes.yml`                   | Monitors day2 cluster and triggers install when node is ready                    | `add_host_cluster_id` |
| `approve_csrs.yml`                     | Montiors for CSRs and accepts them                                               | -                     |
|  Utilities                             | -                                                                                |                       |
| `boot_disk.yml`                        | Reboots nodes to disk                                                            | -                     |
| `dell_idrac_soft_reset.yml`            | Runs `racadm racreset` on dell nodes                                             | -                     |
| `create_vms.yml`                       | Creates VMs                                                                      | -                     |
| `deploy_sushy_tools.yml`               | Deploys sushy tools                                                              | -                     |
| `destroy_vms.yml`                      | Destroy VMs and bridge                                                           | -                     |

[1] `deploy_vms.yml` runs `configure_vm_host_network.yml`, `destroy_vms.yml`, `create_vms.yml` and `deploy_sushy_tools.yml`
