# Ansible Role for Configuration of  Network Element Call Home feature 

Ansible Role for Configuration of Network Element Call Home feature is used to configure the NE Call Home Settings.

## User tasks and capabilities

* Retrieve the Call Home Settings configured on the network element
* Configure up to three or more Call Home Settings
   * Edit Call Home Settings of existing settings present on the network element
   * Create new Call Home Settings if not available on the network element
* Invoke (trigger) Call Home on demand

Note: Upto three Call Home Settings are supported by the network element.

| Tasks | Description| Tags | Input|
|----|------------|----|----|
|configure |Create new (or) Edit existing Call Home Settings on the network element |configure|ne_call_home_configs.configure|
|delete |Delete Call Home Settings on the network element |delete|ne_call_home_configs.delete|
|retrieve |Retrieve Call Home Settings from the network element |retrieve|NA|
|invoke |Invoke Call Home on demand |invoke|ne_call_home_configs.invoke|
|validate |Validate the configurations against a JSON schema |validate|ne_call_home_configs|
|||||

> > Every task that expects user's input from configuration file validates it's respective role's configuration file completely, so that user is informed of any discrepancy in other tasks' inputs as well
>
> For E.g. - `delete_callhome` task's validation will fail even if `delete_callhome` task inputs are correct as some other task in the configuration file has invalid input

## Configuration Variables to Configure Call Home Settings

The list of Call Home Settings to be created if unavailable, or to be used to edit existing configurations are listed below.

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|identifier| string| The unique identifier for the Call Home Setting | at most 64 characters long|Yes|
|dest_address| IPv4/IPv6 Address| The location where the Network Element is required to dial-out to initiate the NETCONF Call Home Session| Valid IPv4/IPv6 address|No (See below)|
|dest_port| integer| The TCP/IP port to which the Network Element will initiate and establish the NETCONF Call Home Session | 1 to 65535 |No|
|protocol| string| The protocol that is to be used for the NETCONF Call Home communication | <ul><li>SSH</li><li>TLS</li></ul>(See Below)|No|
|retry_count| integer| The number of times the Network Elements attempts connecting to this NETCONF Call Home destination before aborting |1 to 5|No|
|timeout| integer| Connection timeout (expressed in seconds) | 1 to 255 |No|
|||||

> The value of the `protocol` is case sensitive
>
> In case of creating a new Call Home Setting, the `dest_address` variable is mandatory
>
> The number of Call Home Settings in the `configure` section can be greater than `3` but the number of Call Home Settings supported by the NE are `3` (The count is not validated)
>
> It is recommended that only `3` instances of Call Home Settings under `configure` are provided

#### Sample configuration file

```yaml
ne_call_home_configs:
  configure:
    - identifier: CallHomeIdentifier1
      dest_address: 10.220.15.39
      timeout: 25
      retry_count: 4

    - identifier: CallHomeIdentifier2
      dest_address: 10.220.5.39
      dest_port: 9090
      retry_count: 4
      timeout: 12
      protocol: SSH

    - identifier: CallHomeIdentifier3
      dest_address: 10.220.165.87
      dest_port: 5432
      retry_count: 2
      timeout: 15
      protocol: SSH
```

-----

## Delete Call Home Settings

The names of the Call Home Settings which are going to be deleted are listed below

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|------------|
|Call Home Settings' Identifiers| list| The list of identifiers representing Call Home Settings that are to be deleted| A valid Identifier that is to be deleted|Yes|No|
|||||||

Note: The number of Call Home Settings' Identifiers in the `delete` section can be greater than `3` but the number of Call Home Settings supported by the NE are `3` (The count is not validated)

#### Sample configuration file

```yaml
ne_call_home_configs:
  delete:
    - CallHomeIdentifier1
    - CallHomeIdentifier2
    - CallHomeIdentifier3
```

-----

## Invoke Call Home Settings

The names of the Call Home Settings which are going to be used for invoking on demand Call Home Session are listed below

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|------------|
|Call Home Settings' Identifiers| list| The list of identifiers representing Call Home Settings that are going to be used for invoking on demand call home| A valid Identifier |Yes|No|
|||||||

> The number of Call Home Settings' Identifiers in the `invoke` section can be greater than `3` but the number of Call Home Settings supported by the NE are `3` (The count is not validated)

#### Sample configuration file

```yaml
ne_call_home_configs:
  invoke:
    - CallHomeIdentifier1
    - CallHomeIdentifier2
    - CallHomeIdentifier3
```

-----

## Sample Configuration File

### Note
  Every task that expects user input from configuration file validates it's respective role's configuration file completely, and provides discrepancy in other tasks inputs if any. For Example, "delete" task's validation will fail even if delete task inputs are correct but some other task in the configuration file has invalid input.

