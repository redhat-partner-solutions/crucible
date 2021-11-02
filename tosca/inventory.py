
import ard


class Inventory:
    def __init__(self):
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

    def write(self, out):
        inventory = {'all': self.all}
        ard.write(inventory, out)

    def from_clout(self, clout):
        clusters = clout.get_vertexes('NodeTemplate', 'crucible::Cluster')
        if clusters:
            if len(clusters) > 1:
                raise Exception('only one cluster is currently supported')
            for cluster in clusters.values():
                self.add_cluster(cluster)
        else:
            raise Exception('no clusters declared')

    def add_cluster(self, vertex):
        self.all['vars']['openshift_full_version'] = vertex.properties['version']
        self.all['vars']['api_vip'] = vertex.properties['api-vip']
        self.all['vars']['ingress_vip'] = vertex.properties['ingress-vip']
        self.all['vars']['machine_network_cidr'] = vertex.properties['machine-network']
        self.all['vars']['service_network_cidr'] = vertex.properties['service-network']
        self.all['vars']['cluster_network_cidr'] = vertex.properties['cluster-network']
        self.all['vars']['cluster_network_host_prefix'] = vertex.properties['cluster-network-host-prefix']

        self.add_nodes(vertex, 'master')
        self.add_nodes(vertex, 'worker')

        for bastion in vertex.get_edges('Relationship', 'bastion'):
            self.bastions['bastion'] = to_host(bastion.target)
            self.all['vars']['pull_secret_lookup_paths'] = bastion.target.properties['pull-secret-lookup-paths']
            self.all['vars']['ssh_key_dest_base_dir'] = bastion.target.properties['ssh-keypair-dest-base-dir']
            self.all['vars']['kubeconfig_dest_dir'] = bastion.target.properties['kubeconfig-dest-dir']

        for dns in vertex.get_edges('Relationship', 'dns'):
            self.services['dns_host'] = to_host(dns.target)
            self.all['vars']['setup_dns_service'] = dns.target_capability.properties['install']

        for ntp in vertex.get_edges('Relationship', 'ntp'):
            self.services['ntp_host'] = to_host(ntp.target)
            self.all['vars']['setup_ntp_service'] = ntp.target_capability.properties['install']
            self.all['vars']['ntp_server'] = ntp.target.properties['ip']
            if ntp.target_capability.is_type('crucible::ChronyNTP'):
                self.all['vars']['ntp_server_allow'] = ntp.target_capability.properties['allow']

        for store in vertex.get_edges('Relationship', 'store'):
            self.services['http_store'] = to_host(store.target)
            self.all['vars']['setup_http_store_service'] = store.target_capability.properties['install']

        for registry in vertex.get_edges('Relationship', 'registry'):
            self.services['registry_host'] = to_host(registry.target)
            self.all['vars']['setup_registry_service'] = registry.target_capability.properties['install']
            if registry.target_capability.is_type('crucible::SimpleRegistry'):
                self.all['vars']['use_local_mirror_registry'] = registry.target_capability.properties['use-local-mirror-registry']

        for ai in vertex.get_edges('Relationship', 'ai'):
            self.services['assisted_installer'] = to_host(ai.target)
            self.all['vars']['discovery_iso_name'] = ai.target_capability.properties['discovery-iso-name']
            self.all['vars']['repo_root_path'] = ai.target_capability.properties['repo-root-path']
            self.all['vars']['fetched_dest'] = ai.target_capability.properties['fetched-dest']
            self.all['vars']['vip_dhcp_allocation'] = ai.target_capability.properties['vip-dhcp-allocation']

    def add_nodes(self, vertex, role):
        for node in vertex.get_edges('Relationship', role):
            if node.target.is_type('crucible::Machine'):
                self.add_node(node.target.name, node.target, role)

    def add_node(self, name, vertex, role):
        host = to_host(vertex)
        host['role'] = role
        host['vendor'] = vertex.properties['vendor']
        host['mac'] = vertex.properties['mac']

        if vertex.is_type('crucible::VM'):
            host['vm_spec'] = {
                'cpu_cores': vertex.properties['cpu-cores'],
                'ram_mib': vertex.properties['ram']['$number'] // 1048576,
                'disk_size_gb': vertex.properties['disk']['$number'] // 1000000000
            }

            for hypervisor in vertex.get_edges('Relationship', 'hypervisor'):
                #if 'vm_host' in self.services:
                #    raise Exception('only one VM host is supported')
                vm_host = to_host(hypervisor.target)

                if hypervisor.target_capability.is_type('crucible::KVM'):
                    vm_host['ansible_user'] = hypervisor.target_capability.properties['ansible-user']
                    vm_host['images_dir'] = hypervisor.target_capability.properties['images-dir']
                    vm_host['vm_bridge_ip'] = hypervisor.target_capability.properties['bridge-ip']
                    vm_host['vm_bridge_interface'] = hypervisor.target_capability.properties['bridge-interface']

                    dnses = hypervisor.target.get_edges('Relationship', 'kvm-dns')
                    if dnses:
                        for dns in dnses:
                            if dns.target.is_type('crucible::Node'):
                                vm_host['dns'] = dns.target.properties['ip']
                            else:
                                raise Exception('node with KVM capability has a "kvm-dns" requirement but it does not target a Node')
                            break # there should be only one
                    else:
                        raise Exception('node with KVM capability does not have a "kvm-dns" requirement')

                self.services['vm_host'] = vm_host

                break # there should be only one

        if 'bmc' in vertex.capabilities:
            host['bmc_address'] = vertex.capabilities['bmc'].properties['ip']

        bmc = vertex.get_policies('crucible::BMC')
        if bmc:
            host['bmc_user'] = bmc[0].properties['user']
            host['bmc_password'] = bmc[0].properties['password']

        self.nodes[role+'s']['hosts'][name] = host


def to_host(vertex):
    host = {}
    host['ansible_host'] = vertex.properties['ip']
    return host
