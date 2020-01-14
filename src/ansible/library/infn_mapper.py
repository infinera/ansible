"""
Utility for mapping TL1 repsonse parameters.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
from ansible.module_utils import six

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: infn_mapper
author: Anand Krishna Rallabhandi (anand-krishna)
short_description: Map the TL1 message parameters to user friendly ones
description:
  - This module maps the TL1 message parameters in the response received from the NE to the ones
    as stated in the mapper(generally, user friendly ones)
options:
  mapper:
    description:
      - Mapping between TL1 parameters and user friendly names
    required: true
    type: dict
  tl1_response:
    description:
      - The TL1 response received from the NE, that is parsed into a JSON
    required: true
    type: dict
"""

# TODO: Update the examples section

EXAMPLES = """
---
- hosts: ne
  connection: local
  tasks:
    - name: Retrieve RADIUS Servers
      infn_mapper:
        mapper: "{{ mapper }}"
        tl1_response: "{{ response }}"
"""


def main():
    spec = dict(
        mapper=dict(type='dict'),
        tl1_response=dict(type='dict')
    )
    module = AnsibleModule(argument_spec=spec)

    try:
        mapped_response = _map_response(
            module.params["tl1_response"], module.params["mapper"])
    except Exception as e:
        module.fail_json(
            msg="Error in mapping the TL1 response"
        )

    module.exit_json(**mapped_response)


def _map_response(tl1_msg_dict, mapper):

    # To skip all the Non AID keys
    keys_to_skip = frozenset(("RawResponse", "Parameters", "Description", "Text"))

    for cmd, cmd_meta in six.iteritems(tl1_msg_dict):
      if "RETRIEVE" in to_text(cmd):
        for cmd_key, cmd_resp in six.iteritems(cmd_meta.get("result", {})):
            if cmd_key not in keys_to_skip:
                param_keys = list(cmd_resp["Parameters"].keys())
                for key in param_keys:
                    mapper_key = mapper.get(key, None)
                    if mapper_key is not None:
                        value = cmd_resp["Parameters"].pop(key, None)
                        cmd_resp["Parameters"][mapper_key] = value
                    elif "RETRIEVE DEFAULT(S) SECURITY ATTRIBUTES" == to_text(cmd):
                        # For security attributes remove things not in mapper
                        cmd_resp["Parameters"].pop(key, None)

    return tl1_msg_dict


if __name__ == "__main__":
    main()
