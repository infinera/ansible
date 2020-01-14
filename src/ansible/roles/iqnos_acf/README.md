# Ansible Role for Access Control Filters (ACFs)

 The Ansible role for Access Control Filters is used to create, delete, clear, and retrieve access filters for network elements.

## Listed below are the necessary pre-requisites and conditions for the Ansible role ACF

 * Host file lists all the network elements and its details. See example file "hosts.yml".
 * Host Group specifies the group of hosts to be used. See example "db_group" in "hosts.yml"     file.
 * Input configuration file lists the inputs required to run the tasks within ACF. 
   See example file "group_vars/config.yml".
 * Updated configuration filename or name of the config.file contains inputs required to run    tasks. See example file "group_vars/acf_config.yml".

## User tasks and capabilities
* Create new ACFs with any specification.
* Delete existing ACFs on the network element.
* Retrieve existing ACFs from the network element.
* Clear the counters in ACFs. 

## Supported tasks

| Tasks | Description| Tags | Input|
|----|------------|----|----|
|acf_configs_validation|Validates the ACF configurations provided against a JSON schema (See example below for input configurations) |validate|[acf_configs](#Sample-Configuration-File)|
|create|Creates ACFs with the given specification (See example below for input configurations) |create|[acf_configs.create](#Create-Configuration-Variables)|
|delete|Deletes the ACFs existing on the network element. The task fails if there are no ACFs configured (See below for input configurations) |delete|[acf_configs.delete](#Delete-Configuration-Variables)|
|retrieve|Retrieves ACFs from the network element. If there are no ACFs, a message is displayed indicating the same. |retrieve|NA|
|clear|Clears the counters of ACFs.  |clear|NA|
|||||

## Configuration variables to create ACF tasks


Every ACF is created with a set of variables, details of which are listed below. 

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|------------|
|name| string| The name of Access Control Filter| Unique name with a maximum of 128 characters|Yes|Yes|
|sequence| integer| A number that assigns priority to the rule | 200 to 4294967100 (in multiples of 100). The filter with sequence number 200 will be checked first|Yes|Yes|
|interface| string| The interfaces to which the rule is applied|<ul><li>dcn</li><li>aux</li><li>igcc</li><li>gcc</li><li>all</li></ul> |Yes|Yes|
|protocol| string| The protocol to which the rule is applied|<ul><li>tcp</li><li>udp</li><li>icmp</li><li>all</li></ul> |Yes|Yes|
|direction| string| The direction of the packets to which the rule is applied|<ul><li>input</li><li>output</li></ul> |Yes|Yes|
|operation| string| The operation (action) applied on the packets|<ul><li>accept</li><li>drop</li><li>reject</li><li>log</li></ul> |Yes|Yes|
|label| string| A descriptive label for the filter| A string with maximum of 128 characters |No|Yes|
|source_address| IPv4/IPv6 address| The source IP address filtered by the ACF| Valid IPv4/IPv6 address|No|Yes|
|source_prefix_length| integer| The source IP address mask length |<ul><li>IPv4 - 1 to 32</li><li>IPv6 - 1 to 128</li></ul>  |No|No|
|source_port| integer| The source port number| 1 to 65535 |No|No|
|source_port_range| integer| The range of source ports filtered by the ACF (The range starts from the configured source_port. A value of 0 means no range.) | 1 to 65535 |No|No|
|dest_address| IPv4/IPv6 address| The destination IP address filtered by the ACF| Valid IPv4/IPv6 address|No|Yes|
|dest_prefix_length| integer| The destination IP address mask length| <ul><li>IPv4 - 1 to 32</li><li>IPv6 - 1 to 128</li></ul>  |No|No|
|dest_port| integer| The destination port number| 1 to 65535 |No|No|
|dest_port_range| integer| The range of destination ports filtered by the ACF (The range starts from the configured dest_port. A value of 0 means no range.) | 1 to 65535 |No|No|
||||||

***Note***
> * The `source_address` and `dest_address` must be in the same format - IPv4 or IPv6.
>
> * A `source_address` is required for `source_prefix_length`, and a `dest_address` is           required for `dest_prefix_length`.
>
>* `source_prefix_length` and `dest_prefix_length` is not allowed if `protocol` is specified     as `icmp` in the input configuration file.
>
> * `port` is not allowed if specific `protocol` is not specified.
>
> * The `port_range` is not allowed if `protocol` is specified as `all` in the input              configuration file.
-----

-----
>
> To create Access Control Filters with source or destination IP same as the network element IP,
> create different host groups for each node and run the playbook for each host group with the exact configuration file name. 

-----
## Configuration variables to delete the ACF tasks


> The list of Access Control Filter variables to be removed or deleted is listed below

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|------------|
|Names of the Access Control Filters| list| The name of access control filter to be deleted| A valid name that is to be deleted|Yes|No|
|||||||

## Sample configuration file to perform ACF tasks

```yaml
---

##############################################################################################################################################################################
#Using Access control Filters feature -
#Secure the interfaces on the NE and run restrict inbound IP access to a Infinera NE, protecting it from access by hosts that don't have permission
#Specify which hosts or groups of hosts can access and manage a Infinera NE by IP address, simplifying operations.
#Gather statistics on the allowed application ports and IP addresses
##############################################################################################################################################################################
#######################################Config variables ######################################################################################################################
# name - Indicates the name of the ACF. Specify a unique name for the ACF. Maximum characters supported is 30
# label - Label for the ACF rule
# protocol - Indicates the protocol applied to the ACF. 
#            Set the value to one of the following: tcp|udp|icmp|all
# operation - Indicates the action taken by the ACF. 
#             Set the value to one of the following:ACCEPT,DROP,REJECT,LOG
# interface - Indicates the interface applied to the ACF.
#             Set the value to one of the following: dcn|aux|igcc|osc|all
# sequence - Indicates the priority of the ACF rule. Sequence is specified in multiples of 100 starting from 200. 200 indicates highest priority. ACF rules on a node need to have unique sequence number.
# direction - Based on this value, the ACF will be applied to incoming, outgoing or forwarded packets. 
#             Set the value to one of the following:INPUT,OUTPUT
# source_address - Indicates the Source IP that this ACF will filter. IPv4 and IPv6 addresses are supported. IPv6 check-box needs to be checked to specify an IPv6 address
# source_prefix_length - Indicates the SIP Prefix length.
# source_port - Indicates the Source Port
# source_port_range - This parameter specifies the range starting with the Source port. A value of 0 indicates no range.
# dest_address - Indicates the Destination IP that this ACF will filter. IPv4 and IPv6 addresses are supported. IPv6 check-box needs to be checked to specify an IPv6 address.
# dest_prefix_length - Indicates the DIP Prefix length.
# dest_port - Indicates the Destination Port
# dest_port_range - This parameter specifies the range starting with the Destination port. A value of 0 indicates no range.

acf_configs:
  create:
    - name                 : Log aux
      label                : Logging aux incoming traffic
      protocol             : tcp
      operation            : log
      interface            : aux
      sequence             : 3800
      direction            : input

    # - name                 : Reject gcc
    #   label                : Rejecting the gcc incoming traffic
    #   protocol             : tcp
    #   operation            : reject
    #   interface            : igcc
    #   sequence             : 300
    #   direction            : input

    # - name                 : Accept igcc
    #   label                : Accepting igcc incoming traffic
    #   protocol             : udp
    #   operation            : accept
    #   interface            : igcc
    #   sequence             : 400
    #   direction            : input
  
  
  # Names of the ACF objects provided while creating Access Control Filters
  delete:
    - Log aux
```

## Sample Access Control Filter Playbook

```yaml
# For input configurations please refer/edit group_vars/acf_config.yml
- hosts: "{{ host_group }}"
  connection: local
  gather_facts: False
  vars_files:
    - "{{ cfg_file }}"
    - "{{ mapper_file | default('group_vars/acf_mapper.yml') }}"
  vars:
     NE_IP: "{{ ne_ip|default (hostvars[inventory_hostname]['ansible_host']) }}"
     NE_User: "{{ne_user|default(hostvars[inventory_hostname]['ansible_user']) }}"
     NE_Pwd: "{{ ne_pwd|default (hostvars[inventory_hostname]['ansible_password']) }}"

  tasks:

    - import_role:
        name: iqnos_acf
      vars:
        task_name: retrieve
      tags: retrieve

    # Please refer/edit group_vars/acf_config.yml - create
    - import_role:
        name: iqnos_acf
      vars:
        task_name: create
      tags: create

    # Please refer/edit group_vars/acf_config.yml - delete
    - import_role:
        name: iqnos_acf
      vars:
        task_name: delete
      tags: delete

    - import_role:
        name: iqnos_acf
      vars:
        task_name: clear
      tags: clear

    - import_role:
        name: iqnos_acf
      vars:
        task_name: acf_configs_validation
      tags: validate
```

## Commands to run the Access Control Filter Playbook

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook acf_playbook.yml -e "cfg_file=acf_cfgs.yml host_group=acf" -i myhosts.yml

## Commands to run the Playbook with tags for each of the ACF tasks

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory --tags=tag1,tag2,tag3...`
* *Example*
  * ansible-playbook acf_playbook.yml -e "cfg_file=acf_cfgs.yml host_group=acf" -i myhosts.yml --tags=create
  * ansible-playbook acf_playbook.yml -e "cfg_file=acf_cfgs.yml host_group=acf" -i myhosts.yml --tags=clear,retrieve

Note:
* Providing a `host_group` along with the `cfg_file`(where applicable) is mandatory
* If no inventory file is passed, the default inventory is `hosts`

## License

BSD License 2.0

## Author Information

Infinera Corporation

Technical Support - techsupport@infinera.com
