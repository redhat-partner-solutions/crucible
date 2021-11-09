# Discovery ISO not booting

> ❗ _Red Hat does not provide commercial support for the content of this repo. Any assistance is purely on a best-effort basis, as resource permits._

Sometimes the discovery iso will not boot here are a few things to check.

## Dell

### Plugin type

For some versions of iDRAC the plug-in type can stop the boot iso from working. If you are trying to install Redhat Openshift Container Platform (RHCOP) version `>=4.7` then follow the instructions bellow from the [ipi docs](https://docs.openshift.com/container-platform/4.7/installing/installing_bare_metal_ipi/ipi-install-installation-workflow.html)

```
There is a known issue with version 04.40.00.00. With iDRAC 9 firmware version 04.40.00.00, the Virtual Console plug-in defaults to eHTML5, which causes problems with the InsertVirtualMedia workflow. Set the plug-in to HTML5 to avoid this issue. The menu path is: Configuration → Virtual console → Plug-in Type → HTML5 .
```

Note if you are trying to install RHOCP version `4.6` then the plugin-in should be set to `eHTML5`.

### Clear UEFI Boot entries

For RHOCP version `4.8` sometimes wont boot despite the plug-in type correct. Try the following:

1. (Re)Boot machine
2. Hit F11 to enter Boot Manager
3. Select "One-shot UEFI Boot Menu"
4. Scroll to the bottom and select "Delete Boot Option"
5. Select all options
6. Click "Commit Changes and Exit"
7. Click "Finish"
8. Click "Finish" & Confirm exit
