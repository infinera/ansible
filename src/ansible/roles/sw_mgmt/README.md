# Ansible Role for Software Image(s) Management

Ansible Role for Software Image(s) Management is used to download software images, to remove software images on the network element, upgrade the software images, prepare the network element for upgrade, and revert the software and database image.


## Supported tasks
| Task Name | Description | Tags |Input |
| ----|------|------------|------------|
| retrieve_sw_info| Retrieve the existing  SW images from NE | retrieve | N/A |
| cleanup|  Cleanup the "backup" software image from NE | cleanup| N/A |
| restart_with_emptydb|  Restart NE with No or default configuration| restart_with_emptydb| N/A |
| download |Download the software to NE | download| FTP Server/Path / SW image name |
| prepare_for_upgrade| Prepare for upgrade|prepare_for_upgrade | N/A |
| cancel_prepare_for_upgrade| Cancel Prepare for upgrade |cancel_prepare_for_upgrade | N/A |
| fresh_install| Fresh install downloaded SW on NE |fresh_install | N/A |
| upgrade| Upgrade NE with downloaded SW| upgrade| N/A |
| revert| Revert NE to older version of SW| revert| DB backup File or backup Run ID  |
| lock_stby| Lock the standby controller card| lock_stby| N/A  |
| unlock_stby| Unlock the standby controller card| unlock_stby| N/A |

> The user needs to lock `stby` card (Standby Controller Card) for `fresh_install`, `revert` and `restart_with_emptydb`
>
> In the `fresh_install`, `restart_with_emptydb` task, after initiating the corresponding fresh install and restart operation there is a check for the availability of the Network Element and followed by a retrieval of software image information.
>
> The purpose of retrieval of software image information is to check whether login to the Network Element is possible through the existing credentials.
>
> Post fresh install and restart with emptydb, logging in through the existing credentials should typically not work.
> Post fresh install and restart with emptydb, Changing the default Password and enabling the default security/privileges has to be taken care outside of Ansible.
>
> It is required to have a backup Software Image present on the Network Element for the tasks - `fresh_install`, `upgrade` and `revert`
>
> There is no idempotency check for the tasks - `fresh_install`, `upgrade` and `revert`
>
> Please refer the document explaining how to set the password, and user privileges - [User Password and Privilege Change](../../UserCredentialsChange.md)

### Configuration variables for the `SERVER_1` and `SERVER_2` FTP Server
----

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|ipaddress | IPv4/IPv6 address|The IP Address of the FTP server| Valid IPv4/IPv6 address|Yes|
|username| string| Username to log into the FTP server|Valid Username|Yes|
|password | string| Password required for logging into the FTP server| Valid Password|Yes|
| protocol| string| Protocol for the file transfer | ftp, sftp| Yes|
|||||

#### Sample configuration

Please see config file at `group_vars/ftp_server.yml`

```
# You can add as many FTP server groups here and use it across the playbooks
# By default SERVER_1 and SERVER_2 are used inside playbooks 
# By default SERVER_1 and SERVER_2 will use SFTP protocol 
# If you want to use only one ftp/sftp server then can remove secondary option 
# Note : 
#   'protocol' should be same for both the server while using configuration for DB/SW operation
#    This file is not validated before running , please edit carefully 
ftp_server:
  SERVER_1:
    ipaddress  : 10.220.5.39
    username   : root
    password   : password
    protocol   : sftp
  SERVER_2:
    ipaddress  : 10.220.104.65
    username   : root
    password   : password
    protocol   : sftp
```
### download
----
Details of the variables for `download` are listed below.

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|ftp_server | Object |FTP Server(refer FTP server section) |Valid FTP Server |Yes|
|path| string| path on FTP server|Valid Path |Yes|
|sw_image_version| string| Software image version | ex: R18.2.10.0101 |Yes|
|wait_time | number  | No. of minutes to wait after download is triggered | Valid int value  |Yes |
|||||


