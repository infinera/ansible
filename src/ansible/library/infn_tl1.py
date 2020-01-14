# !/usr/bin/env python

#---- Import Ansible Utilities (Ansible Framework) ---------------------------#
import os

from ansible.module_utils import six
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.tl1 import TL1 as telnet_tl1
from ansible.module_utils.sshtl1 import TL1 as ssh_tl1
from ansible.module_utils.tl1_utils import parse_to_readable_str, make_masked_tl1_cmd

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: infn_tl1
author: "Govindhi Venkatachalapathy (gvenkatachal@infinera.com)"
short_description: Manage Infinera Devices thru TL1 Interface
description:
  - This module is intended to work with Infinera devices via TL1 interface.
vars:
 host:
   description:
     - IP address of the chassis (GNE). Generally comes from hosts file
 username:
   description:
     - Username of the chassis. Generally comes from hosts file.
 password:
   description:
     - Password of the chassis. Generally comes from hosts file.
 tid:
   description:
     - SNE Id. If the chassis is SNE, then host has to be GNE ipaddress. Generally comes from hosts file.     
options:
  commands:
    description:
      - List of TL1 commands. 
  scripts:
    description:
      - A txt file(each TL1 command in a separate line).
  save:
    description:
      - Takes a log file name where the output of the TL1 commands has to be stored.
  output:
    description:
      - This option is provided, if the output of the TL1 command is required to be in json.
"""

EXAMPLES = """
---
- hosts: ne
  connection: local
  vars:
    tl1:
      host: "{{ hostvars[inventory_hostname]['ansible_host'] }}"
      username: "{{ hostvars[inventory_hostname]['ansible_username'] }}"
      password: "{{ hostvars[inventory_hostname]['ansible_password'] }}"
      tid: "{{ hostvars[inventory_hostname]['tid'] }}"
  tasks:
    - name: Check Alarms and Equipment
      infn_tl1:
        provider: "{{ tl1 }}"
        commands:
          - RTRV-ALM-ALL:::c
          - RTRV-EQPT:::c
        save: "logs_tl1/log_{{ hostvars[inventory_hostname]['ansible_host'] }}.txt"
    - name: Check Alarms and Equipment
      infn_tl1:
        provider: "{{ tl1 }}"
        commands:
          - RTRV-ALM-ALL:::c
          - RTRV-EQPT:::c
        output: json
               
