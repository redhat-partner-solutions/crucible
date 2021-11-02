
import puccini.tosca


class Clout:
    def __init__(self, url):
        data = puccini.tosca.compile(url)
        #ard.write(clout, sys.stdout)
        self.data = data
        self.vertexes = self.data['vertexes']

    def get_vertexes(self, kind, type_):
        vertexes = {}
        for id, vertex in self.vertexes.items():
            if vertex['metadata']['puccini']['kind'] == kind:
                if type_ in vertex['properties']['types']:
                    vertexes[id] = Vertex(vertex, id, self)
        return vertexes


class Vertex:
    def __init__(self, data, id_, clout):
        self.data = data
        self.id = id_
        self.clout = clout
        self.name = self.data['properties']['name']
        self.properties = self.data['properties']['properties']
        if 'capabilities' in self.data['properties']:
            self.capabilities = {}
            for name, capability in self.data['properties']['capabilities'].items():
                self.capabilities[name] = Capability(capability, self)

    def is_type(self, type_):
        return type_ in self.data['properties']['types']

    def get_edges(self, kind, name=None):
        edges = []
        for edge in self.data['edgesOut']:
            if edge['metadata']['puccini']['kind'] == kind:
                if (name is None) or (edge['properties']['name'] == name):
                    edges.append(Edge(edge, self))
        return edges

    def get_policies(self, type_):
        policies = []
        for policy in self.clout.get_vertexes('Policy', type_).values():
            for edge in policy.get_edges('NodeTemplateTarget'):
                if edge.target.id == self.id:
                    policies.append(policy)
        return policies


class Edge:
    def __init__(self, data, vertex):
        self.data = data
        self.vertex = vertex
        vertexes = self.vertex.clout.vertexes
        target_id = self.data['targetID']
        self.target = Vertex(vertexes[target_id], target_id, self.vertex.clout)
        if 'capability' in self.data['properties']:
            capability_name = self.data['properties']['capability']
            self.target_capability = self.target.capabilities[capability_name]
        if 'properties' in self.data['properties']:
            self.properties = self.data['properties']['properties']

    def is_type(self, type_):
        return type_ in self.data['properties']['types']


class Capability:
    def __init__(self, data, node_vertex):
        self.data = data
        self.vertex = node_vertex
        self.properties = self.data['properties']

    def is_type(self, type_):
        return type_ in self.data['types']
