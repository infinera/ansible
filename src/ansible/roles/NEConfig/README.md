# Ansible Role for NE Configuration 

The Ansible Role for NE Configuration (Network Element Configuration) is used to retrieve the network element system information, enable/disable gRPC, HTTPS, and to configure, retrieve or delete the X.509 certificates.

## Supported Tasks

| Tasks | Description| Tags | Input|
|----|------------|----|----|
|retrieve_system_information|Retrieve the system attributes associated with the network element |retrieve_system_information|NA|
|retrieve_grpc_settings|Retrieve the gRPC settings from the network element|retrieve_grpc_settings|NA|
|retrieve_security_settings|Retrieve the HTTPS, and TLSCERT settings from the network element|retrieve_security_settings|NA|
|enable_grpc|Enable gRPC on the network element|enable_grpc|NA|
|disable_grpc|Disable gRPC on the network element|disable_grpc|NA|
|enable_https|Enable HTTPS on the network element |enable_https|NA|
|disable_https|Disable HTTPS on the network element |disable_https|NA|
|set_tls_certificate|Set the TLS certificate to a certificate confgiured on the network element of the node Controller chassis|set_tls_certificate|certificate_configs.tls_certificate|
|configure_certificate|Configure X.509 certificates on the network element of the node Controller Chassis |configure_certificate|certificate_configs.configure|
|delete_certificate|Delete the X.509 certificates configured on the network element of the node controller chassis |delete_certificate|certificate_configs.delete|
|retrieve_certificate|Retrieve the X.509 certificates configured on the network element |retrieve_certificate|NA|
|certificate_configs_validation|Validate the X.509 certificates |validate|NA|
|||||

> Every task that expects user's input from configuration file validates it's respective role's configuration file completely, so that user is informed of any discrepancy in other tasks' inputs as well
>
> For E.g. - `delete_certificate` task's validation will fail even if `delete_certificate` task inputs are correct as some other task in the configuration file has invalid input

## Input for Tasks

### FTP/SFTP Server

Variables for the `CERT_SERVER` FTP/SFTP Server

| Name | Type | Description|Valid Instances/Ranges|Mandatory|
| ----|------|------------|------------|----------|
|ipaddress | IPv4/IPv6 address|The IP Address of the FTP/SFTP server| Valid IPv4/IPv6 address|Yes|
|username| string| Username to log into the FTP server|Valid Username|Yes|
|password | string| Password required for logging into the FTP/SFTP server| Valid Password|Yes|
| protocol| string| Protocol for the file transfer | sftp,ftp | Yes|
|||||

> The certificates will be downloaded from the above server onto the network element for configuring them
>
> **The certificates can be downloaded ONLY via an SFTP server**

#### Sample configuration file for FTP

Please see config file at `group_vars/ftp_server.yml`

```yaml
# You can add as many FTP server groups here and use it across the playbooks
# Note :
#    This file is not validated before running , please edit carefully 
ftp_server:
  CERT_SERVER:
    ipaddress : 10.220.73.152
    username  : ftpcertuser
    password  : ftpcertuser123
    protocol  : sftp
```

-----

### Configure Certificate

Variables for the `configure_certificate` task

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|--------|
|certificate_identifier | string|The unique identifier assigned by the certificate authority| A string that is at-most 128 characters long|Yes|No|
|node_to_certificate_identifier_mapping| object| The Node TID to the certificate identifier mapping|Valid Mapping(See below)|No|No|
|certificate_type| string| The type of certificate|LOCAL|Yes|Yes|
|ftp_server | string| The Server from which the certificate is going to be downloaded to be configured| See the section `FTP Server` above|Yes|No|
|path_to_file| string| The complete path, including the file name and extension, to the certificate present on the Server | Valid path to the file as described(See below) | Yes|No|
|||||||

> The `certificate_identifier` variable is mandatory
>
> If the `node_to_certificate_identifier_mapping` is given then it will be used
>
> The `path_to_file` does not require a forward slash (`/`) to be given along with it in the beginning - Will be added internally

#### Sample configuration file

Please see config file at `group_vars/neconfig_certificate_config.yml`

