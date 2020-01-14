# Ansible Role for Network Time Protocol (NTP)

The Ansible role for Network Time Protocol is used to configure NTP server address and administrative state of the network elements.


## Pre-requisites and conditions for the Ansible role NTP:

1. The Host file lists all the network elements and their details. See example file "hosts.yml".
2. The Host group specifies the group of hosts to be used. See example "db_group" in "hosts.yml" file.
3. The input configuration file lists the inputs required to run the tasks within the NTP. See example file "group_vars/config.yml".
4. The updated configuration file name or name of the config.file contains inputs required to run the tasks. See example file "group_vars/iqnos_ntp_config.yml".

## User tasks and capabilities

1. Retrieve an existing NTP configuration.
2. User configurations are validated periodically.
3. User can perform a new NTP configuration.
4. User has permissions to set the administrative states of the NTP servers to Unlocked, Locked, Maintenance.
5. User can enable or disable the alarm reporting control.
6. Input configurations are provided only if the new configuration is different from the existing configuration.
7. IPv4/IPv6 server configurations are supported.
8. User can configure the requried parameters or all the parameters as applicable.
9. A maximum of three NTP server configuratuions are supported, of which user can configure a specific server or all servers, as applicable. 

## Supported Tasks

| Tasks | Description| Tags | Input|
|----|------------|----|----|
|validate|Validate the given input configurations against a JSON schema (See below for input configurations) |validate|[configs](#Sample-Configuration-File)|
|edit_ntp_config|Edit the NTP IP address of the NTP servers on the network element |edit|[server_configs](#Server-Configuration-Variables)|
|rtrv_ntp_config|Retrieve the NTP configurations from the network element. |retrieve|NA|
|lock_ntp|Lock the given NTP servers on the network element |lock|[state_configs](#State-Configuration-Variables)|
|unlock_ntp|Unlock the given NTP servers on the network element |unlock|[state_configs](#State-Configuration-Variables)|
|set_to_maintenance|Set the NTP servers to Maintenance state on the network element |set_to_maintenance|[state_configs](#State-Configuration-Variables)|
|remove_from_maintenance|Switch the the state of the NTP servers from Maintenance to Unlocked, on the network element |remove_from_maintenance|[state_configs](#State-Configuration-Variables)|
|rtrv_alarm_reporting|Retrieve the existing alarm reporting status for the NTP servers on the network element |retrieve_alarm_reporting|NA|
|enable_alarm_reporting|Enable the alarm reporting for the given NTP servers on the network element |enable_alarm_reporting|[alarm_configs](#Alarm-Configuration-Variables)|
|disable_alarm_reporting|Disable the alarm reporting for the given NTP servers on the network element |disable_alarm_reporting|[alarm_configs](#Alarm-Configuration-Variables)|
|||||

## Configuration variables to create NTP tasks

Every Network Time Protocol server configuration is ***created*** with a set of variables, details of which are listed below

| Variable | Type | Description| Valid Instances| Validated|
| ----:|------|------------|-----------|------|
|identifier| string| Indicates the  NTP server to be edited.|<ul><li>NTP-1</li><li>NTP-2</li><li>NTP-3</li></ul>|Yes|Yes|
|ipaddress |IPv4/IPv6 address|NTP server IP Address|Valid IPv4/IPv6 Address|Yes|
|||||

### NTP Administrative state configuration variables

| Variable | Type | Description| Valid Instances| Validated|
| ----:|------|------------|-----------|--------|
| identifiers| list| Indicates the NTP servers for which the administrative state is to be modified | List with all/either of these - NTP-1,NTP-2,NTP-3|Yes|
|||||

### NTP Alarm reporting control configuration Variables

| Variable | Type | Description| Valid Instances| Validated|
| ----:|------|------------|-----------|-----|
| identifiers| list| Indicates the NTP servers for which the alarm reporting control is to be modified | List with all/either of these - NTP-1,NTP-2,NTP-3|Yes|
|||||

### NTP Administrative State

| Administrative State | Primary State | Primary State Qualifier | Secondary State |
| ----:|------|------------|---------|
| Unlocked | IS (or) OOS | NR (or) AU | Does not contain MT |
| Locked | OOS | AUMA (or) MA | Does not contain MT |
| Maintenance | OOS | AUMA (or) MA | Contains MT |
||||

### NTP Alarm Reporting Control

| Alarm Reporting Control | State |
| ----:|------|
| IND | Disabled |
| RLS | Enabled |
|||

## Sample configuration file to perform the NTP tasks

```yaml
---
# NTP server configuration .
# Maximum of three NTP servers(NTP-1,NTP-2,NTP-3) are allowed to be configured for a given network element.
# Below is the sample template to configure the NTP servers for a given network element.
# IPv4 and IPv6 addresses are supported.
server_configs:
  server1:
    identifier       : NTP-1
    ipaddress        : 10.100.18.111

  # server2:
  #   identifier       : NTP-2
  #   ipaddress        : 2001:0db8:85a3:0000:0000:8a2e:0370:7334 #ip v6

  # server3:
  #   identifier       : NTP-3
  #   ipaddress        : 0.0.0.3

# NTP server state configuration template.
# This configuration is used for changing the state of the NTP server 
# Supported states are lock,unlock and maintenance 
state_configs:
  identifiers:
    - NTP-1
    - NTP-2
    - NTP-3

# NTP server alarm reporting configuration.
# This configuration is used for changing the alarm reporting setting 
# use this for enabling/ disabling alarm reporting
alarm_configs:
  identifiers:
    - NTP-1
    - NTP-2
    - NTP-3
```

## Sample NTP Playbook

```yaml
# For input configurations please refer/edit group_vars/iqnos_ntp_config.yml
- hosts: "{{ host_group }}"
  connection: local
  gather_facts: False
  vars_files:
    - "{{ cfg_file }}"
    - "{{ mapper_file | default('group_vars/ntp_mapper.yml') }}"
  vars:
     NE_IP: "{{ ne_ip | default (hostvars[inventory_hostname]['ansible_host']) }}"
     NE_User: "{{ ne_user | default(hostvars[inventory_hostname]['ansible_user']) }}"
     NE_Pwd: "{{ ne_pwd | default (hostvars[inventory_hostname]['ansible_password']) }}"

  tasks:
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "rtrv_ntp_config"
      tags: retrieve

    # Please refer/edit group_vars/iqnos_ntp_config.yml - state_configs
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "validate"
      tags: validate

    # Please refer/edit group_vars/iqnos_ntp_config.yml - state_configs
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "unlock_ntp"
      tags: unlock

    # Please refer/edit group_vars/iqnos_ntp_config.yml - server_configs
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "edit_ntp_config"
      tags: edit

    # Please refer/edit group_vars/iqnos_ntp_config.yml - state_configs
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "lock_ntp"
      tags: lock

    # # Please refer/edit group_vars/iqnos_ntp_config.yml - state_configs
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "set_to_maintenance"
      tags: set_to_maintenance

    # # Please refer/edit group_vars/iqnos_ntp_config.yml - state_configs
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "remove_from_maintenance"
      tags: remove_from_maintenance

    # # Please refer/edit group_vars/iqnos_ntp_config.yml - alarm_configs
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "enable_alarm_reporting"
      tags: enable_alarm_reporting

    # # Please refer/edit group_vars/iqnos_ntp_config.yml - alarm_configs
    - import_role:
        name: iqnos_ntp
      vars:
        task_name: "disable_alarm_reporting"
      tags: disable_alarm_reporting
```

## Commands to run the NTP Playbook

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook ntp_playbook.yml -e "cfg_file=ntp_cfgs.yml host_group=ntp" -i myhosts.yml

## Commands to run the Playbook with tags for each of the NTP tasks

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory --tags=tag1,tag2,tag3...`
* *Example*
  * ansible-playbook ntp_playbook.yml -e "cfg_file=ntp_cfgs.yml host_group=ntp" -i myhosts.yml --tags=edit
  * ansible-playbook ntp_playbook.yml -e "cfg_file=ntp_cfgs.yml host_group=ntp" -i myhosts.yml --tags=retrieve,lock

> Providing a `host_group` along with the `cfg_file`(where applicable) is mandatory.
>
> If no inventory file is passed, then default inventory is `hosts`

## License

BSD License 2.0

## Author Information

Infinera Corporation

Technical Support - techsupport@infinera.com
