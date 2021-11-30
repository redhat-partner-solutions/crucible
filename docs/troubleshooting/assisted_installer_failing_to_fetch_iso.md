If you are seeing entries like the one below in the logs of `installer` container:

```
level=fatal msg="Failed to upload boot files" func=main.main.func1 file="/go/src/github.com/openshift/origin/cmd/main.go:191" error="Failed uploading boot files for OCP version 4.8: Failed fetching from URL https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.8/4.8.14/rhcos-4.8.14-x86_64-live.x86_64.iso: Get \"https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/4.8/4.8.14/rhcos-4.8.14-x86_64-live.x86_64.iso\": dial tcp: i/o timeout"
```
Then you should check if your containers can resolve `mirror.openshift.com`.
It could be that the hosts dns config is invalid for the container (e.g. 127.0.0.1).
An easy way to do this if you are using the `http_store` is run:

$ podman run -it httpd-24-centos7 /bin/bash
> $ dig mirror.openshift.com
> $ dig @8.8.8.8 mirror.openshift.com
> $ dig @8.8.4.4 mirror.openshift.com

`8.8.8.8` and `8.8.4.4` is the fallback in the case that they are also unavailable. 
Then you will need to either add a valid dns server to the host config or add a `dns` entry with a valid server to the `assisted_installer` host.
