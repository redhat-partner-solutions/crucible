
import ard


__all__ = ('Inventory',)


class Inventory:
    def __init__(self, clout):
        self.all = {
            'vars': {},
            'children': {
                'bastions': {
                    'hosts': {}
                },
                'services': {
                    'hosts': {}
                },
                'nodes': {
                    'vars': {},
                    'children': {
                        'masters': {
                            'vars': {},
                            'hosts': {}
                        },
                        'workers': {
                            'vars': {},
                            'hosts': {}
                        },
                    }
                }
            }
        }

        self.nodes = self.all['children']['nodes']['children']
        self.bastions = self.all['children']['bastions']['hosts']
        self.services = self.all['children']['services']['hosts']

        clusters = clout.get_node_templates('crucible::Cluster')
        if clusters:
            if len(clusters) > 1:
                raise Exception('only one cluster is currently supported')
            for cluster in clusters.values():
                self.add_cluster(cluster)
        else:
            raise Exception('no clusters declared')

    def as_dict(self):
        """Returns the inventory as a Python dict"""
        inventory = {'all': self.all}
        return inventory

    def write(self, out):
        inventory = self.as_dict()
        ard.write(inventory, out)

    def add_cluster(self, cluster):
        self.all['vars']['openshift_full_version'] = cluster.properties['version']
        self.all['vars']['api_vip'] = cluster.properties['api-vip']
        self.all['vars']['ingress_vip'] = cluster.properties['ingress-vip']
        self.all['vars']['machine_network_cidr'] = cluster.properties['machine-network']
        self.all['vars']['service_network_cidr'] = cluster.properties['service-network']
        self.all['vars']['cluster_network_cidr'] = cluster.properties['cluster-network']
        self.all['vars']['cluster_network_host_prefix'] = cluster.properties['cluster-network-host-prefix']

        for node in cluster.get_relationships('machine'):
            if node.target.is_type('crucible::Machine'):
                self.add_node(node)

        for bastion in cluster.get_relationship_targets('bastion'):
            self.bastions['bastion'] = to_host(bastion)
            self.all['vars']['pull_secret_lookup_paths'] = bastion.properties['pull-secret-lookup-paths']
            self.all['vars']['ssh_key_dest_base_dir'] = bastion.properties['ssh-keypair-dest-base-dir']
            self.all['vars']['kubeconfig_dest_dir'] = bastion.properties['kubeconfig-dest-dir']

        for dns in cluster.get_relationships('dns'):
            self.services['dns_host'] = to_host(dns.target)
            self.all['vars']['setup_dns_service'] = dns.target_capability.properties['install']

        for ntp in cluster.get_relationships('ntp'):
            self.services['ntp_host'] = to_host(ntp.target)
            self.all['vars']['setup_ntp_service'] = ntp.target_capability.properties['install']
            self.all['vars']['ntp_server'] = ntp.target.properties['ip']
            if ntp.target_capability.is_type('crucible::ChronyNTP'):
                self.all['vars']['ntp_server_allow'] = ntp.target_capability.properties['allow']

        for store in cluster.get_relationships('store'):
            self.services['http_store'] = to_host(store.target)
            self.all['vars']['setup_http_store_service'] = store.target_capability.properties['install']

        for registry in cluster.get_relationships('registry'):
            self.services['registry_host'] = to_host(registry.target)
            self.all['vars']['setup_registry_service'] = registry.target_capability.properties['install']
            if registry.target_capability.is_type('crucible::SimpleRegistry'):
                self.all['vars']['use_local_mirror_registry'] = registry.target_capability.properties['use-local-mirror-registry']

        for ai in cluster.get_relationships('ai'):
            self.services['assisted_installer'] = to_host(ai.target)
            self.all['vars']['discovery_iso_name'] = ai.target_capability.properties['discovery-iso-name']
            self.all['vars']['repo_root_path'] = ai.target_capability.properties['repo-root-path']
            self.all['vars']['fetched_dest'] = ai.target_capability.properties['fetched-dest']
            self.all['vars']['vip_dhcp_allocation'] = ai.target_capability.properties['vip-dhcp-allocation']

    def add_node(self, node):
        machine = node.target
        role = node.properties['role']
        
        host = to_host(machine)
        host['role'] = role
        host['vendor'] = machine.properties['vendor']
        host['mac'] = machine.properties['mac']

        if 'installation-disk' in node.properties:
            host['installation_disk_path'] = node.properties['installation-disk']

        if machine.is_type('crucible::VM'):
            host['vm_spec'] = {
                'cpu_cores': machine.properties['cpu-cores'],
                'ram_mib': machine.properties['ram']['$number'] // 1048576,
                'disk_size_gb': machine.properties['disk']['$number'] // 1000000000
            }

            for hypervisor in machine.get_relationships('hypervisor'):
                #if 'vm_host' in self.services:
                #    raise Exception('only one VM host is supported')
                vm_host = to_host(hypervisor.target)

                host['bmc_address'] = '{ip}:{port}'.format(
                    ip=hypervisor.target.properties['ip'],
                    port=hypervisor.target_capability.properties['virtual-bmc-port'])

                if hypervisor.target_capability.is_type('crucible::KVM'):
                    vm_host['ansible_user'] = hypervisor.target_capability.properties['ansible-user']
                    vm_host['images_dir'] = hypervisor.target_capability.properties['images-dir']
                    vm_host['vm_bridge_ip'] = hypervisor.target_capability.properties['bridge-ip']
                    vm_host['vm_bridge_interface'] = hypervisor.target_capability.properties['bridge-interface']

                    dnses = hypervisor.target.get_relationship_targets('kvm-dns')
                    if dnses:
                        for dns in dnses:
                            if dns.is_type('crucible::Node'):
                                vm_host['dns'] = dns.properties['ip']
                            else:
                                raise Exception('machine with KVM capability has a "kvm-dns" requirement but it does not target a Node')
                            break # there should be only one
                    else:
                        raise Exception('machine with KVM capability does not have a "kvm-dns" requirement')

                self.services['vm_host'] = vm_host

                break # there should be only one

        if ('bmc' in machine.capabilities) and ('ip' in machine.capabilities['bmc'].properties):
            host['bmc_address'] = machine.capabilities['bmc'].properties['ip']

        for bmc in machine.get_policies('crucible::BMC'):
            host['bmc_user'] = bmc.properties['user']
            host['bmc_password'] = bmc.properties['password']
            break # there should be only one

        self.nodes[role+'s']['hosts'][machine.name] = host


def to_host(node):
    host = {}
    host['ansible_host'] = node.properties['ip']
    return host
