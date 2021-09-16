# Crucible | Connecting to hosts

> ❗ _Red Hat does not provide commercial support for the content of this repo. Any assistance is purely on a best-effort basis, as resource permits._

---
```bash
##############################################################################
DISCLAIMER: THE CONTENT OF THIS REPO IS EXPERIMENTAL AND PROVIDED "AS-IS"

THE CONTENT IS PROVIDED AS REFERENCE WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
##############################################################################
```
---

## Connecting to hosts as crucible user
---
1. Connect to the bastion host as your personal user.
2. _SU_ to the crucible user
3. Execute playbooks as _crucible_ user

```
                                  │
                                  │                         ┌────────────┐
                                  │                         │            │
                                  │                   ┌─────┤ HTTP STORE │
                                  │                   │     │            │
                                  │                   │     └────────────┘
                                  │                   │
                                  │                   │     ┌─────────┐
                                  │                   │     │         │┐
                            ┌─────┼─────┐             ├─────┤ WORKERS ││┐
┌────────────┐              │     │     │             │     │         │││
│ System     │              │  Bastion  │             │     └─────────┘││
│ Integrator ├─────ssh──────►     │     ├──ssh as─────┤      └─────────┘│
│ Host       │ user@bastion │ Command & │ crucible@   |       └─────────┘
└────────────┘              │  Control  │             |
                            └─────┼─────┘             │     ┌──────────┐
                                  |                   │     │          │
                                  |                   ├─────┤ REGISTRY │
                                  |                   │     │          │
                                  │                   │     └──────────┘
                                  │                   │
                                  │                   │     ┌───────────┐
                                  │                   │     │           ├┐
                                  │                   └─────┤ SUPER1-3  │├┐
                                  │                         │           ││|
                                  │                         └┬──────────┘│|
                                  │                          └───────────┘|
                                  │                           └───────────┘
                                  │
                                  │
```
