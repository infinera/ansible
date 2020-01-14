# Ansible Role for Security 

This role can be used for performing tasks such as SSH Key Regeneration, retrieval of SSH fingerprint & public key on the Network Element.

## Pre-requisites and conditions for the Security role

* The Host file lists all the  network elements and their details. See example file "hosts.yml".
* The Host group specifies the group of host to be used. See example "db_group" in "hosts.yml" file.


## User tasks and capabilities

1. User can regenerate SSH Keys
2. User can retrieve the existing SSH fingerprint & public key

| Tasks | Description| Tags | Input|
|----|------------|----|----|
|ssh_key_regen|Regenerate SSH Keys|regen|NA|
|retrieve_ssh_keys|Retrieve the existing SSH fingerprint & public key|retrieve|NA|
|||||

Note: ssh_key_regen terminates all the existing SSH sessions, including SFTP sessions and transfers.

## Sample Playbook for Security tasks

```yaml
---

- hosts: "{{ host_group }}"
  connection: local
  gather_facts: False
  vars_files:
    - "{{ mapper_file | default('group_vars/ssh_mapper.yml') }}"
  vars:
    NE_IP: "{{ ne_ip | default(hostvars[inventory_hostname]['ansible_host']) }}"
    NE_User: "{{ ne_user | default(hostvars[inventory_hostname]['ansible_user']) }}"
    NE_Pwd: "{{ ne_pwd | default(hostvars[inventory_hostname]['ansible_password']) }}"
    TID: "{{ hostvars[inventory_hostname]['tid'] | default('') }}"

  tasks:
    - import_role:
        name: security
      vars:
        task_name: retrieve_ssh_keys
      tags: retrieve

    - import_role:
        name: security
      vars:
        task_name: ssh_key_regen
      tags: regen
```

## Commands to run the Security playbook 

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "host_group=the_host_group" -i file_with_the_inventory`
* *Example*
  * ansible-playbook ssh_key_regen.yml -e "host_group=ssh" -i myhosts.yml

## Commands to run the Security playbook with tags for each of the Security tasks

* *Command*
  * `ansible-playbook name_of_playbook.yml -e "host_group=the_host_group" -i file_with_the_inventory --tags=tag1,tag2,tag3...`
* *Example*
  * ansible-playbook ssh_key_regn_playbook.yml -e "host_group=ssh" -i myhosts.yml --tags=regen
  * ansible-playbook ssh_key_regn_playbook.yml -e "host_group=ssh" -i myhosts.yml --tags=retrieve,regen

> Providing a `host_group` is mandatory
>
> If no inventory file is passed, then default inventory is `hosts`

## License

BSD License 2.0

## Author Information

Infinera Corporation

Technical Support - techsupport@infinera.com
