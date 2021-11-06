If you are seeing entries like the one below in the logs of `installer` container:

```
level=fatal msg="Failed to upload boot files" func=main.main.func1 file="/go/src/github.com/openshift/origin/cmd/main.go:191" error="Failed uploading boot files for OCP version 4.8: Failed fetching from URL https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.8/4.8.14/rhcos-4.8.14-x86_64-live.x86_64.iso: Get \"https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.8/4.8.14/rhcos-4.8.14-x86_64-live.x86_64.iso\": dial tcp: i/o timeout"
```

Then you should check if your containers can resolve `mirror.openshift.com`. An easy way to do this if you are running the http_store is run:

```
$ podman exec -it http_store /bin/bash
> $ ping mirror.openshift.com
> $ ping 8.8.8.8
```

if `mirror.openshift.com` fails to respond but `8.8.8.8` does then you can try configuring the `dns` entry in the `assisted_installer` host.
