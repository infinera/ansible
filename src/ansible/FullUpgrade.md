# Full Upgrade for Ansible

This document provides an overview of the operations involved in a full upgrade process for Ansible along with the necessary code.

## Listed below are the operations involved during a full upgrade process

* Database Cleanup - Removes the image(s) apart from the current database image in use.
* Software Cleanup - Removes the image(s) apart from the current software image in use.
* Software Download - Downloads the software image from the FTP server to the network element.
* Database Backup - Creates a back-up of the existing database image and upload to an FTP       server.
* Prepare - Assists with pre-upgrade checks to verify the success of the upgrade; this          operation is initiated before the upgrade.
* Upgrade - Performs actual upgrade of the software image on the network element.




## Sample configuration file for full upgrade

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

  # To download SW image from FTP server to network element
  download :
    # ftp server details , please refer ftp_server.yml 
    ftp_server: "{{ ftp_server.SERVER_2 }}"
    path: "/home/pub/R18.2.10.0202/tar_ne/SIM/XTC2"
    sw_image_version: R18.2.10.0202
    # Arch type is sim/ppc/x86 and file with name R18.2.10.0118.<sim/ppc/x86>.tar.gz should be present in FTP Server
    arch: sim
    # Time to wait to check network element availability after download operation 
    wait_time: 15
  
db_configs:
  # Number of times to retry the backup check after the backup operation has been initiated
  check_backup_retries: 5

  # Delay in seconds between each retry
  check_backup_delay: 60

  # Delay in minutes after the restore operation has been initiated
  # Common for restore, and restore_local tasks
  restore_pause: 10
##############################################################################################################################################  
  backup:
    # ftp server details , please refer ftp_server.yml
    primary_ftp_server: "{{ ftp_server.SERVER_1 }}"
    primary_path: "dbbkups"
    # ftp server details , please refer ftp_server.yml
    secondary_ftp_server: "{{ ftp_server.SERVER_2 }}"
    secondary_path: "secondary_dbbkups"
    simultaneous: false
    overwrite: true
    run_id: "UNIQUE_RUN_ID" # File will be saved as DB_UNIQUE_RUN_ID_NODENAME
    #file_mapping is used when you want to use different DB names for different NEs 
    file_mapping: 
      "XTC284": "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" # For NE1 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" file will be considered for backup
      "NE2": "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" # For NE2 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" file will be considered for backup

```

## Sample Playbook for full upgrade

```yaml

# Requires ansible 1.8+
# This playbook is intended to help in performing full SW upgrade. Please refer roles/db_mgmt/README.md and  roles/sw_mgmt/README.md
# While creating a new playbook, please copy the sections between ### Start Copy ### and ### End Copy ### as they are mandatory

### Start Copy ### 
- hosts: "{{ host_group }}"
  serial: "{{ batch_size | default(3) }}"
  connection: local
  gather_facts: False
  vars_files:
    - "{{ cfg_file | default('group_vars/sw_upgrade_config.yml') }}"
    - "{{ ftp_file | default('group_vars/ftp_server.yml') }}"

  vars:
    NE_IP: "{{ ne_ip | default(hostvars[inventory_hostname]['ansible_host']) }}"
    NE_User: "{{ne_user | default(hostvars[inventory_hostname]['ansible_user']) }}"
    NE_Pwd: "{{ ne_pwd | default(hostvars[inventory_hostname]['ansible_password']) }}"
    TID: "{{ hostvars[inventory_hostname]['tid']| default('') }}"

### End Copy ###

  tasks:

    # Cleanup existing software images
    - import_role:
        name: sw_mgmt
      vars:
        task_name: cleanup

    # Cleanup existing database images
    - import_role:
        name: db_mgmt
      vars:
        task_name: cleanup_all

    # Download the new software image
    - import_role:
        name: sw_mgmt
      vars:
        task_name: download

    # Backup the image up on an FTP server
    - import_role:
        name: db_mgmt
      vars:
        task_name: backup

    # Initiate the upgrade preparation operation
    - import_role:
        name: sw_mgmt
      vars:
        task_name: prepare

    # Initiate the upgrade preparation operation
    - import_role:
        name: sw_mgmt
      vars:
        task_name: upgrade
```

## Commands to run the Playbook for full upgrade

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook sw_upgrade_playbook.yml -e "cfg_file=sw_upgrade_config.yml host_group=sw_group" -i hosts.yml

> Providing a `host_group`, and a `cfg_file` is mandatory.
>
> If no inventory file is passed, then default inventory is `hosts`

## Issues
  * This playbook tasks uses 'pause' component of ansible. The 'pause' component has known issue that if pause is skipped for first host, then pause will not be executed for other hosts - This may lead to inconsistency in tasks result. We advice to run this playbook on host group with single node. See [here](https://github.com/ansible/ansible/issues/19966) more info about issue.
  * If user `abort` during `pause` action, may lead to inconsistency in task results. Infinera suggest to ignore these results and run the playbook again for correct results.

## License

BSD License 2.0

## Author Information

Infinera Corporation.

Technical Support - techsupport@infinera.com