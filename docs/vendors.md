# Making new vendors

If we do not have the tasks required to boot your vendor then you are free to add your own.
Add a role into the `roles/vendors` the name of the role (must be all lower case) will be used as the vendor in the inventory.
The vendor role is required to have two task entry points `iso.yml` and `disk.yml` which will be called from `boot_iso` and `boot_disk` respectively.
