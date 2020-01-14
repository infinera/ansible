# Ansible Role for Database Image(s) Management

The Ansible Role for Database Image(s) Management is used to clean up the database backup files on the network element, to back up the current database image, to schedule backups, and to restore a database image.

## Supported tasks
| Task Name | Description | Tags |Input |
| ----|------|------------|------------|
| retrieve_database_images| Retrieve the existing DB image information from network element| retrieve| N/A |
| cleanup| Cleanup the existing backup DB image from network element| cleanup| <image_name> |
| cleanup_all| Cleanup all the existing backup DB images from network element| cleanup_all| N/A |
| backup_local| Initiate a local DB backup in the network element| backup_local| N/A |
| backup| Initiate a DB backup to an FTP server | backup| FTP server ip/path , run id/ db name  |
| restore_local| Initiate a restore from local DB backup| restore_local | <image_name> |
| restore| Initiate a restore from an FTP server DB backup| restore| FTP server ip/path , run id/ db name |
| schedule_backup| Schedule a DB backup to an FTP server | schedule_backup| <schedule_time> |
| unschedule_backup| Unschedule a DB backup| unschedule_backup | N/A |
| retrieve_backup_schedule| Retrieve DB backup schedule information | retrieve_schedule | N/A |
| download| Download DB from FTP server to network element (used by restore task) | download | Uses restore input section for FTP information |

## Sample output for a retrieve_backup_schedule with no schedule information 

> When the backup is unscheduled there will be no details and the output will be as shown  

```
ok: [ne_1] => {
    "RETRIEVE BKUPSCHED": {
        "InputParameters": {},
        "result": {},
        "status": "SUCCESS"
    },
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "status": "SUCCESS"
}
```

> schedule_backup  creates backup for given schedule with a file name DB_<YYYYMMDDhhmmss>_TID in FTP server present in the backup section of db_mgmt_config.yml.  
Currently the support is for only one FTP server.

## *Inputs for tasks*

### FTP server
----

> The following are the variables for the `SERVER_1` and `SERVER_2` FTP Server

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|ipaddress | IPv4/IPv6 address|The IP Address of the FTP/SFTP server| Valid IPv4/IPv6 address|Yes|
|username| string| Username to log into the FTP server|Valid Username|Yes|
|password | string| Password required for logging into the FTP/SFTP server| Valid Password|Yes|
| protocol| string| Protocol for the file transfer | sftp,ftp | Yes|
|||||

#### Sample configuration file for FTP server 

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

### cleanup
----
> The following are the variables for the `cleanup` 

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|run_id| string| Unique ID for each run , used to determine file name (DB_<run_id>_TID) | Uniqe ID for each run|Yes|
|file_mapping | object |Key is TID ,value is DB file name| Valid TID and DB file name |Yes|
|||||

If TID is not provided then `run_id` value will be taken as DB file name ,TID means NE name.

if `run_id` is "1234" then file name will be DB_1234_TID" . TID means NE name

#### Sample configuration file for cleanup
Please see config file at `group_vars/db_mgmt_config.yml`

```
  ##############################################################################################################################################  
  cleanup:
    run_id: "UNIQUE_RUN_ID" # File DB_UNIQUE_RUN_ID_NODENAME will be deleted from NE
    #file_mapping is used you want to use different DB names for different NEs 
    file_mapping:
      "NE1": "DB_1823012220190829061801" # For NE1 , "DB_1823012220190829061801" file will be considered for cleanup
      "NE2": "DB_1823012220190829061802" # For NE1 , "DB_1823012220190829061802" file will be considered for cleanup

##############################################################################################################################################  

```
### backup
----
> The following are the variables for the `backup` 

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|primary_ftp_server | Object |FTP Server(refer FTP server section) |Valid FTP Server |Yes|
|primary_path| string| path on FTP server|Valid Path |Yes|
|secondary_ftp_server| string| FTP Server(refer FTP server section) |Valid FTP Server|Yes if simultaneous is true|
|secondary_path| string| path on FTP server|Valid Path|Yes if simultaneous is true|
|simultaneous| string| if true it will transfer database simultaneously  | true/false |Yes|
|overwrite| string| Overwrite database file name on FTP server|true/false |Yes|
|run_id| string| Id , used to determine file name (DB_run_id_TID) | Unique ID for each run|Yes|
|file_mapping | object |Key is TID ,value is database file name| Valid TID and database file name |Yes when you dont want to use run_id file name (DB_run_id_TID)|
|||||

