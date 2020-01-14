
# Infinera Network Automation Suite 

Infinera Network Automation Suite comprises of Ansible network roles and modules that extend benefits of simple, agentless automation to network administrators. Infinera Network Automation Suite can configure a network, test and validate existing network state, discover and rectify network configuration drift. It supports a wide range of device types,and actions to manage the entire deployed Infinera network. 


## Infinera Ansible Roles

The Infinera Ansible roles provide a framework for independent or interdependent collection of tasks or files. 
These roles simplify a complex playbook into multiple files.

Infinera provides the following **Ansible roles** to perform operations on Infinera network elements running IQ NOS Version R18.2.10.
These ansible roles and modules use TL1 over SSH protocol for secure network element          connectivity.

1. [RADIUS](./roles/iqnos_radius/README.md)
2. [NTP](./roles/iqnos_ntp/README.md)
3. [ACF](./roles/iqnos_acf/README.md)
4. [Security](./roles/security/README.md)
5. [Database Management](./roles/db_mgmt/README.md)
6. [Software Management](./roles/sw_mgmt/README.md)
7. [Network Element Configurations](./roles/NEConfig/README.md)
8. [Network Element Entity Configurations](./roles/NEEntityConfig/README.md)
9. [Network Element Call Home](./roles/ne_call_home/README.md)

With Infinera Network Automation Suite a user can:
* Use these roles and create custom playbooks.
* Use sample playbooks provided by Infinera.

## The following documentation is available for Ansible Network Automation

* [Installation Guide](./InstallationGuide.md)
* [Full Upgrade](./FullUpgrade.md)
* [Using Ansible Vault for  Data Encryption](./DataEncryption.md)
* [Task Output](./TaskOutput.md)
* [License information](./License.md)