#### Sample configuration file for `download`
Please see config file at `group_vars/sw_mgmt_config.yml`

```
   # To download SW image from FTP server to NE
  download :
    # ftp server details , please refer ftp_server.yml 
    ftp_server: "{{ ftp_server.SERVER_1 }}"
    path: "swbk"
    sw_image_version: R18.2.3.0128
    # Arch type is sim/ppc/x86 and file with name R18.2.10.0118.<sim/ppc/x86>.tar.gz should be present in FTP Server
    arch: sim
    # Time to wait to check NE availability after download operation 
    wait_time: 15
```

>*Few of the variables aren't required for some cases; it is left to the user to ensure the presence of the required variables for the requried tasks*

### Wait Times, Delays, Retries

Details of the variables for `Wait Times, Delays, Retries` are listed below. The tasks provide a set of configurable delays, retries. 
If variables are not provided as part of input, the the default variables are used

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Default Value|
|---|---|---|---|---|---|
|restart_with_emptydb_wait_time|integer|Time in `minutes` to wait to check NE availability after `restart_with_emptydb` operation|Any valid integer >= 1|No|5|
|revert_wait_time|integer|Time to wait in `minutes` to check NE availability after revert operation|Any valid integer >= 1|No|15|
|fresh_install_wait_time|integer|Time to wait in `minutes` to check NE availability after fresh_install operation|Any valid integer >= 1|No|5|
|prepare_wait_time|integer|Time in `minutes` to wait for after the prepare operation has been initiated|Any valid integer >= 1|No|5|
|upgrade_wait_time|integer|Time in `minutes` to wait after the upgrade operation has been initiated|Any valid integer >= 1|No|30|
|||||||

## Sample Configuration for 'Wait Times, Delays, Retries'
### Note
  Every task that expects user input from configuration file validates it's respective role's configuration file completely, and provides discrepancy in other tasks inputs if any. For Example, "download" task's validation will fail even if download task inputs are correct but some other task in the configuration file has invalid input.

```yaml
---

---

sw_configs:
  # Time in minutes to wait to check NE availability after restart_with_emptydb operation 
  restart_with_emptydb_wait_time: 10
  
  # Time in minutes to wait to check NE availability after revert operation 
  revert_wait_time: 10
  
  # Time in minutes to wait to check NE availability after fresh_install operation 
  fresh_install_wait_time: 10

  # Time in minutes to wait for after the prepare operation has been initiated
  prepare_wait_time: 20
  
  # Time in minutes to wait after the upgrade operation has been initiated
  upgrade_wait_time: 30

  # To download SW image from FTP server to NE
  download :
    # ftp server details , please refer ftp_server.yml 
    ftp_server: "{{ ftp_server.SERVER_1 }}"
    path: "swbk"
    sw_image_version: R18.2.3.0128
    # Arch type is sim/ppc/x86 and file with name R18.2.10.0118.<sim/ppc/x86>.tar.gz should be present in FTP Server
    arch: sim
    # Time to wait to check NE availability after download operation 
    wait_time: 15
  
  # Revert / downgrade to older version
  revert:
    # run_id used for taking backup
    run_id: "UNIQUE_RUN_ID" 
    #db_file_mapping is used when you want to use different DB names for different NEs  
    db_file_mapping: 
      "NE1": "DB_UNIQUE_RUN_ID_CUSTOM_FILE" #add here all NE name to DB name mapping if DB name is not in format DB_backup_08_05_15_NODENAME
      "NE2": "DB_UNIQUE_RUN_ID_CUSTOM_FILE" #add here all NE name to DB name mapping if DB name is not in format DB_backup_08_05_15_NODENAME ---

```

# Sample Playbook