"""
#--------- Infinera Specific TL1 implementation -------------------------------#

# Required in case a fallback Telnet connection is to be used(Can be 
# used for making connections through Telnet instead of SSH)
# If the environmental variable 'USE_TELNET_FOR_ANSIBLE' is set to 'TRUE'
# then it the fallback is enable
# TODO: Move the env. var. to another file
if os.getenv("USE_TELNET_FOR_ANSIBLE", '') == "TRUE":
    is_telnet_fallback_req = True
else:
    is_telnet_fallback_req = False

# Common Parameters
provider_spec = {
    'host': dict(default="hostvars[inventory_hostname][\"ansible_host\"]"),
    'ssh_port': dict(type='int', default=22),
    'port': dict(type='int', default=9090),
    'username': dict(default="hostvars[inventory_hostname][\"ansible_user\"]"),
    'password': dict(default="hostvars[inventory_hostname][\"ansible_password\"]"),
    'tid': dict(default='')
}
base_argument_spec = {
    'provider': dict(type='dict', options=provider_spec),
}

stdout = ''  # Global buffer with module output


def main():
    '''
        Main code
    '''
    module_results = dict(
        status="",
    )

    spec = dict(
        commands_and_inputs=dict(type='dict'),
        script=dict(type='str'),
        save=dict(type='str'),
        output=dict(type='str', default='json')
    )
    mutually_exclusive = [('commands_and_inputs', 'script')]
    required_one_of = [('commands_and_inputs', 'script')]

    # Plus provider argument
    spec.update(base_argument_spec)
    module = AnsibleModule(argument_spec=spec, mutually_exclusive=mutually_exclusive,
                           required_one_of=required_one_of)
    # Establish Telnet Connection
    result = True
    cmdoutput = ''
    tl1obj = None

    ssh_error, is_ssh_failed = '', False
    try:
        tl1obj = ssh_tl1(module.params['provider']['host'], module.params['provider']['username'],
                         module.params['provider']['password'], module.params['provider']['ssh_port'],
                         module.params['provider']['tid'])
    except Exception as e:
        if 'User authentication failed' in to_text(e):
            module_results.update(
                status="FAILURE", error=to_text(e), msg="User authentication failed"
            )
            module.fail_json(
                **module_results
            )
        else:
            is_ssh_failed = True
            ssh_error = to_text(e)

    if is_ssh_failed:
        if is_telnet_fallback_req:
            try:
                tl1obj = telnet_tl1(module.params['provider']['host'], module.params['provider']['username'],
                                    module.params['provider']['password'], module.params['provider']['port'],
                                    module.params['provider']['tid'])
            except Exception as e:
                if 'User authentication failed' in to_text(e):
                    module_results.update(
                        status="FAILURE", error=to_text(e), msg="User authentication failed"
                    )
                    module.fail_json(
                        **module_results
                    )
                else:
                    module_results.update(
                        status="FAILURE", error=to_text(e), msg='Connection to {0} failed'.format(module.params['provider']['host'])
                    )
                    module.fail_json(
                        **module_results
                    )
        else:
            module_results.update(
                status="FAILURE", error="Could not establish connection - {0}".format(ssh_error), msg='Connection to {0} failed'.format(module.params['provider']['host'])
            )
            module.fail_json(
                **module_results
            )            

    # Get command list to send
    if module.params['script'] is not None:
        # convert script into individual commands
        with open(module.params['script'], 'r') as frd:
            cmdstoexecute = frd.read().splitlines()
    else:
        cmdstoexecute = list(six.iterkeys(module.params['commands_and_inputs']))

    # Open a log file to store the details of commands sent to NE
    # and received from NE.
    if 'save' in module.params and module.params['save'] is not None:
        save_file = open(module.params['save'], 'a')
    else:
        save_file = None

    failure_count = 0
    readable_str_counter = {} # See below for usage; readable_tl1cmd_str
    for idx,tl1cmd in enumerate(cmdstoexecute,1):
        cmd_status = {}
        cmd_status["Command"] = tl1cmd
        try:
            # sendcmd returns a boolean and the output(response from NE) as string.
            # result is True if the response from NE is successful(ie COMPLD in the response)
            # result is False if the response from NE does not have COMPLD(probably DENY)
            # cmdoutput will have complete output from NE which can be eiether
            # successful message or error message.
            result, cmdoutput = tl1obj.sendcmd(
                tl1cmd, output_format=module.params['output'])
            if result:
                cmd_status["result"] = cmdoutput
                cmd_status["status"] = "SUCCESS"
            else:
                cmd_status["error"] = cmdoutput
                cmd_status["status"] = "FAILURE"
                failure_count += 1
             # Also, save the TL1 Command output sent and received in file if the option
             # is provided.
            if module.params['save'] is not None:
                log_tl1cmd = make_masked_tl1_cmd(tl1cmd.rstrip()) # Hide sensitive data before saving to file
                outputstr = '>>>>>>>>>>\nSent the following TL1 cmd to %s:\n%s\n' \
                    % (module.params['provider']['host'], log_tl1cmd)
                outputstr += 'Received the following output from %s:\n%s\n<<<<<<<<<<\n' \
                    % (module.params['provider']['host'], cmdoutput)
                save_file.write(outputstr)

        except Exception as tl1exp:
            cmd_status["error"] = to_text(tl1exp)
            cmd_status["status"] = "FAILURE"
            failure_count += 1

        readable_tl1cmd_str = parse_to_readable_str(tl1cmd)
        current_key = readable_tl1cmd_str
        # For the cases where there is no AID(E.g., NTP-1, RADSERVER1), we get the same readable
        # string for different TL1 commands. E.g., Delete Rfile.
        # For such cases append counter of the number of duplicates to the readable string.
        if module_results.get(readable_tl1cmd_str, None) is not None:
            readable_str_counter[readable_tl1cmd_str] = 2 # First duplicate
            previous_value = module_results[readable_tl1cmd_str]
            previous_key = "{0}-{1}".format(readable_tl1cmd_str, 1)
            current_key = "{0}-{1}".format(readable_tl1cmd_str, 2)
            module_results[previous_key] = previous_value
            module_results.pop(readable_tl1cmd_str)
        else:
            if readable_str_counter.get(readable_tl1cmd_str, 0) > 1:
                readable_str_counter[readable_tl1cmd_str] += 1
                current_key = "{0}-{1}".format(readable_tl1cmd_str, readable_str_counter[readable_tl1cmd_str])
            else:
                readable_str_counter[readable_tl1cmd_str] = 1
                current_key = readable_tl1cmd_str

        module_results[current_key] = cmd_status
        module_results[current_key]["InputParameters"] = module.params['commands_and_inputs'][tl1cmd]

    # Ensure that commands are present
    if len(cmdstoexecute):
        if failure_count == len(cmdstoexecute):
            status = "FAILURE"
        elif failure_count > 0:
            status = "PARTIAL"
        else:
            status = "SUCCESS"
    else:
        status = "NO OPERATIONS NEED TO BE PERFORMED AS SYSTEM IS ALREADY CONFIGURED WITH INTENDED INPUT"
    
    # Close the file handler
    if save_file:
        save_file.close()
    # Close the TL1 session
    try:
        if tl1obj:
            tl1obj.close()
    except:
        pass
    
    module_results.update(
        status=status,
    )
    # Announce the results
    module.exit_json(
        **module_results
    )


if __name__ == '__main__':
    main()
