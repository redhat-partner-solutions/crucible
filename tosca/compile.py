#!/usr/bin/env python3

from clout import *
import sys, puccini.tosca, ard


def main():
    if len(sys.argv) <= 1:
        sys.stderr.write('no URL provided\n')
        sys.exit(1)

    url = sys.argv[1]

    try:
        clout = Clout(url)
        inventory = to_inventory(clout)
        ard.write(inventory, sys.stdout)
    except puccini.tosca.Problems as e:
        print('Problems:', file=sys.stderr)
        for problem in e.problems:
            ard.write(problem, sys.stderr)
        sys.exit(1)


def to_inventory(clout):
    vars = {
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

    nodes = vars['children']['nodes']['children']

    clusters = clout.get_vertexes('NodeTemplate', 'crucible::Cluster')
    if clusters:
        if len(clusters) > 1:
            raise Exception('only one cluster is currently supported')
        for cluster in clusters.values():
            nodes['masters'] = get_hosts(cluster, 'master')
            nodes['workers'] = get_hosts(cluster, 'worker')
            #cluster.get_edges('Relationship', 'ntp'):

    else:
        raise Exception('no clusters declared')

    return {'all': {'vars': vars}}


def get_hosts(cluster_vertex, role):
    hosts = {}
    for edge in cluster_vertex.get_edges('Relationship', role):
        if edge.target.is_type('crucible::Machine'):
            name = edge.target.name
            hosts[name] = to_host(edge.target)
            hosts[name]['role'] = role
    return hosts


def to_host(vertex):
    host = {}
    host['vendor'] = vertex.properties['vendor']
    host['ansible_host'] = vertex.properties['ip']
    host['mac'] = vertex.properties['mac']

    if vertex.is_type('crucible::VM'):
        host['vm_spec'] = {
            'cpu_cores': vertex.properties['cpu-cores'],
            'ram_mib': vertex.properties['ram']['$number'] // 1048576,
            'disk_size_gb': vertex.properties['disk']['$number'] // 1000000000
        }

    if 'bmc' in vertex.capabilities:
        host['bmc_address'] = vertex.capabilities['bmc'].properties['ip']

    bmc = vertex.get_policies('crucible::BMC')
    if bmc:
        host['bmc_user'] = bmc[0].properties['user']
        host['bmc_password'] = bmc[0].properties['password']

    return host


if __name__ == "__main__":
    main()