If TID is not provided then `run_id` value will be used to form DB file name

#### Sample configuration file for backup
Please see config file at `group_vars/db_mgmt_config.yml`

```
  ##############################################################################################################################################  
  backup:
    primary_ftp_server: "{{ ftp_server.SERVER_1 }}"
    primary_path: "dbbkups"
    secondary_ftp_server: "{{ ftp_server.SERVER_2 }}"
    secondary_path: "secondary_dbbkups"
    simultaneous: false
    overwrite: false
    run_id: "UNIQUE_RUN_ID" # File will be saved as DB_UNIQUE_RUN_ID_NODENAME
    #file_mapping is used you want to use different database names for different NEs 
    file_mapping: 
      "NE1": "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" # For NE1 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" file will be considered for backup
      "NE2": "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" # For NE2 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" file will be considered for backup

##############################################################################################################################################  
 
```

### restore_local
----
> The following are the variables for the `restore_local` 

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|run_id| string| Unique ID for each run , used to determine file name (DB_<run_id>_TID) | Unique ID for each run|Yes|
|file_mapping | object |Key is TID ,value is database file name| Valid TID and Database file name |Yes|
|||||

If TID is not provided then `run_id` value will be taken as database file name

#### Sample configuration file for restore_local
Please see config file at `group_vars/db_mgmt_config.yml`

```
  ##############################################################################################################################################  
  restore_local:
    run_id: "UNIQUE_RUN_ID" 
    #file_mapping is used you want to use different database names for different NEs 
    file_mapping:
      "NE1": "DB_1823012220190829061801" # For NE1 , "DB_1823012220190829061801" file will be considered for restore_local
      "NE2": "DB_1823012220190829061802" # For NE1 , "DB_1823012220190829061802" file will be considered for restore_local

##############################################################################################################################################  

```
### restore
----
> The following are the variables for the `restore` 

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|primary_ftp_server | Object |FTP Server(refer FTP server section) |Valid FTP Server |Yes|
|primary_path| string| path on FTP server|Valid Path |Yes|
|run_id| string| Id , used to determine file name (DB_run_id_TID) | Uniqe ID for each run|Yes|
|file_mapping | object |Key is TID ,value is DB file name| Valid TID and database file name |Yes when you dont want to use run_id file name (DB_run_id_TID)|
|||||

> If TID is not provided then `run_id` value will be used to form database file name
>
> Secondary ftp server is not supported for `restore`

#### Sample configuration file for restore
Please see config file at `group_vars/db_mgmt_config.yml`

```
 ##############################################################################################################################################  
  restore:
    primary_ftp_server: "{{ ftp_server.SERVER_1 }}"
    primary_path: "dbbkups"
    run_id: "UNIQUE_RUN_ID"  #Run ID used for backup,  DB_UNIQUE_RUN_ID_NODENAME File will be downloaded
    #file_mapping is used you want to use different database names for different NEs 
    file_mapping: 
      "NE1": "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" # For NE1 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" file will be considered for restore
      "NE2": "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" # For NE2 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" file will be considered for restore

##############################################################################################################################################  

 
```

### schedule 
----
> The following are the variables for the `schedule`

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|interval | string| The frequency at which the backup should be done| <ul><li>daily</li><li>weekly</li></ul>|Yes|
|day| string| Day of the week when the backup is to done|<ul><li>sunday</li><li>monday</li><li>tuesday</li><li>wednesday</li><li>thursday</li><li>friday</li><li>saturday</li></ul>|Required for weekly backup|
|time | string| The time in 24-hr clock| HH:MM format(see below)|Yes|
|||||

> In case the value for variable `interval` is provided as `daily` then the variable `day` needs to be commented out - Add a `#` before it

#### Sample configuration file for schedule
Please see config file at `group_vars/db_mgmt_config.yml`

```yaml
schedule:
    interval: "weekly"
    day: "monday"
    time: "01:00"
```

> The HH:MM time string should be enclosed in quotes and the MM values are 0,15,30,45
>
> If the schedule interval is daily then day is not required(Command will not be executed)
>
> Schedule task will use FTP server details from `backup` section from config file , to configure FTP server.Currently only primary_server is supported.
>
>*Few of the variables aren't required for some cases; it is left to the user to ensure the presence of the required variables for the requried tasks*
>
> NOTE: It is left to the user to give the appropriate input:
>
>   1. No `day` to be specified when `interval` is defined to be `daily`
>
>   2. The `day` to be specified when the `interval` is `weekly`
>
> The validation merely validates the values against the schema and not any interdependencies(day-interval)
>
> If the user provides `day` when the `interval` is defined to be `daily`, or does not provide a `day` when the `interval` is defined to be `weekly` then the schedule task is executed and the corresponding TL1 error is shown to the user

