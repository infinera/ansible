# Mandatory Parameters

The host file requires mandatory parameters:

* host_name - A readable name for the Network Element
* ansible_host - which is the IP Address of the Network Element
* ansible_user - The Username that will be used to login to the Network Element
* ansible_password - The Password associated with the above Username
* tid - The Target Identifier of the Network Element

> **TID is compulsory for all the tasks**
>
> Few Examples:
>
> 1. When changing the Operation Mode of a 1-100GX-TIM, a valid TID needs to be provided else the task execution fails. This TID maps to the AIDs of the TIM who's operation mode is to be changed
>
> 2. When the database backup name is to be different for each Network Element, the TID is to be provided. This TID is mapped to the specified name which will be the filename of the backup

## Sample `hosts.yml` file

```yaml
all: # keys must be unique, i.e. only one 'hosts' per group
  hosts:
    ne_1: &ne_1
      ansible_host : "10.220.165.84"
      ansible_user: "Username"
      ansible_password: "Password"
      tid: "XTC284"
  vars:
      ne_password: &ne_password "Password"
      ne_user: &ne_user "Username"
  children:   # key order does not matter, indentation does
        tune_up_group:
            children:
                ntp_group:
                    hosts:
                      ntp_1:
                        ansible_host : "10.220.165.86"
                        ansible_user: *ne_user
                        ansible_password: *ne_password
        db_group:
            hosts:
              ne_1: *ne_1
```
