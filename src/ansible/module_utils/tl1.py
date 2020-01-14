#!/usr/bin/env python
"""
    This module provides access to Infinera devices using TL1 interface.
"""

#--------- Infinera Specific TL1 implementation -------------------------------#
import re
import telnetlib
import time
import socket
import json
import logging

from ansible.module_utils.tl1_error import ERROR_CODES
from ansible.module_utils.tl1_utils import make_masked_tl1_cmd
from ansible.module_utils.tl1_formatter import parse_error_response, parse_normal_response

def getlogger():
    '''
        This function is used to get the Logger Object to be used for logging.
    '''
    logger = logging.getLogger('infn_tl1')
    hdlr = logging.FileHandler('/tmp/infn_tl1.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    hdlr.setLevel(logging.INFO)
    return logger


class TL1(object):
    '''
        This class is used to connect to TL1 and send the commands
    '''
    def __init__(self, neaddress, username, password, port=9090, tid=''):
        self.username = username
        self.password = password
        self.neaddress = neaddress
        self.port = port
        self.tl1tn = None
        self.tid = tid
        self.logger = getlogger()
        self._connect()

    def _connect(self):
        '''
            This API is used to connect to the TL1 (telnet on port 9090) session.
        '''
        self.tl1tn = telnetlib.Telnet(self.neaddress, self.port)
        self.logger.info("Telnet connection established successfully to NE %s at port %s", \
            self.neaddress, self.port)
        self.tl1tn.read_until("TL1>")
        #Activate the user - The user has to be activated in order to send any commands.
        self.tl1tn.write("act-user:%s:%s:c::%s;" %(self.tid, self.username, self.password)+"\n")
        time.sleep(2)
        tl1cmdoutput = self.tl1tn.read_very_eager()
        if 'COMPLD' in tl1cmdoutput:
            self.logger.info('User authentication carried out successfully with user %s on NE(%s)',\
                self.username, self.neaddress)
        else:
            self.logger.info('User authentication failed with user {0} on NE ({1})'.format(self.username, self.neaddress))
            raise Exception('User authentication failed with user {0} on NE ({1})'.format(self.username, self.neaddress))

        self.logger.info("Disabling Autonomous Messages Reporting")
        self._disable_autonomous_messages_reporting()
        
        self.logger.info("Disable Database Change Reporting")
        self._disable_database_changes_reporting()

    def _disable_autonomous_messages_reporting(self):
        self.tl1tn.write("INH-MSG-ALL:{TID}::CTAG::;".format(TID=self.tid))
        time.sleep(2)
        self.tl1tn.read_very_eager()

    def _disable_database_changes_reporting(self):
        self.tl1tn.write("INH-DBREPT-ALL:{TID}::CTAG;".format(TID=self.tid))
        time.sleep(2)
        self.tl1tn.read_very_eager()

    def sendcmd(self, command, output_format='tl1str', delay=2):
        '''
        This function is used to execute the provided TL1 command.

        '''
        result = False
        tl1cmdoutput = ''
        connection_retry = 1
        max_connection_retry = 2
        max_tl1_response_time = 60
        tl1_response_time = 0
        #Retry 1 (Outer While):To handle the occasional socket error/Telnet EOFError seen with NE.
        #Retry 2 (Inner While):To handle the incomplete/slow response from NE. Wait until
        #COMPLD or DENY seen within 60secs.
        while connection_retry <= max_connection_retry:
            try:
                self.tl1tn.write(command)
                masked_cmd = make_masked_tl1_cmd(command)
                self.logger.info('Sent the following command to NE (%s):\n%s', \
                    self.neaddress, masked_cmd)
                time.sleep(delay)
                while tl1_response_time <= max_tl1_response_time:
                    tl1_response_time += 1
                    time.sleep(1)
                    tl1cmdoutput += self.tl1tn.read_very_eager()
                    self.logger.info('Received the following response from NE (%s):\n%s', \
                        self.neaddress, tl1cmdoutput)
                    if 'COMPLD' in tl1cmdoutput or 'DENY' in tl1cmdoutput:
                        if 'COMPLD' in tl1cmdoutput:
                            result = True
                        break
                break
            except (EOFError, socket.error):
                connection_retry += 1
                #Probably a network glitch, hence reconnect after 15 secs
                time.sleep(15)
                self._connect()
            except Exception as tl1_exp:
                self.logger.info('Exception occurred while processing TL1 command in NE (%s):%s',\
                    self.neaddress, tl1_exp)
                raise Exception(tl1_exp)
        tl1cmdoutput = tl1cmdoutput.replace(command + "\r\n", '')
        tl1cmdoutput = tl1cmdoutput.replace("\r\nTL1>>", '')

        # Search for single AID retrievals of below facilities
        if re.search("RTRV-(ODU4|OTU4|ODU2e):.*:.+:.+;", command):
            is_facility = True
        else:
            is_facility = False

        if output_format == 'json':
            #Convert to json
            if result:
                try:
                    parsed_output = parse_normal_response(tl1cmdoutput)
                    self.logger.info('Response frm NE(%s) in JSON:\n%s', self.neaddress, tl1cmdoutput)
                except Exception as tl1_exp:
                    #Ignore if there any error in converting to json. Return tl1str instead
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
        self.tl1tn.write(command)
        self.logger.info('Sent the following command to NE (%s):%s', self.neaddress, command)
        time.sleep(2)
        tl1cmdoutput = self.tl1tn.read_very_eager()
        self.logger.info('Received the following response from NE (%s):%s', \
            self.neaddress, tl1cmdoutput)
        if 'COMPLD' in tl1cmdoutput:
            self.logger.info('User %s logged out successfully in NE(%s)', \
                self.username, self.neaddress)
        else:
            self.logger.info('User %s did not log out in NE(%s)', self.username, self.neaddress)
        #Close the Telnet connection
        if self.tl1tn:
            self.tl1tn.close()

#------------------- End of Infinera TL1 implementation ------------------------------------------#
