# Task Output Structure

The general form of output for each task that is performing operations on the network element has the following structure.

Note: The tasks that validate input and map the raw network element response to a readable form have a different structure.

```json
{
    "TaskName1": {
        "InputParameters": {},
        "Result": {},
        "TaskStatus": "Value"
    },
    "TaskName2": {
        "InputParameters": {},
        "Result": {
            "Component-0": {
                "Parameters": {
                    "Property1": "Value1",
                    "Property2": "Value2",
                    "Property3": "Value3",
                    .
                    .
                    .
                }
            },
            "Component-1": {
                "Parameters": {
                    "Property1": "Value1"
                }
            },
            .
            .
            .
        },
        "TaskStatus": "Value"
    },
    .
    .
    .
    "OverallStatus": "Value"
}
```

The overall status is useful in cases where multiple commands are sent to the network element.

* For instance, Editing three NTP servers

> The *Component-X* block denotes the different entities associated with the task's output
> In certain cases it has a task specific name

### Sample  for generic *Component-X* response 

```json
{
    "RETRIEVE DEFAULT(S) SECURITY ATTRIBUTES": {
        "Parameters": {},
        "result": {
            "Component-0": {
                "Parameters": {
                    "ACLISESSION": "ENABLED",
                    "AUTHPOLICY": "LOCAL",
                    "DURAL": "60",
                    "FXFRSSH": "false",
                    "HTTPS": "false",
                    "MAXSESS": "30",
                    "MXINV": "3",
                    "PIDCHGPOLICY": "USER",
                    "POSTLOGINWARNDIS": "ENABLE",
                    "PRELOGINWARNDIS": "DISABLE",
                    "PWDDIGEST": "SHA_256",
                    "PWDROT": "5",
                    "SCP": "DISABLE",
                    "SECUREALL": "false",
                    "SERIALACCESS": "ENABLED",
                    "TL1SSH": "false",
                    "TLSCERT": "NONE",
                    "TLSCONNTIME": "86400",
                    "TLSIDLETIME": "180",
                    "TNETSSH": "false",
                    "XMLSSH": "false",
                    "ssh_finger_print": "0b:26:36:cf:8d:49:90:ae:d9:cc:1f:1a:4f:09:87:d3"
                }
            }
        },
        "status": "SUCCESS"
    },
    "status": "SUCCESS"
}
```

### Sample for Task specific result blocks

```json
{
    "RETRIEVE NTP": {
        "InputParameters": {},
        "result": {
            "NTP-1": {
                "Parameters": {
                    "ipaddress": "10.220.0.1",
                    "is_active_source": "false",
                    "ntp_status": "REJECT",
                    "primary_state": "OOS",
                    "primary_state_qualifier": "AUMA"
                }
            },
            "NTP-2": {
                "Parameters": {
                    "ipaddress": "10.220.0.12",
                    "is_active_source": "false",
                    "ntp_status": "REJECT",
                    "primary_state": "OOS",
                    "primary_state_qualifier": "AUMA"
                }
            },
            "NTP-3": {
                "Parameters": {
                    "ipaddress": "10.220.0.11",
                    "is_active_source": "false",
                    "ntp_status": "REJECT",
                    "primary_state": "OOS",
                    "primary_state_qualifier": "AUMA"
                }
            }
        },
        "status": "SUCCESS"
    },
    "status": "SUCCESS"
}
```
