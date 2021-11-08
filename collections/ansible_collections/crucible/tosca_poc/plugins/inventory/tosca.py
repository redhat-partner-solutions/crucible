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

import puccini
import copy

from ansible.errors import AnsibleParserError
from ansible.plugins.inventory.yaml import InventoryModule as YAMLInventoryModule

from ansible_collections.crucible.tosca_poc.plugins.module_utils.inventory import Inventory as CloutToYAMLInventory
from ansible_collections.crucible.tosca_poc.plugins.module_utils.clout import Clout


class InventoryModule(YAMLInventoryModule):

    NAME = 'tosca'

    def __init__(self):
        super(InventoryModule, self).__init__()

    def parse(self, inventory, loader, path, cache=True):
        # Monkey patch the loader in order to trick the parser into reading a
        # TOSCA file, instead of expecting a generic Ansible YAML Inventory file.
        # The patched loader returns a Python object compatible with the Ansible
        # YAML Inventory schema. The returned object is generated on the fly
        # based on the results of compiling provided TOSCA source files.

        patched_loader = copy.deepcopy(loader)
        patched_loader.load_from_file = self._load_yaml_inventory_compiled_from_tosca_file

        # Use the built-in Ansible YAML Inventory Plugin to parse the Inventory
        # dynamically generated on an invocation of the patched loader function.
        super(InventoryModule, self).parse(inventory, patched_loader, path, cache)

        # To ensure all subsequent uses of the loader maintain the expected base
        # behavior, reassign the loader back to the original one.
        self.loader = loader

    def _load_yaml_inventory_compiled_from_tosca_file(self, path, cache=False):
        yaml_inventory = self._get_inventory_as_python_dict(path)

        return yaml_inventory

    def _get_inventory_as_python_dict(self, path):
        """Reads a TOSCA file, compiles it to Clout, and then returns the
            generated inventory as a Python dict."""
        try:
            clout_obj_from_tosca_source = Clout(path)
            inventory = CloutToYAMLInventory(clout_obj_from_tosca_source)
            data = inventory.as_dict()
        except puccini.tosca.Problems as e:
            raise AnsibleParserError(e.problems)

        return data
