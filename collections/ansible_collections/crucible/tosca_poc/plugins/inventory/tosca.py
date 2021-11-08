from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: tosca
    version_added: "2.9"
    short_description: Consumes a TOSCA service instance file, which is then translated into a valid Crucible YAML Inventory.
    options:
      yaml_extensions:
        description: list of 'valid' extensions for the TOSCA files in YAML format
        type: list
        default: ['.yaml', '.yml']
'''

from ansible.errors import AnsibleParserError
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.module_utils._text import to_native
from ansible.plugins.inventory.yaml import InventoryModule as YAMLInventoryModule

from crucible_tosca_poc.inventory import Inventory as CloutToYAMLInventory
from crucible_tosca_poc.clout import Clout


class InventoryModule(YAMLInventoryModule):

    NAME = 'tosca'

    def __init__(self):
        super(InventoryModule, self).__init__()

    def parse(self, inventory, loader, path, cache=True):
        # This method is based on the parse() method from the YAML Inventory plugin
        # https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/inventory/yaml.py

        data = self._get_inventory_as_python_dict(path)

        if not data:
            raise AnsibleParserError('The provided inventory is empty.')
        elif not isinstance(data, MutableMapping):
            raise AnsibleParserError('YAML inventory has invalid structure. It should be a dictionary, got: %s' % type(data))

        # We expect top level keys to correspond to groups, iterate over them
        # to get host, vars and subgroups (which we iterate over recursivelly)
        if isinstance(data, MutableMapping):
            for group_name in data:
                self._parse_group(group_name, data[group_name])
        else:
            raise AnsibleParserError("Invalid data from file, expected dictionary and got:\n\n%s" % to_native(data))

    def _get_inventory_as_python_dict(path):
        """Reads the TOSCA file, compiles it to Clout, and then returns the inventory as a Python dict."""
        try:
            clout_obj_from_tosca_source = Clout(path)
            inventory = CloutToYAMLInventory(clout_obj_from_tosca_source)
            data = inventory.as_dict()
        except puccini.tosca.Problems as e:
            raise AnsibleParserError(e)

        return data
