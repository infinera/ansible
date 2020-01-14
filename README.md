
# Infinera Network Automation Suite 

Infinera Network Automation Suite comprises of Ansible network roles and modules that extend benefits of simple, agentless automation to network administrators. Infinera Network Automation Suite can configure a network, test and validate existing network state, discover and rectify network configuration drift. It supports a wide range of device types,and actions to manage the entire deployed Infinera network. 


## Infinera Ansible Roles

The Infinera Ansible roles provide a framework for independent or interdependent collection of tasks or files. 
These roles simplify a complex playbook into multiple files.

Infinera provides the following [**Ansible roles**](./src/ansible/README.md) to perform operations on Infinera network elements running IQ NOS Version R18.2.10.
These ansible roles and modules use TL1 over SSH protocol for secure network element          connectivity.

1. [RADIUS](./src/ansible/roles/iqnos_radius/README.md)
2. [NTP](./src/ansible/roles/iqnos_ntp/README.md)
3. [ACF](./src/ansible/roles/iqnos_acf/README.md)
4. [Security](./src/ansible/roles/security/README.md)
5. [Database Management](./src/ansible/roles/db_mgmt/README.md)
6. [Software Management](./src/ansible/roles/sw_mgmt/README.md)
7. [Network Element Configurations](./src/ansible/roles/NEConfig/README.md)
8. [Network Element Entity Configurations](./src/ansible/roles/NEEntityConfig/README.md)
9. [Network Element Call Home](./src/ansible/roles/ne_call_home/README.md)

With Infinera Network Automation Suite a user can:
* Use these roles and create custom playbooks.
* Use sample playbooks provided by Infinera.

## The following documentation is available for Ansible Network Automation

* [Installation Guide](./src/ansible/InstallationGuide.md)
* [Full Upgrade](./src/ansible/FullUpgrade.md)
* [Using Ansible Vault for  Data Encryption](./src/ansible/DataEncryption.md)
* [Task Output](./src/ansible/TaskOutput.md)
* [License information](./src/ansible/License.md)