```yaml
---

certificate_configs:
  configure:
    - certificate_identifier          : tls
      certificate_type                : LOCAL
      label                           : CERT123
      pass_phrase                     : Infinera
      server                          : "{{ ftp_server.CERT_SERVER }}"
      path_to_file                    : exports/images/naveen/CERT_20thMar/server_certificate.p12
      node_to_certificate_identifier_mapping:
        "XTC284": "tls1"
        "XTC286": "tls2"

    - certificate_identifier          : tlscert
      certificate_type                : LOCAL
      label                           : CERT123
      pass_phrase                     : Infinera
      server                          : "{{ ftp_server.CERT_SERVER }}"
      path_to_file                    : exports/images/DY/server_certificate.p12
      node_to_certificate_identifier_mapping:
        "XTC284": "tlscert1"
        "XTC286": "tlscert2"
```

-----

### Delete certificate

> The following are the variables for the `delete_certificate` task

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|--------|
|certificate_identifier | string|The unique identifier assigned by the certificate authority| A string that is at-most 128 characters long|Yes|No|
|node_to_certificate_identifier_mapping| object| The Node TID to the certificate identifier mapping|Valid Mapping(See below)|No|No|
|certificate_type| string| The type of certificate |LOCALCERT|Yes|Yes|
|||||||

> The `certificate_identifier` variable is mandatory
>
> If the `node_to_certificate_identifier_mapping` is given the it will be used

#### Sample configuration file to delete the certificate

Please see config file at `group_vars/neconfig_certificate_config.yml`

```yaml
---

certificate_configs:
  delete:
    - certificate_identifier          : tls1
      certificate_type                : LOCAL
      node_to_certificate_identifier_mapping:
        "XTC284": "tls1"
        "XTC286": "tls2"

    - certificate_identifier          : TLS
      certificate_type                : LOCAL
      node_to_certificate_identifier_mapping:
        "XTC284": "tls1"
        "XTC286": "tls2"

```

-----

### Set TLS Certificate

> The following are the variables for the `set_tls_certificate` task

| Variable | Type | Description|Valid Instances/Ranges|Mandatory|Validated|
| ----|------|------------|------------|----------|--------|
|certificate_identifier | string|The unique identifier assigned by the certificate authority| A string that is at-most 128 characters long|Yes|No|
|node_to_certificate_identifier_mapping| object| The Node TID to the certificate identifier mapping|Valid Mapping(See below)|No|No|
|idle_time|integer|The time in seconds up to which TLS session can be inactive|1 to 600. If no value is provided then a value of 180 is configured|No|Yes|
|connection_time|integer|The time in seconds until which the TLS session can be active|0 to 172800. If no value is provided then a value of 86400 is configured. If 0 is given, the session never times out |No|Yes|
|||||||

> The `certificate_identifier` variable is mandatory
>
> If the `node_to_certificate_identifier_mapping` is given the it will be used

#### Sample configuration file to Set TLS Certificate

```yaml
---

certificate_configs:
  tls_certificate:
    idle_time: 100
    connection_time: 2400
    certificate_identifier            : tls
    node_to_certificate_identifier_mapping:
      "XTC284": "tls1"
      "XTC286": "tls2"
```

-----

## Sample configuration file

### Note
  Every task that expects user input from configuration file validates it's respective role's configuration file completely, and provides discrepancy in other tasks inputs if any. For Example, "delete_certificate" task's validation will fail even if delete_certificate task inputs are correct but some other task in the configuration file has invalid input.

