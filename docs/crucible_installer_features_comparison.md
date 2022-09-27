# Crucible Features

This is a comparison of the features available through crucible depending on which installer is used

| Feature                                            | Assisted installer (on-prem)  | Agent based installer    |
| -------------------------------------------------- | ----------------------------- | ------------------------ |
| Compact cluster                                    | Y                             | Y                        |
| Workers                                            | Y                             | Y                        |
| SNO                                                | Y                             | Y                        |
| 2 day workers                                      | Y                             | N[1]                     |
| Set Network type                                   | Y                             | Y                        |
| DHCP                                               | Y                             | Y[2]                     |
| IPV6                                               | Y                             | Y                        |
| Dual Stack                                         | Y                             | Y                        |
| NMState network config                             | Y                             | Y                        |
| Mirror Registry support                            | Y                             | Y                        |
| Set hostname                                       | Y                             | Y                        |
| Set role                                           | Y                             | Y                        |
| Proxy                                              | Y                             | Y                        |
| Install OLM Operators (LSO, ODF, CNV)              | Y                             | N[3]                     |
| Partitions                                         | Y                             | N[4]                     |
| Discovery iso password                             | Y                             | N[4]                     |
| -                                                  | -                             | -                        |

Footnotes:
[1] There are plans for the agent based method to install the [multicluster engine operator](https://docs.openshift.com/container-platform/4.12/architecture/mce-overview-ocp.html) which crucible could then leverage to add day2 workers.
[2] A `network_config` is still required however you could provide a raw nmstate, which configures the interfaces for dhcp and the corresponding `mac_interface_map`. If you are not using the DHCP provided by crucible you would need to provide the correct IP for the bootstrap node (by default the first node in the masters group).
[3] It is possible to apply extra manifests to deploy those operators as part of the install. The MCE deploy ment mentioned in [1] will likely expose this feature as well.
[4] This feature of crucible is done by modifing an iginition file which is not currently possible in the agent based flow.
