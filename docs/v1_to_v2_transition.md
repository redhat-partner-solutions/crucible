# API v1 to v2 transition. 

Crucible has moved from assisted installer v1 API to v2. 
In doing so we have renamed the pod running assisted installer to be inline with assisted installers podman deployment documentation. 
To allow the transition to take play you will need to remove the v1 assisted installer pod `podman pod rm -f assisted-service`. 
It may also help to remove anything left behind from the previous pod in the `assisted_installer_dir`(default: `/opt/assisted-installer`). 
You may want to back this up if you need any infomation the then previous deployments held in assisted installer.

In addition to the three previous containers, there is a new image service. 
For assisted installer to work correctly with this service the assisted installer pod must be able to resolve the image service (by default this will be the `host` var in the `assisted_installer` host definition). So if a domain is being used you will need to add the ip address to your DNS server to the `dns_servers` in the `assisted_installer` host definition:

```yaml
...
services:
  hosts:
    assisted_installer:
      ansible_host: service_host.example.lab
      host: service_host.example.lab
      port: 8090 
      dns_servers:
        - 10.40.0.100
        - 8.8.8.8
        - 4.4.4.4
...
```

## Overrides

The Assisted Installer has changed the structure of the required data for defining OpenShift versions available to install. If you have overridden the images you will need to split the former data into two parts as follows:
```yaml
assisted_service_openshift_versions_defaults:
  "4.6":
    display_name: 4.6.16
    release_image: "quay.io/openshift-release-dev/ocp-release{% if 'release_4.6' in image_hashes %}@{{ image_hashes['release_4.6'] }}{% else %}:4.6.17-x86_64{% endif %}"
    release_version: 4.6.16
    rhcos_image: https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.6/4.6.8/rhcos-4.6.8-x86_64-live.x86_64.iso
    rhcos_rootfs: https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.6/4.6.8/rhcos-live-rootfs.x86_64.img
    rhcos_version: 46.82.202012051820-0
    support_level: production
    ...
```

becomes two dicts (notice that the value in the new version is a list):

```yaml
os_images:
  - openshift_version: '4.6'
    cpu_architecture: x86_64
    url: https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.6/4.6.8/rhcos-4.6.8-x86_64-live.x86_64.iso
    rootfs_url: https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.6/4.6.8/rhcos-live-rootfs.x86_64.img
    version: 46.82.202012051820-0
  ...
release_images:
  - openshift_version: '4.6'
    cpu_architecture: x86_64
    url: quay.io/openshift-release-dev/ocp-release:4.6.16-x86_64
    version: 4.6.16
  ...
```

## Proxy

For people using proxies you will need to make HTTP_PROXY, HTTPS_PROXY and NO_PROXY all lower case. 
