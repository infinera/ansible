"""
Utilities for TL1 commands.
"""

import re

from ansible.module_utils import six


# Strings found in the TL1 commands
ED_FXFR_STR = "ED-FXFR"
COPY_RFILE_STR = "COPY-RFILE"
ED_RADIUS_STR = "ED-RADIUS"
ENT_CERT_STR = "ENT-CERT"
ACT_USER_STR = "ACT-USER"
RADSS_STR = "RADSS"
PASSPHRASE_STR = "PASSPHRASE"
PRIFTPPID_STR = "PRIFTPPID"
PRIDSTFILENAME_STR = "PRIDSTFILENAME"

# Map the words found in the TL1 command to better readable words
cmd_verbs = {
    "ENT": "Enter",
    "ED": "Edit",
    "RTRV": "Retrieve",
    "DLT": "Delete",
    "CANC": "Log out",
    "OPR": "Operate",
    "SET": "Set threshold values",
    "INIT": "Initialize",
    "ACT": "Activate",
    "CPY": "Copy"
}

cmd_modifiers = {
    "EQPT": "Equipment",
    "CRS": "Cross-connect",
    "USER": "User",
    "SECU": "Security Attributes",
    "DFLT": "Default(s)",
    "MEM": "Memory Contents",
    "SECUDFLT": "Security Default(s)",
    "DEFTEMP": "Default Template(s)"
}

def parse_to_readable_str(tl1_command):
    """ Return a readable representation of the TL1 command """
    verbs_n_modifiers, _, cmd_ = tl1_command.partition(":")
    target_id, _, cmd_ = cmd_.partition(':')
    aid, _, cmd_ = cmd_.partition(':')

    verb, _, modifiers = verbs_n_modifiers.partition('-')

    if aid == '':
        aid_str = ''
    else:
        aid_str = " FOR {0}".format(aid)

    return (cmd_verbs.get(verb, verb) + ' ' + ' '.join(map(lambda x:cmd_modifiers.get(x, x), modifiers.split('-')))).upper() + aid_str


def make_masked_tl1_cmd(tl1_cmd_str):
    """ Return a TL1 command with the sensitive data censored """
    masked_tl1_cmd_str = tl1_cmd_str
    if ACT_USER_STR in tl1_cmd_str.upper():
        reverse_act_cmd = tl1_cmd_str[::-1]
        reverse_act_cmd_ = reverse_act_cmd.replace(reverse_act_cmd[1:reverse_act_cmd.index(':')], "*****")
        masked_tl1_cmd_str = reverse_act_cmd_[::-1]
    if COPY_RFILE_STR in tl1_cmd_str or ENT_CERT_STR in tl1_cmd_str:
        uri_occurrences = re.findall("ftp://.*:.*@.*/", tl1_cmd_str)
        uri_occurrences_ = { original_str: re.sub(":[^:]*@", ":*****@", original_str) for original_str in uri_occurrences }
        for original_str, masked_str in six.iteritems(uri_occurrences_):
            masked_tl1_cmd_str = masked_tl1_cmd_str.replace(original_str, masked_str)
    if PASSPHRASE_STR in tl1_cmd_str:
        masked_tl1_cmd_str = re.sub(PASSPHRASE_STR + "=.*", PASSPHRASE_STR + "=*****", masked_tl1_cmd_str)
    if ED_RADIUS_STR in tl1_cmd_str:
        masked_tl1_cmd_str = re.sub(RADSS_STR + "=.*", RADSS_STR + "=*****", masked_tl1_cmd_str)
    if ED_FXFR_STR in tl1_cmd_str:
        masked_tl1_cmd_str = re.sub(PRIFTPPID_STR + "=.*," + PRIDSTFILENAME_STR, PRIFTPPID_STR + "=*****," + PRIDSTFILENAME_STR, masked_tl1_cmd_str)

    return masked_tl1_cmd_str
