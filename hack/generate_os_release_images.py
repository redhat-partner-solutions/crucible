#! /usr/bin/env python3

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
try:
    from semver import Version as VersionInfo
except ImportError:
    from semver import VersionInfo

import yaml

import requests
import re
import argparse

DEBUG = False

def generate_image_values(ocp_version, arch):
    rhcos = requests.get(
        f"https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/{ocp_version.major}.{ocp_version.minor}"
    )
    if not rhcos.ok:
        raise ValueError(
            f"Failed to find rhcos dependencies  for version: {ocp_version.major}.{ocp_version.minor}"
        )

    page = BeautifulSoup(rhcos.content, "lxml")
    versions = map(lambda p: p["href"].strip("/"), page.find_all("a")[1:-1])

    os_version = None
    for v in versions:
        ver = VersionInfo.parse(v)
        if ver.compare(ocp_version) < 1 and (
            os_version is None or os_version.compare(ver) == -1
        ):
            os_version = ver

    if os_version is None:
        raise ValueError(
            f"Failed to find a version <= {ocp_version} in {versions.join(', ')}"
        )

    release_info = requests.get(
        f"https://mirror.openshift.com/pub/openshift-v4/{arch}/clients/ocp/{os_version}/release.txt"
    )
    if not release_info.ok:
        raise ValueError(f"Failed to find release.txt for version: {os_version}")

    rhcos_version_match = re.search(
        r"^\s+machine-os (?P<rhcos_version>.+) Red Hat Enterprise Linux CoreOS$",
        release_info.content.decode(),
        re.MULTILINE,
    )
    rhcos_version = rhcos_version_match.groupdict()["rhcos_version"]

    if DEBUG:
        print(arch)
        print(ocp_version)
        print(os_version)
        print(rhcos_version)

    result = {
        "os_images": {
            str(os_version): {
                "openshift_version": f"{os_version.major}.{os_version.minor}",
                "cpu_architecture": f"{arch}",
                "url": f"https://mirror.openshift.com/pub/openshift-v4/{arch}/dependencies/rhcos/{os_version.major}.{os_version.minor}/{os_version}/rhcos-{os_version}-{arch}-live.{arch}.iso",
                "rootfs_url": f"https://mirror.openshift.com/pub/openshift-v4/{arch}/dependencies/rhcos/{os_version.major}.{os_version.minor}/{os_version}/rhcos-live-rootfs.{arch}.img",
                "version": f"{rhcos_version}",
            },
        },
        "release_images": [
            {
                "openshift_version": f"{ocp_version.major}.{ocp_version.minor}",
                "cpu_architecture": arch,
                "cpu_architectures": [arch],
                "url": f"quay.io/openshift-release-dev/ocp-release:{ocp_version}-{arch}",
                "version": str(ocp_version),
            },
        ],
    }

    return result


def merge_results(results):
    merged = {
        "os_images": {},
        "release_images": [],
    }

    for r in results:
        for os_v, os in r["os_images"].items():
            merged["os_images"][os_v] = os
        for os in r["release_images"]:
            merged["release_images"].append(os)

    res = {
        "os_images": [],
        "release_images": merged["release_images"],
    }

    for os in merged["os_images"].values():
        res["os_images"].append(os)

    return res


def verify_urls(merged):
    for os in merged["os_images"]:
        url_head = requests.head(os["url"])
        if not url_head.ok:
            raise ValueError(f"file not found at expected url {os['url']}")
        rootfs_url_head = requests.head(os["rootfs_url"])
        if not rootfs_url_head.ok:
            raise ValueError(f"file not found at expected url {os['rootfs_url']}")

    for release in merged["release_images"]:
        url_head = requests.head(os["url"])
        if not url_head.ok:
            raise ValueError(f"file not found at expected url {os['url']}")


def main(ocp_versions, arch, verify):
    results = []
    for v in ocp_versions:
        results.append(generate_image_values(v, arch))

    if DEBUG:
        print(results)

    merged_results = merge_results(results)
    if DEBUG:
        print(merged_results)

    class IndentDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(IndentDumper, self).increase_indent(flow, False)

    if verify:
        verify_urls(merged_results)

    print(yaml.dump(merged_results, Dumper=IndentDumper))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--arch",
        help="target archictecture",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="append",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    DEBUG = args.debug

    ocp_versions = []
    for v in args.version:
        ocp_versions.append(VersionInfo.parse(v))

    main(ocp_versions=ocp_versions, arch=args.arch, verify=args.skip_verify)
