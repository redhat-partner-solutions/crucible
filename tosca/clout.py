
import puccini.tosca


class Clout:
    def __init__(self, url):
        data = puccini.tosca.compile(url)
        #ard.write(clout, sys.stdout)
        self.data = data
        self.vertexes = self.data['vertexes']

    def get_vertexes(self, kind, type_=None):
        vertexes = {}
        for id_, vertex in self.vertexes.items():
            if get_kind(vertex) == kind:
                if (type_ is None) or (type_ in vertex['properties']['types']):
                    vertexes[id_] = Vertex.new(vertex, id_, self)
        return vertexes


class Vertex:
    @staticmethod
    def new(data, id_, clout):
        kind = get_kind(data)
        if kind == 'NodeTemplate':
            return NodeTemplate(data, id_, clout)
        elif kind == 'Group':
            return Group(data, id_, clout)
        elif kind == 'Policy':
            return Policy(data, id_, clout)
        else:
            return Vertex(data, id_, clout)

    def __init__(self, data, id_, clout):
        self.data = data
        self.id = id_
        self.clout = clout

    def get_edges(self, kind, name=None):
        edges = []
        for edge in self.data['edgesOut']:
            if get_kind(edge) == kind:
                if (name is None) or (edge['properties']['name'] == name):
                    edges.append(Edge.new(edge, self))
        return edges

    def get_edge_targets(self, kind, name=None):
        targets = []
        for edge in self.get_edges(kind, name):
            targets.append(edge.target)
        return targets


class NodeTemplate(Vertex):
    def __init__(self, data, id_, clout):
        super().__init__(data, id_, clout)
        self.name = self.data['properties']['name']
        self.properties = self.data['properties']['properties']
        self.capabilities = {}
        for name, capability in self.data['properties']['capabilities'].items():
            self.capabilities[name] = Capability(capability, self)

    def is_type(self, type_):
        return type_ in self.data['properties']['types']

    def get_groups(self, type_=None):
        '''
        All groups to which this node belongs
        '''
        groups = []
        for group in self.clout.get_vertexes('Group', type_).values():
            for target in group.get_edge_targets('Member'):
                if target.id == self.id:
                    groups.append(group)
        return groups

    def get_policies(self, type_=None):
        '''
        Policies that apply to this node or to a group that contains this node
        '''
        policies = []
        for policy in self.clout.get_vertexes('Policy', type_).values():
            for node_template in policy.get_all_node_template_targets():
                if node_template.id == self.id:
                    policies.append(policy)
        return policies


class Group(Vertex):
    def __init__(self, data, id_, clout):
        super().__init__(data, id_, clout)
        self.name = self.data['properties']['name']
        self.properties = self.data['properties']['properties']

    def get_members(self):
        return self.get_edge_targets('Member')


class Policy(Vertex):
    def __init__(self, data, id_, clout):
        super().__init__(data, id_, clout)
        self.name = self.data['properties']['name']
        self.properties = self.data['properties']['properties']

    def get_all_node_template_targets(self):
        node_templates = []
        for node_template in self.get_node_template_targets():
            node_templates.append(node_template)
        for group in self.get_group_targets():
            for node_template in group.get_members():
                node_templates.append(node_template)
        return node_templates

    def get_node_template_targets(self):
        return self.get_edge_targets('NodeTemplateTarget')

    def get_group_targets(self):
        return self.get_edge_targets('GroupTarget')


class Edge:
    @staticmethod
    def new(data, vertex):
        kind = get_kind(data)
        if kind == 'Relationship':
            return Relationship(data, vertex)
        else:
            return Edge(data, vertex)

    def __init__(self, data, vertex):
        self.data = data
        self.vertex = vertex
        target_id = self.data['targetID']
        self.target = Vertex.new(self.vertex.clout.vertexes[target_id], target_id, self.vertex.clout)

    def is_type(self, type_):
        return type_ in self.data['properties']['types']


class Relationship(Edge):
    def __init__(self, data, vertex):
        super().__init__(data, vertex)
        self.target_capability_name = self.data['properties']['capability']
        self.target_capability = self.target.capabilities[self.target_capability_name]
        self.properties = self.data['properties']['properties']


class Capability:
    def __init__(self, data, vertex):
        self.data = data
        self.vertex = vertex
        self.properties = self.data['properties']

    def is_type(self, type_):
        return type_ in self.data['types']


def get_kind(data):
    if ('metadata' in data) and ('puccini' in data['metadata']) and ('kind' in data['metadata']['puccini']):
        return data['metadata']['puccini']['kind']
    else:
        return None