### Wait Times, Delays, Retries

> The tasks provide a set of configurable delays, retries. The following table summarizes them
>
> If they are not provided as a part of input then the defaults are used

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Default Value|
|---|---|---|---|---|---|
|check_backup_retries|integer| Number of times to retry the backup check after the `backup` operation has been initiated|Any valid integer >= 1|No|5|
|check_backup_delay|integer|Delay in `seconds` between each retry of `check_backup_retries` |Any valid integer >= 1|No|60|
|restore_pause|integer|Time to wait in `minutes` after the restore operation has been initiated. Common for `restore`, and `restore_local` tasks|Any valid integer >= 1|No|5|
|||||||

## Sample Configuration File for Wait Times, Delays, Retries
### Note
  Every task that expects user input from configuration file validates it's respective role's configuration file completely, and provides discrepancy in other tasks inputs if any. For Example, "backup" task's validation will fail even if backup task inputs are correct but some other task in the configuration file has invalid input.

```yaml
---

db_configs:
  # Number of times to retry the backup check after the backup operation has been initiated
  check_backup_retries: 5

  # Delay in seconds between each retry
  check_backup_delay: 60

  # Delay in minutes after the restore operation has been initiated
  # Common for restore, and restore_local tasks
  restore_pause: 10

##############################################################################################################################################  
  cleanup:
    run_id: "UNIQUE_RUN_ID" # File DB_UNIQUE_RUN_ID_NODENAME will be deleted from NE
    #file_mapping is used when you want to use different database names for different NEs 
    file_mapping:
      "XTC284": "DB_1823011820191003084953" # For NE1 , "DB_1823012220190829061801" file will be considered for cleanup
      "NE2": "DB_1823012220190829061802" # For NE1 , "DB_1823012220190829061802" file will be considered for cleanup

##############################################################################################################################################  
  backup:
    # ftp server details , please refer ftp_server.yml
    primary_ftp_server: "{{ ftp_server.SERVER_1 }}"
    primary_path: "dbbkups"
    # ftp server details , please refer ftp_server.yml
    secondary_ftp_server: "{{ ftp_server.SERVER_2 }}"
    secondary_path: "secondary_dbbkups"
    simultaneous: false
    overwrite: false
    run_id: "UNIQUE_RUN_ID" # File will be saved as DB_UNIQUE_RUN_ID_NODENAME
    #file_mapping is used when you want to use different database names for different NEs 
    file_mapping: 
      "XTC284": "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" # For NE1 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" file will be considered for backup
      "NE2": "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" # For NE2 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" file will be considered for backup

##############################################################################################################################################  
  restore_local:
    run_id: "UNIQUE_RUN_ID" 
    #file_mapping is used when you want to use different database names for different NEs 
    file_mapping:
      "XTC284": "DB_1823012220190829061801" # For NE1 , "DB_1823012220190829061801" file will be considered for restore_local
      "NE2": "DB_1823012220190829061802" # For NE1 , "DB_1823012220190829061802" file will be considered for restore_local

##############################################################################################################################################  
  restore:
    # ftp server details , please refer ftp_server.yml
    # please note that , same input section will be used by download task ,download task will not apply restore command after download
    primary_ftp_server: "{{ ftp_server.SERVER_1 }}"
    primary_path: "dbbkups"
    run_id: "UNIQUE_RUN_ID"  #Run ID used for backup,  DB_UNIQUE_RUN_ID_NODENAME File will be downloaded
    #file_mapping is used when you want to use different database names for different NEs 
    file_mapping: 
      "NE1": "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" # For NE1 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE1" file will be considered for restore
      "NE2": "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" # For NE2 , "DB_UNIQUE_RUN_ID_CUSTOM_FILE2" file will be considered for restore

##############################################################################################################################################  
# schedule db backup
  schedule:
    # NOTE: It is left to the user to give the appropriate input:
    #    1. No `day` to be specified when `interval` is defined to be `daily`
    #    2. The `day` to be specified when the `interval` is `weekly`
    # The validation merely validates the values against the schema and not any interdependencies(day-interval).
    # If the user provides `day` when the `interval` is defined to be `daily`, or does not provide a `day` when the `interval` is 
    # defined to be `weekly` then the schedule task is executed and the corresponding TL1 error is shown to the user.
    interval: "weekly" # Supported values are 'daily' and 'weekly'. Not case sensitive.
    day: "monday" # Supported values are 'monday', 'tuesday', 'wednesday', 'thursday', 'friday, 'saturday', and 'sunday'. Not case sensitive.
    time: "01:00" # The values for time should be of the form HH:MM in the 24-hour clock format.
##############################################################################################################################################
```

