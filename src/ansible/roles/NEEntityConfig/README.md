# Ansible Role for Network Element Entity Configuration

The Ansible role for Network Element Entity Configuration is used to set the service type for TRIB default template, and editing the operation modes for TIMs.

With this role, service type for TRIB port can be set to 10GBE_LAN

## Supported Tasks


| Tasks | Description| Tags | Input|
|----|------------|----|----|
|edit_default_template_tribptp_service_type|Edit service type for TRIB default template to 10GBE_LAN - Applicable only for `10G Tribs` |edit_default_template_tribptp_service_type|[default_template_configs.trib.service_type](#Default-Template-TRIB-Configurations)|
|retrieve_default_template_tribptp|Retrieve the TRIB default template settings |retrieve_default_template_tribptp|NA|
|edit_eqpt_operation_mode|Edit the operation mode for TIM - Applicable only for `TIM-1-100GX` |edit_eqpt_operation_mode|eqpt_operation_mode_configs|
|edit_facility_autotti_settings|Edit the AUTOTTI Settings attribute for the facilities|edit_facility_autotti_settings|facility_autotti_settings_configs|
|enable_lc|Enable LC for neighbor discovery. This task sets the Facility Monitoring Mode to Intrusive for the ODU4, OTU4 facilities|enable_lc|enable_lc_configs|
|validate|Validate the input configuration file |validate|contents of `neentityconfig_config.yml`|
|||||


### TRIB Configuration variables for NEEntity tasks 

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|---------|
|service_type| string| Default setting for the provisioned service type of tributary ports| 10GBE_LAN|Yes|Yes|
||||||

> The value for the `service_type` is expected to be `10GBE_LAN` and not any other value

#### Sample default template TRIB configuration

Please refer `default_template_configs` in the file `group_vars/neentityconfig_config.yml`

```yaml
---

default_template_configs:
  trib:
    service_type: 10GBE_LAN
```

-----

### Equipment operation mode configurations

1. After changing the operation mode of the TIM equipment the task retrieves the TIM(s) and checks if the Operation Mode Status is Active.
2. The retrieval and check is repeated for 50 times with a delay of 60 seconds in between each repetition
3. If the status is not Active then the task fails.
4. If it is Active then it moves the equipment to unlocked state

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|---------|
|eqpt| string| The equipment for which the operation mode is to be edited| TIM|Yes|Yes|
|mode| string| The mode to which the operation mode must be set to| <ul><li>ODUk</li><li>ODUk-ODUj</li><li>GBE100-ODU4-4i-2ix10V</li><li>ODU4-ODL</li></ul>|Yes|Yes|
|node_to_aid_mapping| object(See Below)| The mapping between Node TID to the the list of AIDs| Valid Mapping(See Below)|Yes|No|
||||||

Note:
> * The `eqpt` variable is required to be `TIM`.
> * The `mode` value is expected to be the above values (case sensitive) and not others.
>
> The value for the `AID` in the `node_to_aid_mapping` in the configuration block is assumed to be an `AID` that corresponds to a `TIM` of type `TIM-1-100GX`
>
> The value for the `AID` needs to be in uppercase - `1-A-1-1` and not `1-a-1-1`

#### Sample Equipment operation mode configuration

Please refer `eqpt_operation_mode_configs` in the file - `group_vars/neentityconfig_config.yml` 

```yaml
eqpt_operation_mode_configs:
  eqpt: TIM # DON'T MODIFY
  mode: ODUk
  node_to_aid_mapping:
    "XTC286":
      - 1-A-5-3
      - 1-A-5-1
```

> Note : If a network element is included in the host group, it is mandatory to provide a mapping corresponding to it in the `node_to_aid_mapping` section.

-----

### Configurations for Facility AUTOTTI Settings 

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|---------|
|facility| string| The facility for which AUTOTTI is to be enabled or disabled | <ul><li>ODU4</li><li>OTU4</li><li>ODU2e</li></ul>|Yes|Yes|
|autotti| string| The mode to which the operation mode must be set to| <ul><li>Enable</li><li>Disable</li></ul> |Yes|Yes|
|node_to_aid_mapping| object(See Below)| The mapping between Node TID to the the list of trib AIDs(See below)| Valid Mapping(See Below)|Yes|No|
||||||

> The value for `facility` is case sensitive
>
> The value for the `AID` in the `node_to_aid_mapping` in the configuration block is assumed to be an `AID` that corresponds to a `trib` in `TIM-1-100GX` (or) `TIM-5-10GX`
>
> The value for the `AID` needs to be in uppercase - `1-A-1-T1-1` and not `1-a-1-t1-1`

#### Sample Facility AUTOTTI Settings Configuration

Please refer `facility_autotti_settings_configs` in the file - `group_vars/neentityconfig_config.yml`

```yaml
facility_autotti_settings_configs:
    facility: ODU4 # And OTU4, ODU2e are supported
    autotti: ENABLE # Or DISABLE
    node_to_aid_mapping:
      "XTC286":
        - 1-A-1-T1-1
        - 1-A-5-T1-1
```

>Note: If a network element is included in the host group, it is mandatory to provide a mapping corresponding to it in the `node_to_aid_mapping` section.

-----

### Enable LC Configurations

* Order of execution of tasks for the `enable_lc` task
  1. Retrieve TIM, OTU4, ODU4
  2. Perform Idempotency Check
     1. Check if OTU4 Service Mode is not `Adaptation` and Facility Monitoring Mode is not `Im`
     2. Check if ODU4 Service Mode is not `Adaptation` and Facility Monitoring Mode is not `Im`
        * If both the conditions for are satisfied for ODU4 and OTU4 and the TIM Operation Mode is not ODUk - Mark as `xcon_required` for the particular AID
        * If both the conditions for are satisfied for ODU4 only and the TIM Operation Mode is not ODUk - Mark as `xcon_required` for the particular AID
        * Mark as `xcon_not_required` in other cases
  3. Retrieve XCON
  4. Create XCON
  5. Delete XCON
  6. Retrieve OTU4, ODU4
  7. Show Service Mode and Facility Monitoring Mode for each AID

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|---------|
|node_to_aid_mapping| object(See Below)| The mapping between Node TID to the the list of AIDs| Valid Mapping(See Below)|Yes|No|
|||||||

> The value for the `AID` needs to be in uppercase - `1-A-1-1` and not `1-a-1-1`

#### Example

Please refer `enable_lc_configs` in the file `group_vars/neentityconfig_config.yml`

```yaml
---

enable_lc_configs:
    node_to_aid_mapping:
      "XTC284":
        - 1-A-1-1
```

>Note: If a network element is included in the host group, it is mandatory to provide a mapping corresponding to it in the `node_to_aid_mapping` section.

-----

## Sample Configuration File

### Note
  Every task that expects user input from configuration file validates it's respective role's configuration file completely, and provides discrepancy in other tasks inputs if any. For Example, "enable_lc" task's validation will fail even if enable_lc task inputs are correct but some other task in the configuration file has invalid input.

```yaml
---

########################################################################################
#     Configurations for the tasks in the NEEntityConfig role                          #
#       Refer the README for more details on the variables                             #
#                                                                                      #
# Sections in the configuration:                                                       #
# - default_template_configs - Required for the                                        #
#                              edit_default_template_tribptp_service_type task         #
# - eqpt_operation_mode_configs - Required for the                                     #
#                                  edit_eqpt_operation_mode task                       #
# - facility_autotti_configs: - Required for the                                       #
#                                 edit_facility_autotti_settings task                  #
########################################################################################

##############################################################################################################################################
default_template_configs:
  # Default TRIB template settings
  trib:
    service_type: 10GBE_LAN # The service type to be set. Only 10GBE_LAN(as it is) is supported.

##############################################################################################################################################
eqpt_operation_mode_configs:
  eqpt: TIM # DON'T MODIFY
  # Mode to set the operational state to for the TIMs. Supported values are ODUk, ODUk-ODUj, GBE100-ODU4-4i-2ix10V, ODU4-ODL.
  # The values are case sensitive, i.e., ODUk is accepted and not oduk.
  mode: ODUk
  # This is the mapping required for setting the operational state of the AIDs of each Node(TID) to the given mode.
  # Here the TID of the Node is mapped to the list of AIDs on the Node.
  # If an NE is included in the host group then it is mandatory to provide a mapping corresponding to it in the node_to_aid_mapping section.
  # The value for the AID needs to be in uppercase - 1-A-1-1 and not 1-a-1-1
  node_to_aid_mapping:
    "XTC286":
      - 1-A-5-3
      - 1-A-5-1

##############################################################################################################################################
facility_autotti_settings_configs:
    facility: ODU4 # And OTU4, ODU2e are supported. These are case sensitive. ODU4 and not odu4, OTU4 and not otu4, ODU2e and not odu2e.
    autotti: ENABLED # Or DISABLED
    # This is the mapping required for enabling (or) disabling AUTOTTI of the trib AIDs of each Node(TID).
    # Here the TID of the Node is mapped to the list of trib AIDs on the Node.
    # If an NE is included in the host group then it is mandatory to provide a mapping corresponding to it in the node_to_aid_mapping section.
    # The value for the AID needs to be in uppercase - 1-A-1-T1-1 and not 1-a-1-t1-1
    node_to_aid_mapping:
      "XTC286":
        - 1-A-1-T1-1
        - 1-A-5-T1-1
############################################################################
enable_lc_configs: 
    # This is the mapping required for enabling LC of the AIDs of each Node(TID).
    # Here the TID of the Node is mapped to the list of AIDs on the Node.
    # If an NE is included in the host group then it is mandatory to provide a mapping corresponding to it in the node_to_aid_mapping section.
    # The value for the AID needs to be in uppercase - 1-A-1-1 and not 1-a-1-1
    node_to_aid_mapping:
      "XTC284":
        - 1-A-1-1
```

## Sample Playbook

```yaml
---

# Requires ansible 1.8+
# This playbook is intended to help in performing the tasks related to setting the service type for default TRIB template. Please refer roles/NEEntityConfig/README.md
# For input configurations please refer/edit group_vars/neentityconfig_config.yml

# While creating a new playbook, please copy the sections between ### Start Copy ### and ### End Copy ### as they are mandatory

### Start Copy ###
- hosts: "{{ host_group }}"
  connection: local
  gather_facts: False
  vars_files:
    - "{{ cfg_file | default('group_vars/neentityconfig_config.yml') }}"
    - "{{ mapper_file | default('group_vars/neentityconfig_mapper.yml') }}"
  vars:
     NE_IP: "{{ ne_ip|default (hostvars[inventory_hostname]['ansible_host']) }}"
     NE_User: "{{ne_user|default(hostvars[inventory_hostname]['ansible_user']) }}"
     NE_Pwd: "{{ ne_pwd|default (hostvars[inventory_hostname]['ansible_password']) }}"
     TID: "{{ tid | default(hostvars[inventory_hostname]['tid'] | default('')) }}"

### End Copy ###


  tasks:

    # To validate the configs
    - import_role:
        name: NEEntityConfig
      vars:
        task_name: validate
      tags: validate

    # To set the service type for the default TRIB template
    # Please refer group_vars/neentityconfig_config.yml
    - import_role:
        name: NEEntityConfig
      vars:
        task_name: edit_default_template_tribptp_service_type
      tags: edit_default_template_tribptp_service_type

    # To retrieve the default TRIB template settings
    - import_role:
        name: NEEntityConfig
      vars:
        task_name: retrieve_default_template_tribptp
      tags: retrieve_default_template_tribptp

    # To edit the operation mode for TIM
    # Firstly, the tasks moves the TIM equpiment to OOS(out of service) state and the changes the operation mode
    # Then the task moves it back to IS(in service) mode
    # Please refer group_vars/neentityconfig_config.yml
    - import_role:
        name: NEEntityConfig
      vars:
        task_name: edit_eqpt_operation_mode
      tags: edit_eqpt_operation_mode

    # To change the AUTOTTI settings for the ODU4, OTU4, ODU2e facilities. Either Enable (or) Disable AUTOTTI.
    # Please refer group_vars/neentityconfig_config.yml
    - import_role:
        name: NEEntityConfig
      vars:
        task_name: edit_facility_autotti_settings
      tags: edit_facility_autotti_settings

    # Enable LC for neighbor discovery. This task sets the Facility Monitoring Mode to Intrusive for the ODU4, OTU4 facilities
    # Please refer group_vars/neentityconfig_config.yml
    - import_role:
        name: NEEntityConfig
      vars:
        task_name: enable_lc
      tags: enable_lc

```

## Sample to run the playbook for NE entity configuration tasks

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook neentityconfig_playbook.yml -e "cfg_file=neentityconfig_cfgs.yml host_group=neentityconfig" -i myhosts.yml

## Sample to run the playbook with tags for NE entity configuration tasks 

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory --tags=tag1,tag2,tag3...`
* *Example*
  * ansible-playbook neentityconfig_playbook.yml -e "cfg_file=neentityconfig_cfgs.yml host_group=neentityconfig" -i myhosts.yml --tags=edit_default_template_tribptp_service_type,edit_facility_autotti_settings

> Providing a `host_group` along with the `cfg_file`(where applicable) is mandatory
>
> If no inventory file is passed, then default inventory is `hosts`

## License

BSD License 2.0

## Author Information

Infinera Corporation

Technical Support - techsupport@infinera.com
