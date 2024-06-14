# generate_os_release_images.py

## Requirements

```shell
python3 -m pip install -r ./requirements.txt
```

## Usage
Can be used to generate `os_images` and `release_images`.

Here's an example for multiple different ocp versions:
```shell
./generate_os_release_images.py -a x86_64 -v 4.12.29 -v 4.11.30 -v 4.13.2 -v 4.14.12 -v 4.15.1
```

## Sample Output
```yaml
os_images:
  - cpu_architecture: x86_64
    openshift_version: '4.14'
    rootfs_url: https://mirror.openshift.com/pub/openshift-v4/x86_64/dependencies/rhcos/4.14/4.14.15/rhcos-live-rootfs.x86_64.img
    url: https://mirror.openshift.com/pub/openshift-v4/x86_64/dependencies/rhcos/4.14/4.14.15/rhcos-4.14.15-x86_64-live.x86_64.iso
    version: 414.92.202402261929-0
release_images:
  - cpu_architecture: x86_64
    cpu_architectures:
      - x86_64
    openshift_version: '4.14'
    url: quay.io/openshift-release-dev/ocp-release:4.14.30-x86_64
    version: 4.14.30
```