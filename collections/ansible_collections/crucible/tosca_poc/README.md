# Crucible TOSCA PoC Collection

This collection provides the code necessary to expose an alternative user interface for Crucible using TOSCA.

TOSCA files can be consumed using a dedicated Inventory plugin which parses, validates, compiles and then translates the source files into Crucible-specific YAML Inventory schema.

## Enabling the Inventory plugin

In order to use the Inventory plugin, add `crucible.tosca_poc.tosca` to the list of enabled plugins in the `ansible.cfg` configuration file.

```
[inventory]
enable_plugins = crucible.tosca_poc.tosca, yaml
```

## Example usage

The following command runs Crucible's main playbook (`site.yml`) with a provided Inventory file in a TOSCA format.

```
ansible-playbook site.yml -i tosca/simple.yaml
```
