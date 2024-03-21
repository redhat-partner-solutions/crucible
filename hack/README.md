# generate_os_release_images.py

## Requriments

```shell
pip install semver beautifulsoup4
```

## Usage
Can be used to generate `os_images` and `release_images`.

Here's an example for multiple different ocp versions:
```shell
./generate_os_release_images.py -a x86_64 -v 4.12.29 -v 4.11.30 -v 4.13.2 -v 4.14.12 -v 4.15.1
```
