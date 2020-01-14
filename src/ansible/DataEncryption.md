# Using Ansible Vault

This document provides detailed instructions to use Ansible Vault to encrypt or decrypt the configuration files and sensitive information.
In order to protect host information and configuration information, hosts and configuration .yml files are encrypted using Ansible Vault. 
User has to enter Vault password while running the playbooks to proceed with the execution or user can decrypt the files first and then run the playbook.

## Instructions to be followed to use the Ansible Vault

1. Use the following flags with the `ansible-playbook` command to use encrypted data in plays.
   1. If all the data is encrypted with a single password
        * `--ask-vault-pass`
   2. If different passwords are used for different pieces of data
       * `--vault-id`
2. Use the flag `--vault-id` to create multiple passwords. It creates different password for each encrypted piece of data.
   * --vault-id ID@prompt contains multiple ID associated with multiple passwords

## Sample encryption file with single password

  
  * `ansible-vault encrypt file_name`

  ```console
  $ cat full_upgrade_config.yml
  ---

  sw_configs:
    username: gbuild
    password: 123gbuild
    ipaddress: 10.220.0.234
    path: /home/pub/M20.0.0.9601/tar_ne
    sw_image_version: M20.0.0.9601
    protocol: ftp
    is_sim: true # For internal purposes
    # db_image_name: DB_20190513.061514NE2 # Required for restoring


  db_configs:
    primary:
      username   : root
      password   : password
      ipaddress  : 10.220.27.75
      path       : dbbkups
      protocol   : sftp

  $ ansible-vault encrypt full_upgrade_config.yml
  New vault password:
  Confirm vew vault password:
  Encryption successful

  $ cat full_upgrade_config.yml
  $ANSIBLE_VAULT;1.2;AES256
  63633661373934333634363462383464316164653039336233313636383063356538343236623831
  6539316439623238666238386666663262323035346561630a393732613538376139613462336464
  31303764663239393032313439633264303062366266653063356636356431383062366665363961
  3037623136643839360a656263323132363965613164323530373734366433336231383430373038
  30653232373934376665306266633564373763313037323534633064323038633634663539306534
  39663462353165363932626666383433333266343231643234386330363737316537336163326431
  35333733346466656666626163646639303330393135356335656265313432656431336363653061
  31366439393535646534356664366330373861303766383439303666353834306230316539626433
  37373765646331333063626333306233663662383661643838343335356163326566366634616334
  65313162376430666534663063383232393737313330306564363766336536616662613538663166
  66366638313865383330376338626335313533386236306666373966366531386132646236616137
  36623630346538623036333733623737383231646138393666663166326661396465386536313331
  31623861346365616630373063653832376433343861333764363336613836353262383231386432
  30376636323132343461306131646235333262383063663938643732343531373666383463326335
  38633536623535346234363230663265353761616366393533643038653639396364636438373731
  34323234333137303337376138393361303639643664396237633439323264623965346163323830
  63326131626563653166663838303735336533653365376331663464343831323335646366666634
  34376266643431633230303363353135376263633064653262323963353633653463633235646264
  38326537656162353766336536616331323262323738376665626262613464363736343839336264
  37366164393539356131623236306434353730646537353863313866393365616231323864323865
  61633439656264366231383166633038653466323365376435313762663935376532333363613038
  64353935623730633735396130303137363238396431636364633731633561353338643964643930
  39623764336465363133636432633766313230343263663735376334646432646166653936613634
  35396636663430663236613934343835616635386638383938633132633031646433373839633037
  39343532353961363536616263623133633065613339376464323136626436643161663562373366
  6434333565363434313963656531366664316533353334633431
  ```

   ## Perform the following steps to encrypt a selected content with single password 
  
  1. Execute the below command to encrypt the string value for encryption.

    `ansible-vault encrypt_string string_to_encrypt --name name_of_the_key`

  2. Paste the below string into the file that should contain this encrypted value.

    `variable_name: <Encrypted Meta><Encrypted Data>` 

  Sample encryption of selected content with single password

    ```shell
    $ cat full_upgrade_config.yml
    ---

    sw_configs:
      username: gbuild
      password: password
      ipaddress: 10.220.0.234
      path: /home/pub/M20.0.0.9601/tar_ne
      sw_image_version: M20.0.0.9601
      protocol: ftp
      is_sim: true # For internal purposes
      # db_image_name: DB_20190513.061514NE2 # Required for restoring


    db_configs:
      primary:
        username   : root
        password   : password
        ipaddress  : 10.220.27.75
        path       : dbbkups
        protocol   : sftp

    $ ansible-vault encrypt_string "123gbuild" --name password
    New vault password:
    Confirm vew vault password:
    password: !vault |
              $ANSIBLE_VAULT;1.2;AES256
              64383535366530656662356463383433323561353036306332356337313430323635323539616439
              3765303465356539656336383434396464666262356532610a393734616563623163376631333965
              63386532363565306461303830653464303835393866393431303734326138613935333136643838
              3037656264316235650a653235356433663435366262323936313736306466386436343339383437
              3336
    Encryption successful

    $ # Paste the above as is in the appropriate place 

    $ cat full_upgrade_config.yml
    ---

    sw_configs:
    username: gbuild
    password: !vault |
              $ANSIBLE_VAULT;1.2;AES256
              64383535366530656662356463383433323561353036306332356337313430323635323539616439
              3765303465356539656336383434396464666262356532610a393734616563623163376631333965
              63386532363565306461303830653464303835393866393431303734326138613935333136643838
              3037656264316235650a653235356433663435366262323936313736306466386436343339383437
              3336
    ipaddress: 10.220.0.234
    path: /home/pub/M20.0.0.9601/tar_ne
    sw_image_version: M20.0.0.9601
    protocol: ftp
    is_sim: true # For internal purposes
    db_image_name: DB_20190513.061514NE2 # Required for restoring
   ```

