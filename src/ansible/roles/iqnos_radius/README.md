# Ansible Role for RADIUS 
Ansible Role for RADIUS is used to configure the RADIUS servers and the authentication policy for the network elements.

## Pre-requisites and conditions for the Ansible role RADIUS

* Host file lists all the network elements and its details. See example file "hosts.yml".
* Host group specifies the group of hosts to be used. See example "db_group" in "hosts.yml" file.
* Input configuration file lists the inputs required to run tasks within this role. See example file "group_vars/config.yml".
* Updated configuration file name or name of the config.file that contains inputs required to run the tasks. See example file "group_vars/iqnos_radius_config.yml".

## User tasks and capabilities

* Retrieve the existing RADIUS configuration.
* Validate the configurations periodically.
* Configure the new RADIUS configuration.
   - User can either configure all of the parameters or configure requried parameters only.
   - A maximum of three RADIUS servers are supported; user can configure all of them or specific ones.

### Note:
    * Input configurations are applied only if the existing configuration is not same as new configuration.
    * IPv4/IPv6 server configurations are supported.

 ## Supported Tasks
  
| Tasks | Description| Tags | Input|
|----|------------|----|----|
|radius_configuration|Edit the RADIUS configuration|config|[server_configs](#Authentication-Policy-Configuration-Variables)|
|auth_policy_configuration|Edit the Authentication Policy|auth_config|[auth_configs](#Server-Configuration-Variables)|
|radius_retrieve|Retrieve the RADIUS servers and the associated configurations from the network element. |retrieve|NA|
|auth_policy_retrieve|Retrieve the Authentication policy from the network element |auth_retrieve|NA|
||||| 
 


## Configuration variables for RADIUS server  

| Variable | Type | Description|Valid Instances/Ranges| Mandatory| Validated|
| ----|------|------------|------------|----------|--------|
|identifier| string| Indicates which RADIUS server to edit|<ul><li>RADSERVER1</li><li>RADSERVER2</li><li>RADSERVER3</li></ul>|Yes|Yes|
|ipaddress |IPv4/IPv6 address|RADIUS server IP Address|Valid IPv4/IPv6 address|No|Yes|
|port |int|RADIUS authentication port number|1024 to 65535|No|Yes|
|timeout  |int|RADIUS authentication request time out in `seconds`|1 to 90|No|Yes|
|shared_secret_key |string|RADIUS shared secret key|16 to 128 characters long|No|Yes|
|max_attempts|int|Maximum number of attempts per RADIUS server|1 to 5|No|Yes|
||||||

## Authentication policy configuration variables

| Variable | Type | Description| Valid Instances| Mandatory| Validated|
|----|------|------------|----------------|----------|---------|
|auth_policy| string| The `user` authentication policy|<ul><li>LOCAL</li><li>RADIUS</li><li>RFL</li></ul>|Yes|Yes|
|||||

## Sample configuration file to perform all the RADIUS server tasks

```yaml
---
#RADIUS Configuration template.


  # Network element allows maximum of three Radius servers[RADSERVER1/RADSERVER2/RADSERVER3] to configure.
  # Below is the sample template to configure the RADIUS servers on the Network element.

  ########################################################################################
  #                                                                                      #
  # identifier        = Indicates which RADIUS server to edit.                           #
  # host              = Radius server ip_address                               #
  # port              = Radius authentication port number.                               #
  # timeout           = Radius authentication request time out in [seconds].             #
  # shared_secret_key = Radius shared secret of range 16 to 128 characters.              #
  # max_attempts      = Maximum number of attempts per radius server.                    #
  #                                                                                      #
  ########################################################################################
server_configs:
  server1:
    identifier       : RADSERVER1
    ipaddress        : 1.1.1.1
    port             : 1823
    timeout          : 10
    shared_secret_key: secretkey1secretkey1
    max_attempts     : 3

  # server2:
  #   identifier       : RADSERVER2
  #   ipaddress        : 2.2.2.2
  #   port             : 1823
  #   timeout          : 10
  #   shared_secret_key: secretkey2secretkey2
  #   max_attempts     : 3

  # server3:
  #   identifier       : RADSERVER3
  #   ipaddress        : 3.3.3.3
  #   port             : 1823
  #   timeout          : 10
  #   shared_secret_key: secretkey3secretkey3
  #   max_attempts     : 3

#Below are the possible options can be configured as a RADIUS authentication policy:
# LOCAL  - Users are authenticated according to the Local settings on the network element.
# RADIUS - Users are authenticated according to the settings on the RADIUS servers that are configured for the network element.
# RFL    - Users are authenticated first according to the settings on the RADIUS servers.
#          If no RADIUS server can be contacted,  users are authenticated according to the local settings on the network element.

auth_configs:
  auth_policy: LOCAL
```

## Sample RADIUS server Playbook

```yaml
# For input configurations please refer/edit group_vars/iqnos_radius_config.yml
- hosts: "{{ host_group }}"
  connection: local
  gather_facts: False
  vars_files:
    - "{{ cfg_file }}"
    - "{{ mapper_file | default('group_vars/radius_mapper.yml') }}"
  vars:
     NE_IP: "{{ ne_ip | default(hostvars[inventory_hostname]['ansible_host']) }}"
     NE_User: "{{ ne_user | default(hostvars[inventory_hostname]['ansible_user']) }}"
     NE_Pwd: "{{ ne_pwd | default(hostvars[inventory_hostname]['ansible_password']) }}"

  tasks:

    - import_role:
        name: iqnos_radius
      vars:
        task_name: "radius_retrieve"
      tags: retrieve

    # Please refer/edit group_vars/iqnos_radius_config.yml - server_configs
    - import_role:
        name: iqnos_radius
      vars:
        task_name: "radius_configuration"
      tags: config

    - import_role:
        name: iqnos_radius
      vars:
        task_name: "auth_policy_retrieve"
      tags: auth_retrieve

    # Please refer/edit group_vars/iqnos_radius_config.yml - auth_configs
    - import_role:
        name: iqnos_radius
      vars:
        task_name: "auth_policy_configuration"
      tags: auth_config
```

## Commands to run the RADIUS server Playbook

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook radius_playbook.yml -e "cfg_file=group_vars/radius_cfgs.yml host_group=radius" -i myhosts.yml

## Commands to run the Playbook with tags for each of the RADIUS server tasks

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory --tags=tag1,tag2,tag3...`
* *Example*
  * ansible-playbook radius_playbook.yml -e "cfg_file=radius_cfgs.yml host_group=radius" -i myhosts.yml --tags=retrieve
  * ansible-playbook radius_playbook.yml -e "cfg_file=radius_cfgs.yml host_group=radius" -i myhosts.yml --tags=config,auth_config

> Providing a `host_group` along with the `cfg_file`(where applicable) is mandatory
>
> If no inventory file is passed, then default inventory is `hosts`

## License

BSD License 2.0

## Author Information

Infinera Corporation

Technical Support - techsupport@infinera.com