## Sample Playbook

```yaml

# Requires ansible 1.8+
# This playbook is intended to help in performing the tasks related to Database Mgmt.. Please refer roles/db_mgmt/README.md
# For input configurations please refer Or edit group_vars/db_mgmt_config.yml

# While creating a new playbook, please copy the sections between ### Start Copy ### and ### End Copy ### as they are mandatory

### Start Copy ### 
- hosts: "{{ host_group }}"
  serial: "{{ batch_size | default(3) }}"
  connection: local
  gather_facts: False
  
  vars_files: 
    - "{{ cfg_file | default('group_vars/db_mgmt_config.yml') }}"
    - "{{ mapper_file | default('group_vars/db_mgmt_mapper.yml') }}"
    - "{{ ftp_file | default('group_vars/ftp_server.yml') }}"

  vars:
    NE_IP: "{{ ne_ip | default(hostvars[inventory_hostname]['ansible_host']) }}"
    NE_User: "{{ne_user | default(hostvars[inventory_hostname]['ansible_user']) }}"
    NE_Pwd: "{{ ne_pwd | default(hostvars[inventory_hostname]['ansible_password']) }}"
    TID: "{{ hostvars[inventory_hostname]['tid']| default('') }}"

### End Copy ###

  tasks:

    # To Retrieve Database Images
    - import_role:
        name: db_mgmt
      vars:
        task_name: retrieve_database_images
      tags: retrieve
    
    # To Cleanup database image
    # Please refer/edit group_vars/db_mgmt_config.yml - cleanup section 
    - import_role:
        name: db_mgmt
      vars:
        task_name: cleanup
      tags: cleanup

    # To Cleanup all existing database images
    - import_role:
        name: db_mgmt
      vars:
        task_name: cleanup_all
      tags: cleanup_all

    # To Backup the database image locally in NE 
    - import_role:
        name: db_mgmt
      vars:
        task_name: backup_local
      tags: backup_local

    # To Backup the database image on an FTP/SFTP server
    # Please refer/edit group_vars/db_mgmt_config.yml - backup section 
    - import_role:
        name: db_mgmt
      vars:
        task_name: backup
      tags: backup

    # To Restore the database image from an FTP/SFTP server
    # Please refer/edit group_vars/db_mgmt_config.yml - restore section 
    - import_role:
        name: db_mgmt
      vars:
        task_name: restore
      tags: restore

    # To Restore local database image 
    # Please refer/edit group_vars/db_mgmt_config.yml - restore_local section 
    - import_role:
        name: db_mgmt
      vars:
        task_name: restore_local
      tags: restore_local

    # To Schedule Backup of database on an FTP server
    # Please refer/edit group_vars/db_mgmt_config.yml - schedule section 
    - import_role:
        name: db_mgmt
      vars:
        task_name: "schedule_backup"        
      tags: schedule_backup
    
    # To UnSchedule Backup of database on an FTP server
    - import_role:
        name: db_mgmt
      vars:
        task_name: "unschedule_backup"        
      tags: unschedule_backup

    # To Retrieve Schedule Information of Backup of database
    - import_role:
        name: db_mgmt
      vars:
        task_name: "retrieve_backup_schedule"        
      tags: retrieve_schedule
    
    # To Download database image to NE from an FTP server
    # Please refer/edit group_vars/db_mgmt_config.yml - restore section 
    - import_role:
        name: db_mgmt
      vars:
        task_name: "download"        
      tags: download  
    
    
```

## Commands to run the playbook

*Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`

*Example*
  * ansible-playbook db_mgmt_playbook.yml -e "cfg_file=group_vars/db_mgmt_config.yml host_group=db_group" -i hosts.yml

> Providing a `host_group`, `ftp_server`and a `cfg_file` is mandatory
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