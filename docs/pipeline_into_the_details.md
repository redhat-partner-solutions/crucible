## Pipeline into the details
### ‘Prerequisite’ / ‘Deployment’ / ‘Configuration’ - Management cluster
#### _Using Assisted Installer_
---
#### --- PRIVATE AND CONFIDENTIAL, DO NOT DISTRIBUTE ---
---

1. Prerequisite Stage:
    1. Manual Steps:
        - BIOS & Firmware updates on all servers
        - Networks configurations:
            - Switch configuration
            - Subnet configurations
    2. Ansible Orchestration - via jumphost:
        - Generate SSH key pair used for debugging deployments
        - Set up local container for the registry
        - The Container registry for hosting and distributing additional container images:
            - `openshift-release-dev/ocp-release`
            - `ocpmetal/assisted-installer-controller`
            - `ocpmetal/assisted-installer-agent`
            - `ocpmetal/assisted-installer`
            - `olm-index/redhat-operator-index`
        - HTTP Store (optional):
            - Is HTTP Store a pre-exisiting server?
            - Setup HTTP Server
        - DNS (optional):
            - Is DNS pre-existing?
            - Setup DNSMASQ DNS Server
        - NTP (optional):
            - Is NTP pre-existing?
            - Setup Chrony NTP Server
        - Podman creates the Assisted Installer pod:
            - Installer
            - DB
            - UI
        - Launch stand alone Assisted Installer with REST API capabilities.
2. Configuration:
    - Assisted Installer:
        - Create cluster deployment
        - Configure cluster deployment
            - Redirects for the repose of the registry:
                - QUAY
                - SSL
        - Restricted network install customizations (optional)
        - Network SDN drivers (optional):
            - Openshift SDN
            - OVN Kubernetes
        - API discovery ISO customizations:
            - Static IPs:
        - Download the Discovery ISO:
            - Copy to the HTTP Store.
3. Discovery:
    - Mount the Discovery ISO from the HTTP Store on target hosts
    - Set ISO to boot media on target hosts
    - Reboot hosts into Discovery ISO
4. Post discovery:
    - Apply additional cluster install configurations:
        - Ingress VIP
        - API Controller
    - Assign roles to discovered hosts
5. Deploy / Install Management Cluster:
    - Trigger install via the Assisted Installer REST API.
    - Monitor install via the Assisted Installer REST API.
6. Post Flight:
    - Retrieve kubeconfig and save it to jumphost




__Note__: Time for the above procedure is about 1.5hr, on Bare Metal Servers.




#### COMING SOON:
Apply a workload configuration manifests:
Persistent Storage
Advanced Cluster Manager
Creation of the ACM Pods on the Management Cluster(Workers).
Using the ACM in order to deploy OpenShift on the DU & CU servers.
