# Steps to configure the Bastion Host VM

This instructions will help you set up the Bastion Host VM for the fully virtualized environment. Please note that
this guide assumes that the host is running RHEL 8.5 and it has a registered subscription.

## Create the redhat user

> [root]# useradd redhat

### Create the crucible group

> [root]# groupadd crucible

Add the redhat user to the crucible group

> [root]# usermod -aG crucible redhat

Make the crucible group sudo passwordless by editing the sudoers file

> [root]# vim /etc/sudoers

    # Add the following line
    %crucible ALL=(ALL) NOPASSWD: ALL

### Check VM network configuration

You will need two network interfaces. The first one (enp1s0 in the diagram) must have access to the Internet. The second one (enp7s0 in
the diagram) does not need an IP address, just needs to be up.

### Create ssh key

> $ ssh-keygen -t rsa -N '' -b 4096
> 
> $ ssh-copy-id redhat@localhost

### Install Ansible

Install the EPEL repository

> $ sudo subscription-manager repos --enable="rhocp-4.9-for-rhel-8-x86_64-rpms"
> 
> $ sudo subscription-manager repos --enable="ansible-2.9-for-rhel-8-x86_64-rpms"

Install Ansible

> $ sudo yum install ansible

### Install git package

> $ sudo yum install git