Sample encryption file with multiple passwords
  
  * `ansible-vault encrypt --vault-id identifier@prompt file_name`

  ```console
  $ cat full_upgrade_config.yml
  ---

  sw_configs:
    username: gbuild
    password: 123gbuild
    ipaddress: 10.220.0.234
    path: /home/pub/M20.0.0.9601/tar_ne
    sw_image_version: M20.0.0.9601
    protocol: ftp
    is_sim: true # For internal purposes
    # db_image_name: DB_20190513.061514NE2 # Required for restoring


  db_configs:
    primary:
      username   : root
      password   : password
      ipaddress  : 10.220.27.75
      path       : dbbkups
      protocol   : sftp

  $ ansible-vault --vault-id fup@prompt encrypt full_upgrade_config.yml
  New vault password (fup):
  Confirm vew vault password (fup):
  Encryption successful

  $ cat full_upgrade_config.yml
  $ANSIBLE_VAULT;1.2;AES256;fup
  63633661373934333634363462383464316164653039336233313636383063356538343236623831
  6539316439623238666238386666663262323035346561630a393732613538376139613462336464
  31303764663239393032313439633264303062366266653063356636356431383062366665363961
  3037623136643839360a656263323132363965613164323530373734366433336231383430373038
  30653232373934376665306266633564373763313037323534633064323038633634663539306534
  39663462353165363932626666383433333266343231643234386330363737316537336163326431
  35333733346466656666626163646639303330393135356335656265313432656431336363653061
  31366439393535646534356664366330373861303766383439303666353834306230316539626433
  37373765646331333063626333306233663662383661643838343335356163326566366634616334
  65313162376430666534663063383232393737313330306564363766336536616662613538663166
  66366638313865383330376338626335313533386236306666373966366531386132646236616137
  36623630346538623036333733623737383231646138393666663166326661396465386536313331
  31623861346365616630373063653832376433343861333764363336613836353262383231386432
  30376636323132343461306131646235333262383063663938643732343531373666383463326335
  38633536623535346234363230663265353761616366393533643038653639396364636438373731
  34323234333137303337376138393361303639643664396237633439323264623965346163323830
  63326131626563653166663838303735336533653365376331663464343831323335646366666634
  34376266643431633230303363353135376263633064653262323963353633653463633235646264
  38326537656162353766336536616331323262323738376665626262613464363736343839336264
  37366164393539356131623236306434353730646537353863313866393365616231323864323865
  61633439656264366231383166633038653466323365376435313762663935376532333363613038
  64353935623730633735396130303137363238396431636364633731633561353338643964643930
  39623764336465363133636432633766313230343263663735376334646432646166653936613634
  35396636663430663236613934343835616635386638383938633132633031646433373839633037
  39343532353961363536616263623133633065613339376464323136626436643161663562373366
  6434333565363434313963656531366664316533353334633431
  ```