```yaml

---

# Requires ansible 1.8+
# This playbook is intended to help in performing the tasks related to Sw Mgmt.. Please refer roles/sw_mgmt/README.md
# For input configurations please refer Or edit group_vars/sw_mgmt_config.yml

# While creating a new playbook, please copy the sections between ### Start Copy ### and ### End Copy ### as they are mandatory

### Start Copy ### 
- hosts: "{{ host_group }}"
  serial: "{{ batch_size | default(3) }}" # 3 Nodes are managed by default at a time
  connection: local
  gather_facts: False
  vars_files: 
    - "{{ cfg_file | default('group_vars/sw_mgmt_config.yml') }}"
    - "{{ mapper_file | default('group_vars/sw_mgmt_mapper.yml') }}"
    - "{{ ftp_file | default('group_vars/ftp_server.yml') }}"

  vars:
    NE_IP: "{{ ne_ip|default (hostvars[inventory_hostname]['ansible_host']) }}"
    NE_User: "{{ne_user|default(hostvars[inventory_hostname]['ansible_user']) }}"
    NE_Pwd: "{{ ne_pwd|default (hostvars[inventory_hostname]['ansible_password']) }}"
    TID: "{{ hostvars[inventory_hostname]['tid']| default('') }}"

### End Copy ###

  tasks:

    # To Retrieve SW images information from NE
    - import_role:
        name: sw_mgmt
      vars:
        task_name: retrieve_sw_info
      tags: retrieve

    # To delete downloded SW image from NE   
    - import_role:
        name: sw_mgmt
      vars:
        task_name: cleanup
      tags: cleanup

    # To lock standby controller card , this task needs to be run before fresh_install,revert,restart_with_emptydb
    - import_role:
        name: sw_mgmt
      vars:
        task_name: lock_stby
      tags: lock_stby
    
    # To unlock standby controller card
    - import_role:
        name: sw_mgmt
      vars:
        task_name: unlock_stby
      tags: unlock_stby

    # To restart NE with emptydb with current SW image 
    - import_role:
        name: sw_mgmt
      vars:
        task_name: restart_with_emptydb
      tags: restart_with_emptydb
    
    # To download SW image from FTP/SFTP server to NE 
    - import_role:
        name: sw_mgmt
      vars:
        task_name: download
      tags: download

    # To start 'prepare_for_upgrade' operation on NE after downloading SW image 
    - import_role:
        name: sw_mgmt
      vars:
        task_name: prepare
      tags: prepare_for_upgrade

    # To cancel 'prepare_for_upgrade' operation on NE  
    - import_role:
        name: sw_mgmt
      vars:
        task_name: cancel_prepare
      tags: cancel_prepare_for_upgrade

    # To fresh install SW image NE after downloading it to NE (Please make sure you have DB backup for current release before running this task )  
    - import_role:
        name: sw_mgmt
      vars:
        task_name: fresh_install
      tags: fresh_install

    # To upgrade to new SW image NE after downloading it to NE (Please make sure you have DB backup for current release before running this task )  
    - import_role:
        name: sw_mgmt
      vars:
        task_name: upgrade
      tags: upgrade

    # To revert to older SW image after upgrading NE (Please make sure you have DB backup for current release before running this task )  
    - import_role:
        name: sw_mgmt
      vars:
        task_name: revert
      tags: revert
```

## Commands to run the Playbook

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook sw_mgmt_playbook.yml -e "cfg_file=sw_mgmt_config.yml host_group=sw_group" -i hosts.yml

> Providing a `host_group`, and a `cfg_file` is mandatory
>
> If no inventory file is passed, then default inventory is `hosts`

## Issues
  * This playbook tasks uses 'pause' component of ansible. The 'pause' component has known issue that if pause is skipped for first host, then pause will not be executed for other hosts - This may lead to inconsistency in tasks result. We advice to run this playbook on host group with single node. See [here](https://github.com/ansible/ansible/issues/19966) more info about issue. 
  * If user `abort` during `pause` action, may lead to inconsistency in task results. Infinera suggest to ignore these results and run the playbook again for correct results.
  
## License

BSD License 2.0

## Author Information

Infinera Corporation

Technical Support - techsupport@infinera.com