```yaml
---

####################################################################
#       Configurations for the tasks in the NEConfig role          #
#       Refer the README for more details on the variables         #
#                                                                  #
# Sub Sections in the configuration:                               #
# - delete - Required for the delete_certificate task.             #
# - configure - Requried for the configure_certificate task.       #
# - tls_certificate - Requried for the set_tls_certificate task.   #
####################################################################
certificate_configs:
##############################################################################################################################################
  # The list of certificates that are to be deleted.
  # The certificate_identifier is a mandatory variable.
  # In case the node_to_certificate_identifier_mapping variable is given then it 
  # wil be used for obtaining the certificate_identifier for each of the Node(TID).
  delete:
    - certificate_identifier          : tls1 # The unique serial number issued by the Certificate Authority.
      certificate_type                : LOCAL # The type of the certificate.
      # Node(TID) to certificate_identifier mapping
      node_to_certificate_identifier_mapping:
        "XTC284": "tls1"
        "XTC286": "tls2"

    - certificate_identifier          : TLS # The unique serial number issued by the Certificate Authority.
      certificate_type                : LOCAL # The type of the certificate.
      # Node(TID) to certificate_identifier mapping
      node_to_certificate_identifier_mapping:
        "XTC284": "tls1"
        "XTC286": "tls2"

##############################################################################################################################################
  # The list of certificates that are to be configured.
  # In case the node_to_certificate_identifier_mapping variable is given then it 
  # wil be used for obtaining the certificate_identifier for each of the Node(TID).
  configure:
    - certificate_identifier          : tls # The unique serial number issued by the Certificate Authority.
      certificate_type                : LOCAL # The type of the certificate.
      label                           : CERT123 # The label for the certificate.
      pass_phrase                     : Infinera # The passphrase value for the certificate(Applicable for LOCAL ones).
      server                          : "{{ ftp_server.CERT_SERVER }}" # This is the server from which the certificate is going to be downloaded. Refer group_vars/ftp_server.yml.
      # A forward slash(/) is added to the front of the path internally.
      # That is, the path in the example is treated as /exports/images/naveen/CERT_20thMar/server_certificate.p12 when configuring a certificate
      path_to_file                    : exports/images/naveen/CERT_20thMar/server_certificate.p12 # The path to the certificate file including the FILE NAME AND FILE EXTENSION.
      # Node(TID) to certificate_identifier mapping
      node_to_certificate_identifier_mapping:
        "XTC284": "tls1"
        "XTC286": "tls2"

    - certificate_identifier          : tlscert # The unique serial number issued by the Certificate Authority.
      certificate_type                : LOCAL # The type of the certificate.
      label                           : CERT123 # The label for the certificate.
      pass_phrase                     : Infinera # The passphrase value for the certificate(Applicable for LOCAL ones).
      server                          : "{{ ftp_server.CERT_SERVER }}" # This is the server from which the certificate is going to be downloaded. Refer group_vars/ftp_server.yml.
      # A forward slash(/) is added to the front of the path internally.
      # That is, the path in the example is treated as /exports/images/naveen/CERT_20thMar/server_certificate.p12 when configuring a certificate
      path_to_file                    : exports/images/DY/server_certificate.p12 # The path to the certificate file including the FILE NAME AND FILE EXTENSION.
      # Node(TID) to certificate_identifier mapping
      node_to_certificate_identifier_mapping:
        "XTC284": "tlscert1"
        "XTC286": "tlscert2"

##############################################################################################################################################
  # The below configuration variables are required to set the TLS certificate to an existing one that is already configured on the NE.
  # In case the node_to_certificate_identifier_mapping variable is given then it 
  # wil be used for obtaining the certificate_identifier for each of the Node(TID).
  tls_certificate:
    # The time in seconds upto which TLS session can be inactive.
    # The values range from 1 to 600
    # If no value is provided then a value of 180 is configured.
    idle_time: 240
    # The time in seconds until which the TLS session can be active.
    # If 0 is given, the session never times out.
    # Values range from 0 to 172800
    # If no value is provided then a value of 86400 is configured.
    connection_time: 2500
    certificate_identifier            : tls # Name of the TLS certificate, required for enabling HTTPS setting on the NE.
    # Node(TID) to certificate_identifier mapping
    node_to_certificate_identifier_mapping:
      "XTC284": "tls1"
      "XTC286": "tls2"
```

## Sample Playbook for NE configuration