## Perform the following steps to encrypt a selected content with multiple passwords
  
  1. Execute the below command to encrypt the string value for encryption.

   `ansible-vault encrypt_string --vault-id identifier@prompt string_to_encrypt --name name_of_the_key`

  2. Paste the below string into the file that should contain this encrypted value.

   `variable_name: <Encrypted Meta><Encrypted Data>` 

Sample encryption of selected content with multiple passwords

    ```shell
     $ cat full_upgrade_config.yml
  ---

   sw_configs:
    username: gbuild
    password: 123gbuild

    ipaddress: 10.220.0.234
    path: /home/pub/M20.0.0.9601/tar_ne
    sw_image_version: M20.0.0.9601
    protocol: ftp
    is_sim: true # For internal purposes
    # db_image_name: DB_20190513.061514NE2 # Required for restoring


   db_configs:
    primary:
      username   : root
      password   : password
      ipaddress  : 10.220.27.75
      path       : dbbkups
      protocol   : sftp

   $ ansible-vault --vault-id fup_sw_ftp@prompt encrypt_string "123gbuild" --name password
   New vault password (fup_sw_ftp):
   Confirm vew vault password (fup_sw_ftp):
   password: !vault |
            $ANSIBLE_VAULT;1.2;AES256;fup_sw_ftp
            64383535366530656662356463383433323561353036306332356337313430323635323539616439
            3765303465356539656336383434396464666262356532610a393734616563623163376631333965
            63386532363565306461303830653464303835393866393431303734326138613935333136643838
            3037656264316235650a653235356433663435366262323936313736306466386436343339383437
            3336
  Encryption successful

  $ # Paste in the above as is in the appropriate place 

  $ cat full_upgrade_config.yml
  cat full_upgrade_config.yml
  ---

  sw_configs:
  username: gbuild
  password: !vault |
            $ANSIBLE_VAULT;1.2;AES256;fup_sw_ftp
            64383535366530656662356463383433323561353036306332356337313430323635323539616439
            3765303465356539656336383434396464666262356532610a393734616563623163376631333965
            63386532363565306461303830653464303835393866393431303734326138613935333136643838
            3037656264316235650a653235356433663435366262323936313736306466386436343339383437
            3336
  ipaddress: 10.220.0.234
  path: /home/pub/M20.0.0.9601/tar_ne
  sw_image_version: M20.0.0.9601
  protocol: ftp
  is_sim: true # For internal purposes
  db_image_name: DB_20190513.061514NE2 # Required for restoring

  ```

## Example hosts.yml 
  ```yaml
# This is the default ansible 'hosts.yml' file.
#
# It should live in /etc/ansible/hosts
#
#   - Comments begin with the '#' character
#   - Blank lines are ignored
#   - Groups of hosts are keys followed by hosts
#   - You can enter hostnames or ip addresses
#   - A hostname/ip can be a member of multiple groups

all: # keys must be unique, i.e. only one 'hosts' per group
  hosts:
    ne_1: &ne_1
      ansible_host : "10.220.165.84"
      ansible_user: "secadmin"
      ansible_password: !vault |
            $ANSIBLE_VAULT;1.2;AES256;fup_sw_ftp
            64383535366530656662356463383433323561353036306332356337313430323635323539616439
            3765303465356539656336383434396464666262356532610a393734616563623163376631333965
            63386532363565306461303830653464303835393866393431303734326138613935333136643838
            3037656264316235650a653235356433663435366262323936313736306466386436343339383437
            3336
      tid: "XTC284"
  vars:
      ne_password: &ne_password "password"
      ne_user: &ne_user "secadmin"
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

## Commands to run the Playbook 

1. Single Password
   * `ansible_playbook playbook.yml <other_options> --ask-vault-pass`
2. Multiple Passwords
   * `ansible_playbook playbook.yml <other_options> --vault-id ID1@prompt --vault-id ID2@prompt`
