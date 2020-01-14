# Infinera Network Automation Module Installation Guide

This document provides detailed instructions to install the Infinera Network Automation modules and Ansible.

## Listed below are the  characteristic features of Ansible

- Ansible manages machines over the SSH protocol by default. 
- With Ansible installed, there is no database added and no daemons to start or keep running. 
- Installing Ansible on one machine, a laptop for instance, can manage an entire fleet of remote machines from a single laptop. 
- Ansible only manages remote machines, these machines do not need software installed, so there is no upgrade issue to a new version of Ansible.

### Control Node

 The device with Ansible installed is considered the control node.
 Ansible on the control node currently works on any machine with Python 2 (version 2.7 and higher) or Python 3 (version 3.5 and higher) installed. Control nodes do not support Windows operating system.

### Managed Node

The devices managed with Ansible is considered the managed node. Managed nodes by default use sftp for communication. If sftp is unavailable, switch to scp in ansible.cfg. Managed node also requires Python 2 (version 2.7 and higher) or Python 3 (version 3.5 and higher) installed.

## Steps to install Ansible

1. Navigate to https://www.python.org/ on the web browser.


2. Select the link to download and click Python version 2.7.15+ installer listed.

3. Run the installer and follow the installation steps.

4. Install the python packages and click finish.

    The ansible roles require the following python packages to be installed

    netaddr (Used for validation of IPv4/IPv6 addresses; internally)
  
```bash
  pip install netaddr
```

  * jinja2 (Version 2.10.1)
  
           ```bash
             pip install jinja2==2.10.1
           ```

  * jsonschema (Used for validating the input configurations against a predefined JSON schema)

           ```bash
            pip install jsonschema[format]
           ```

5. Execute the following commands to install the Ansible version 2.8 with any of the below    listed environments

   - Red Hat or CentOS

     ```bash
     sudo yum install ansible
     ```

   - Ubuntu

      ```bash
      sudo apt-get update
      sudo apt-get install software-properties-common
      sudo apt-add-repository --yes --update ppa:ansible/ansible
      sudo apt-get install ansible
      ```

   - pip

      ```bash
      sudo pip install ansible
      ```

6. Execute the following commands and verify the installation 

```shell
# Check version
ansible --version

# For printing help doc
ansible -help
```

7. Set the `ANSIBLE_CONFIG` environmental variable to the `ansible.cfg` file present in the `src/ansible/` folder

```shell
cd src/ansible
export ANSIBLE_CONFIG=./ansible.cfg
```

> The above approach has to be repeated everytime we open a new shell
>
> Instead, the variable can be set in the `~/.bash_profile` file.
>
> Follow the below procedure to accomplish it -
>
> 1. `vim ~/.bash_profile`
>
> 2. Press the `i` key or the `insert` key and go to the end of the file by scrolling down with the `down-arrow` key
>
> 3. Type in the following line after reaching the bottom of the file - `shell ANSIBLE_CONFIG=path_to_the/ansiblefolder_with_infinera_code/ansible.cfg`
>
> 4. Once the line ine entered press the `escape` followed by the `:` key (colon) and `q` key and press `enter`
>
> 5. This can be checked by running the following - `printenv ANSIBLE_CONFIG`

## Installing Infinera Module

### Installing the Infinera ansible module from a ‘tar’ file Ex : infn-net-ansible-playbooks-1.0.0-66.tar.gz

Copy this file to the machine or VM to any folder and follow the below steps

1. Create directory “/opt/infn/”
2. Copy infn-net-ansible-playbooks-1.0.0-66.tar.gz file to “/opt/infn/”
3. Extract contents
   3.1 tar -xv --file=infn-net-ansible-playbooks-1.0.0-66.tar.gz
   3.2 Navigate to directory - cd “/opt/infn/src/ansible/”
4. Update host file
   - Update inventory of network element in hosts.yml
5. Start executing ansible playbooks

## Installing the Infinera ansible module using `git clone`

1. Create directory “/opt/infn/”
2. Run `git clone <link_to_repository>` inside the above directory
3. Update host file
   - Update inventory of network element in hosts.yml
4. Start executing ansible playbooks

> For Supported Roles , please refer [Supported Roles](/src/ansible/README.md)

## Links for Reference

* [Ansible 2.9 Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
* [Python](https://www.python.org/downloads/)
