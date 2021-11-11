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

import puccini.tosca, copy

from ansible.errors import AnsibleParserError
from ansible.plugins.inventory.yaml import InventoryModule as YAMLInventoryModule

from ..module_utils.inventory import Inventory
from ..module_utils.clout import Clout


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
        patched_loader.load_from_file = self._load_from_tosca_file

        # Use the built-in Ansible YAML Inventory Plugin to parse the Inventory
        # dynamically generated on an invocation of the patched loader function.
        super(InventoryModule, self).parse(inventory, patched_loader, path, cache)

        # To ensure all subsequent uses of the loader maintain the expected base
        # behavior, reassign the loader back to the original one.
        # TODO: have we changed the loader anywhere?
        self.loader = loader

    def _load_from_tosca_file(self, path, cache=False):
        return self._new_inventory_from_url_as_dict(path)

    def _new_inventory_from_url_as_dict(self, url):
        """Reads a TOSCA file, compiles it to Clout, and then returns the
            generated inventory as a Python dict."""
        try:
            return Inventory.new_from_url(url).as_dict()
        except puccini.tosca.Problems as e:
            raise AnsibleParserError(e.problems)
