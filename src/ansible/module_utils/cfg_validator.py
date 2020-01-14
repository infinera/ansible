"""
Utility for validating a a configuration against a JSON Schema.
"""

import ast
import json
import jsonschema

from collections import deque

from ansible.module_utils._text import to_text


def validate(what_am_I_validating, configs, schema):
    """
    Validate a dictionary representing a configuration against a JSON Schema and return
    the result.

    Parameters
    ----------
    configs: dict
    what_am_I_validating: str
    schema: str
    
    Returns
    -------
    is_validated,error,result: tuple
        The tuple containing the result of the validations along with any errors if present.
    """
    is_validated,error,result = True,"",""
    try:
        double_quoted_schema = ast.literal_eval(schema) # module.params["schema"] is a single quoted; JSON spec. says only double quotes are allowed
        jsonschema.validate(configs, double_quoted_schema, format_checker=jsonschema.FormatChecker(["ipv4", "ipv6"]))
    except jsonschema.ValidationError as e:
        is_validated = False
        prefix_message = "Error in validating the {0}.".format(what_am_I_validating)
        # This is just in case :)))))
        try:
            suffix_dict = {
                1: "st",
                2: "nd",
                3: "rd"
            }
            if len(e.relative_path) == 0:
                if "ipv4" in e.message or "ipv6" in e.message:
                    error = "Invalid IP Address : {0}".format(e.instance)
                else:
                    if "regexes" in e.message:
                        regex_str = e.message[e.message.index("^"): e.message.index("$") + 1]
                        error = "The value is not in the permissible set: {0}".format(_parse_regex(regex_str, "top_key"))
                    else:
                        error = e.message
            else:
                error_meta = e.path
                parent = error_meta.popleft()
                error_element = parent # Sometimes there are no elements in the deque for us to process
                error_str = "The property causing error is under '{0}', ".format(parent)
                while error_meta:
                    element = error_meta.popleft()
                    if type(element) is int:
                        error_str += "in the '{0}{1}' entity, ".format(element + 1, suffix_dict.get(element + 1, "th"))
                    elif len(error_meta) == 0:
                        error_element = element
                        error_str += "which is '{0}'".format(error_element)
                    else:
                        error_str += "under '{0}', ".format(element)

                if error_element == "shared_secret_key":
                    error_message = e.message.replace("\'" + to_text(e.instance) + "\'", "******")
                else:
                    error_message = e.message

                if "regex" in error_message or "does not match" in error_message:
                    permissible_vals = _parse_regex(e.validator_value, error_element)                        
                    message_to_display = "The value is not in the permissible set: {0}".format(permissible_vals)
                elif "type" in error_message:
                    message_to_display = "Invalid value for {0} - {1}.".format(error_element, error_message.replace("None", "Blank entry").replace("u'", "").replace("'", ""))
                else:
                    message_to_display = error_message

                error = error_str + ": " +  str(message_to_display)
        except:
            error = e.message
        error = "{0}{1}".format(prefix_message, error)
    else:
        result = "Configuration validated successfully against the schema"

    return is_validated,error,result

def _parse_regex(regex, err_attr=''):
    """
    Parse the regex string to extract the permissible values for the attribute.

    Parameters
    ----------
    regex: string
    err_attr: string

    Returns
    -------
    permissible_vals: any
    """
    characters = ['^', '$', '(', ')']
    string_ = regex.replace("(?i)", '')
    for character in characters:
        string_ = string_.replace(character, '')
    if "identifier" in err_attr or err_attr == "top_key":
        prefix_val = string_[: string_.index('[')]
        lower_bound, upper_bound = int(string_[string_.index('[') + 1]), int(string_[string_.index(']') - 1])
        return ["{0}{1}".format(prefix_val, to_text(idx)) for idx in range(lower_bound, upper_bound + 1)]
    elif err_attr == "time":
        return { "Hours": "0-23", "Minutes": [00, 15, 30, 45] }
    else:
        return ["{0}".format(to_text(x)) for x in string_.split('|')]