```yaml
---

###################################################################
#     Configurations for the tasks in the ne_call_home role       #
#       Refer the README for more details on the variables        #
#                                                                 #
# Sub Sections in the configuration:                              #
# - configure - Required for the configure task                   #
# - delete - Required for the delete task                         #
# - invoke - Required for the invoke task                         #
###################################################################
ne_call_home_configs:
##############################################################################################################################################
  # The list of configurations that are to be edited or created.
  # In case they are present on the Network Element then the existing ones will be edited.
  # In case they are not present on the Network Element then new ones with the input will be created.
  # The value of protocol is case sensitive - SSH/TLS and not ssh/tls.
  configure:
    - identifier: CallHomeIdentifier1
      dest_address: 10.220.15.39
      timeout: 25
      retry_count: 4

    - identifier: CallHomeIdentifier2
      dest_address: 10.220.5.39
      dest_port: 9090
      retry_count: 4
      timeout: 12
      protocol: SSH # Case sensitive - SSH/TLS and not ssh/tls

    - identifier: CallHomeIdentifier3
      dest_address: 10.220.165.87
      dest_port: 5432
      retry_count: 2
      timeout: 15
      protocol: SSH # Case sensitive - SSH/TLS and not ssh/tls
##############################################################################################################################################
  # The list of identifiers, each of which corresponds to a Call Home Setting on the Network Element, that are going to be deleted.
  delete:
    - CallHomeIdentifier1
    - CallHomeIdentifier2
    - CallHomeIdentifier3

##############################################################################################################################################
  # The list of identifiers, each of which corresponds to a Call Home Setting on the Network Element, 
  # that are going to be used for invoking an on demand Call Home Session.
  invoke:
    - CallHomeIdentifier1
    - CallHomeIdentifier2
    - CallHomeIdentifier3

```

## Sample Playbook

```yaml
---

# Requires ansible 1.8+
# This playbook is intended to help in performing the tasks related to NE Call Home Settings Configurations. Please refer roles/ne_call_home/README.md
# For input configurations please refer/edit group_vars/ne_call_home_config.yml
# While creating a new playbook, please copy the sections between ### Start Copy ### and ### End Copy ### as they are mandatory

### Start Copy ### 

- hosts: "{{ host_group }}"
  connection: local
  gather_facts: False
  vars_files:
    - "{{ cfg_file | default('group_vars/ne_call_home_config.yml') }}"
    - "{{ mapper_file | default('group_vars/ne_call_home_mapper.yml') }}"
  vars:
     NE_IP: "{{ ne_ip|default (hostvars[inventory_hostname]['ansible_host']) }}"
     NE_User: "{{ne_user|default(hostvars[inventory_hostname]['ansible_user']) }}"
     NE_Pwd: "{{ ne_pwd|default (hostvars[inventory_hostname]['ansible_password']) }}"
     TID: "{{ tid | default(hostvars[inventory_hostname]['tid'] | default('')) }}"

### End Copy ###

  tasks:

    # To Retrieve the Call Home Settings from the Network Element.
    # In case there are no Call Home settings then there will be a message indicating it.
    - import_role:
        name: ne_call_home
      vars:
        task_name: retrieve
      tags: retrieve

    # To Create Call Home Settings with the given input if not present on the Network Element.
    # To Edit existing Call Home Settings with the given input on the Network Element.
    # Please refer/edit group_vars/ne_call_home_config.yml - configure
    - import_role:
        name: ne_call_home
      vars:
        task_name: configure
      tags: configure

    # To Delete the existing Call Home Settings on the Network Element.
    # Task fails in case input contains identifiers to settings that don't exist.
    # Please refer/edit group_vars/ne_call_home_config.yml - delete
    - import_role:
        name: ne_call_home
      vars:
        task_name: delete
      tags: delete

    # To invoke On demand Call Home.
    # Please refer/edit group_vars/ne_call_home_config.yml - invoke
    - import_role:
        name: ne_call_home
      vars:
        task_name: invoke
      tags: invoke

    # To Validate the input against a JSON schema
    # Please refer/edit group_vars/ne_call_home_config.yml
    - import_role:
        name: ne_call_home
      vars:
        task_name: validate
      tags: validate

```

## Commands to run the Playbook

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook ne_call_home_playbook.yml -e "cfg_file=ne_call_home_config.yml host_group=ne_call_home" -i myhosts.yml

## Commands to run the Playbook with Tags

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory --tags=tag1,tag2,tag3...`
* *Example*
  * ansible-playbook ne_call_home_playbook.yml -e "cfg_file=ne_call_home_config.yml host_group=ne_call_home" -i myhosts.yml --tags=configure
  * ansible-playbook ne_call_home_playbook.yml -e "cfg_file=ne_call_home_config.yml host_group=ne_call_home" -i myhosts.yml --tags=retrieve,delete

> Providing a `host_group` along with the `cfg_file`(where applicable) is mandatory
>
> If no inventory file is passed, then default inventory is `hosts`

## License

BSD License 2.0

## Author Information

Infinera Corporation.

Technical Support - techsupport@infinera.com
