#!/usr/bin/env python
"""
    This module provides access to Infinera devices using TL1 interface via SSH
"""
#--------- Infinera Specific SSH TL1 implementation -------------------------------#
import re
import sys
import time
import socket
import json
import logging
#try:
#    import paramiko
# except:
#    sys.modules["gssapi"] = None
#    import paramiko
sys.modules["gssapi"] = None
import paramiko

from ansible.module_utils.tl1_error import ERROR_CODES
from ansible.module_utils.tl1_utils import make_masked_tl1_cmd
from ansible.module_utils.tl1_formatter import parse_error_response, parse_normal_response

BUFFER_SIZE = 9999

def getlogger():
    '''
        This function is used to get the Logger Object to be used for logging.
        The log file is saved at /tmp as infn_ssh_tl1.log for debug purpose.
    '''
    logger = logging.getLogger('infn_ssh_tl1')
    hdlr = logging.FileHandler('/tmp/infn_ssh_tl1.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    hdlr.setLevel(logging.INFO)
    return logger

class TL1(object):
    '''
        This class is used to connect to TL1 subsystem via SSH, send commands and receive response
        from Infinera Devices.

    '''
    def __init__(self, neaddress, username, password, port=22, tid='', iqnos_rel_ver=18.2):
        self.username = username
        self.password = password
        self.neaddress = neaddress
        self.port = port
        self.tid = tid
        self.logger = getlogger()
       
        #paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connect(iqnos_rel_ver)
        output = ''
        for i in range(2):
            output = self.chan.recv(BUFFER_SIZE)
            print(output, i)
            if 'TL1>>' in output:
                break
        #Activate the user to process further commands
        activate_cmd = 'act-user:%s:%s:c::%s;' %(self.tid,self.username,self.password)
        self._send(activate_cmd)
        result,activate_output = self._recv()
        # print(result, activate_output)
        if result:
            self.logger.info('User authentication carried out successfully with user %s on NE(%s)',\
                self.username, self.neaddress)
        else:
            #If the user is not activated successfully, raise the Exception back as 
            #no command further will get processed if the user is not activated.
            self.logger.info('User authentication failed with user {0} on NE ({1})'.format(self.username, self.neaddress))
            raise Exception('User authentication failed with user {0} on NE ({1})'.format(self.username, self.neaddress))
        
        self.logger.info("Disabling Autonomous Messages Reporting")
        self._disable_autonomous_messages_reporting()
        
        self.logger.info("Disable Database Change Reporting")
        self._disable_database_changes_reporting()

    def _disable_autonomous_messages_reporting(self):
        self._send("INH-MSG-ALL:{TID}::CTAG::;".format(TID=self.tid))
        self._recv()

    def _disable_database_changes_reporting(self):
        self._send("INH-DBREPT-ALL:{TID}::CTAG;".format(TID=self.tid))
        self._recv()

    def _connect(self, iqnos_release_version):
        """
        Call the connect method corresponding to the IQNOS release version.
        """
        if iqnos_release_version == 18.2:
            self._connect_and_open_shell()
        elif iqnos_release_version == 19:
            self._connect_and_open_subsystem()
        else:
            raise Exception("The Connection module is not supported for IQNOS R{0}.".format(iqnos_release_version))

    def _connect_and_open_shell(self):
        """
        Connect to the NE running IQNOS R18.2 and open a shell for TL1 command execution.
        """
        try:
            self.ssh.connect(self.neaddress,port=self.port,username="tl1telnet",password="",look_for_keys=False)
        except Exception as e:
            raise Exception("SSH connection to '%s' failed:%s" %(self.neaddress,str(e)))
        if self.logger: self.logger.info("Connected successfully to '%s' via SSH" %self.neaddress)
        try:
            self.chan = self.ssh.invoke_shell()
            self.chan.keep_this = self.ssh
        except Exception as e:
            raise Exception('Failed to invoke shell')


    def _connect_and_open_subsystem(self):
        """
        Connect to the NE running IQNOS R19.X and invoke the `tl1telnet` subsystem for TL1 commands execution.
        """
        try:
            self.ssh.connect(self.neaddress,port=self.port,username=self.username,password=self.password,look_for_keys=False)
        except Exception as e:
            raise Exception("SSH connection to '%s' failed:%s" %(self.neaddress,str(e))) 
        if self.logger: self.logger.info("Connected successfully to '%s' via SSH" %self.neaddress)
        try:
            self.chan = self.ssh.get_transport().open_session()
            self.chan.invoke_subsystem('tl1telnet')
        except Exception as e:
            raise Exception('Failed to invoke subsystem tl1telnet')

    def _send(self,command,delay=2):
        '''
            A wrapper function for  Channel send command

        '''
        if self.chan.send_ready():
            self.chan.send(command+';')
            if self.logger:
                masked_cmd = make_masked_tl1_cmd(command)
                self.logger.info("Sent to NE %s: %s" %(self.neaddress, masked_cmd))
            time.sleep(4)

    def _recv(self):
        '''
            A wrapper function for Channel recv command

        '''
        output = ''
        result = False
        maxtime = 180
        curtime = 0 
        if self.chan.recv_ready():
            output = self.chan.recv(BUFFER_SIZE)
                        
            while True:
                #It is seen that when NE response IP (In progress response), the channel recv_ready becomes false
                #This condition is added to handle it.
                if not self.chan.recv_ready():
                    if ('COMPLD' in output or 'DENY' in output and not ' IP ' in output) and 'TL1>>':
                        break
                    else:
                        time.sleep(10)
                        curtime += 10
                        if curtime > maxtime:
                            break
                        continue
                else:
                    output += self.chan.recv(BUFFER_SIZE)
                    time.sleep(1)
                    if ('COMPLD' in output or 'DENY' in output and not ' IP ' in output) and 'TL1>>':
                        break
        if "ACT-USER:" in output or "act-user:" in output:
            output = re.sub(r'ACT-USER:[^;]+', 'ACT-USER:****************;', output)
            output = re.sub(r'act-user:[^;]+', 'act-user:****************;', output)
        if self.logger:
            self.logger.info("Response from NE %s: %s" %(self.neaddress,output))
        if 'COMPLD' in output:
            result = True 
        return result,output

    def sendcmd(self, command, output_format='tl1str'):
        '''
        This function is used to execute the provided TL1 command.

        '''
        try:
            result = False
            tl1cmdoutput = ''
            self._send(command)
            result,tl1cmdoutput = self._recv()
        except:
            return False, "SSH connection is closed"

        tl1cmdoutput = tl1cmdoutput.replace(command + "\r\n", '')
        tl1cmdoutput = tl1cmdoutput.replace("\r\nTL1>>", '')

        # Search for single AID retrievals of below facilities
        if re.search("RTRV-(ODU4|OTU4|ODU2e):.*:.+:.+;", command):
            is_facility = True
        else:
            is_facility = False

        if output_format == 'json':
            if result:
                try:
                    parsed_output = parse_normal_response(tl1cmdoutput)
                    self.logger.info('Response frm NE(%s) in JSON:\n%s', self.neaddress, parsed_output)
                except Exception as tl1_exp:
                    #If any exception seen during conversion, re-raise the exception so that
                    #the user is aware that there is something wrong in the conversion.
                    self.logger.info('Exception while converting TL1 string to JSON in NE(%s):%s', \
                        self.neaddress, tl1_exp)
                    parsed_output = tl1cmdoutput

            else:
                parsed_output = parse_error_response(tl1cmdoutput)
                # For cases where we don't have anything on the NE, the command returns DENY
                if ERROR_CODES["IENE"]["Description"] == parsed_output.get("Description", ""):
                    # Facilities don't have any TEXT block -> Fail the retrieval
                    if is_facility:
                        result = False
                    # In case of deleting something not present
                    elif re.search("^Object {.*}={.*} is not found$", parsed_output.get("Text", "")):
                        # Adding this for the case of enable lc task. No XCON -> it is treated as DENY.
                        if "XCON" in parsed_output.get("Text", ""):
                            result = True
                        else:
                            result = False
                    # In case of invoking on demand call home when the AID is not present on the NE
                    elif re.search("^Please check if the corresponding {.*} exists. \[{.*}\] cannot handle action \[{.*}\]$", parsed_output.get("Text", "")):
                        result = False
                    # In case of initiating software revert
                    elif re.search("^{Software Revert} failed. {Database} {.*} does not exist.$", parsed_output.get("Text", "")):
                        result = False
                    else:
                        result = True
        else:
            parsed_output = tl1cmdoutput

        return result, parsed_output

    def close(self):
        '''
        This function is used to log out the user and close the telnet connection.
        '''
        #Logout the user
        command = "canc-user:%s:%s:c;" %(self.tid, self.username)
        self._send(command)
        result,output = self._recv()
        if result:
            self.logger.info('User %s logged out successfully in NE(%s)', \
                self.username, self.neaddress)
        else:
            self.logger.info('User %s not logged out in NE(%s):\n%s', self.username, self.neaddress,\
                output)
        #Close the SSH and Channel connection
        if self.ssh:
            self.ssh.close()
        if self.chan:
            self.chan.close()

#------------------- End of Infinera TL1 implementation ------------------------------------------

