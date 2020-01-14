#!/usr/bin/env python

#---- Import Ansible Utilities (Ansible Framework) ---------------------------#
from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: infn_cfg_validator
author: "Anand Krishna Rallabhandi (anand-krishna)"
short_description: Validate the user defined configurations
description:
  - The configurations given are to be validated against a JSON Schema defined for them
options:
  what_is_being_validated:
    description:
      - A string describing what is being validated
    required: true
    type: string

  configs:
    description:
      - Input configurations for any role
    required: true
    type: dict
  schema:
    description:
      - JSON Schema for the input configuration of that role
    required: true
    type: string
"""

EXAMPLES = """
---
- hosts: swne
  connection: local
  gather_facts: False
  vars_files:
    - group_vars/iqnos_radius_config.yml
  vars:
     NE_IP: "{{ ne_ip | default(hostvars[inventory_hostname]['ansible_host']) }}"
     NE_User: "{{ ne_user | default(hostvars[inventory_hostname]['ansible_user']) }}"
     NE_Pwd: "{{ ne_pwd | default(hostvars[inventory_hostname]['ansible_password']) }}"
  tasks:
    - name: Check if the input configuration is valid or not
      infn_cfg_validator:
        what_is_being_validated: "NTP Server Configs"
        configs: "{{ configs }}"
        schema: "{{ lookup('file', 'ntp_config_schema.json') | from_json | string }}"
"""
#--------- Infinera Specific Implementation for Configuration Validation -------------------------------#
from ansible.module_utils.cfg_validator import validate


def main():
    spec = dict(
        what_is_being_validated=dict(type='str'),
        configs=dict(type='dict'),
        schema=dict(type='str')
    )
    module = AnsibleModule(argument_spec=spec)

    validated,error,result = validate(module.params["what_is_being_validated"], module.params["configs"], module.params["schema"])

    if validated:
        module.exit_json(
            result=result,
            validated=validated,
            status='SUCCESS'
        )
    else:
        module.fail_json(
            msg=error,
            validated=validated,
            status='FAILURE'
        )


if __name__ == '__main__':
    main()