```yaml
---

# Requires ansible 1.8+
# This playbook is intended to help in performing the tasks related to System Information, gRPC Settings, HTTPS Settings, and X.509 Certificates. Please refer roles/NEConfig/README.md
# For input configurations please refer Or edit group_vars/neconfig_certificate_config.yml

# While creating a new playbook, please copy the sections between ### Start Copy ### and ### End Copy ### as they are mandatory

### Start Copy ###
- hosts: "{{ host_group }}"
  connection: local
  gather_facts: False
  vars_files: 
    - "{{ cfg_file | default('group_vars/neconfig_certificate_config.yml') }}" # The configuration file that contains the input configuration
    - "{{ mapper_file | default('group_vars/neconfig_mapper.yml') }}" # DON'T CHANGE - Mapper file to map the parameters retrieved from the network element
    - "{{ ftp_file | default('group_vars/ftp_server.yml') }}" # File that contains the server details from which certificates are downloaded
  vars:
     NE_IP: "{{ ne_ip | default (hostvars[inventory_hostname]['ansible_host']) }}"
     NE_User: "{{ ne_user | default(hostvars[inventory_hostname]['ansible_user']) }}"
     NE_Pwd: "{{ ne_pwd | default (hostvars[inventory_hostname]['ansible_password']) }}"
     TID: "{{ tid | default(hostvars[inventory_hostname]['tid'] | default('')) }}"

### End Copy ###


  tasks:
    # To validate certificate configs
    - import_role:
        name: NEConfig
      vars:
        task_name: certificate_configs_validation
      tags: validate

    # To retrieve the attributes of system information from the network element
    - import_role:
        name: NEConfig
      vars:
        task_name: retrieve_system_information
      tags: retrieve_system_information

    # To Enable gRPC on the network element
    - import_role:
        name: NEConfig
      vars:
        task_name: enable_grpc
      tags: enable_grpc

    # To Disable gRPC on the network element
    - import_role:
        name: NEConfig
      vars:
        task_name: disable_grpc
      tags: disable_grpc

    # To Enable HTTPS on the network element
    # Requires a TLS certificate to be set
    - import_role:
        name: NEConfig
      vars:
        task_name: enable_https
      tags: enable_https

    # To Disable HTTPS on the network element
    - import_role:
        name: NEConfig
      vars:
        task_name: disable_https
      tags: disable_https

    # To set a configured certificate as the TLS certificate
    # Required for enabling HTTPS
    # For input configurations please refer/edit group_vars/neconfig_certificate_config.yml
    - import_role:
        name: NEConfig
      vars:
        task_name: set_tls_certificate
      tags: set_tls_certificate

    # Configure X.509 certificates with the specified configuration on shelves of network elements
    # For input configurations please refer/edit group_vars/neconfig_certificate_config.yml
    - import_role:
        name: NEConfig
      vars:
        task_name: configure_certificate
      tags: configure_certificate

    # Delete X.509 certificates that have been configured on the network element
    # For input configurations please refer/edit group_vars/neconfig_certificate_config.yml
    - import_role:
        name: NEConfig
      vars:
        task_name: delete_certificate
      tags: delete_certificate

    # Retrieve X.509 certificates that have been configured on the network element
    - import_role:
        name: NEConfig
      vars:
        task_name: retrieve_certificate
      tags: retrieve_certificate

```

## Commands to run the Playbook for NE Configuration tasks

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/cfg_file.yml host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook neconfig_playbook.yml -e "cfg_file=neconfig_cfgs.yml host_group=neconfig" -i myhosts.yml

## Commands to run the Playbook with tags for NEConfig tasks

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "cfg_file=path_to_the/ftp_cfg_file.yml host_group=the_host_group" -i file_with_the_inventory --tags=tag1,tag2,tag3...`
* *Example*
  * ansible-playbook neconfig_playbook.yml -e "cfg_file=neconfig_cfgs.yml host_group=neconfig" -i myhosts.yml --tags=retrieve_system_information
  * ansible-playbook neconfig_playbook.yml -e "cfg_file=neconfig_cfgs.yml host_group=neconfig" -i myhosts.yml --tags=retrieve_system_information,enable_grpc

> Providing a `host_group` along with the `cfg_file`(where applicable) is mandatory
>
> If no inventory file is passed, then default inventory is `hosts`

## License

BSD License 2.0

## Author Information

Infinera Corporation.

Technical Support - techsupport@infinera.com
