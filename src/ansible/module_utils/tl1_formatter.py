"""
Utilities for TL1 messages.
"""


def _parse_to_dict(msg):
    parsed_dict = {}

    raw_tl1_resp = msg.replace("\r\n\n", '')
    metadata, _, part_res = raw_tl1_resp.partition("\r\n")
    compl_code_data, _, part_res = part_res.partition("\r\n")
    terminator, _, part_res = part_res[::-1].partition("\n\r")
    text_blks = part_res[::-1]

    # # Ignore the 'M' character and the correlation tag
    # _, _, completion_code = [x for x in compl_code_data.split(' ') if x != '']
    
    parsed_dict["RawResponse"] = msg
    # parsed_dict["CommandStatus"] = completion_code
    parsed_dict["TextBlocks"] = text_blks
    parsed_dict["Terminator"] = terminator

    return parsed_dict

def parse_error_response(err_msg):
    parsed_msg_dict = _parse_to_dict(err_msg)
    
    text_blocks = parsed_msg_dict["TextBlocks"]

    parsed_error = {}
    parsed_error["RawResponse"] = parsed_msg_dict["RawResponse"]
    for line in text_blocks.split("\r\n"):
        if '\"' in line:
            parsed_error["Description"] = line.replace('\"', '').strip(' ')
        elif "/*" in line:
            parsed_error["Text"] = line.replace("/*", '').replace("*/", '').strip(' ')
    
    return parsed_error

def parse_normal_response(normal_msg):
    parsed_msg_dict = _parse_to_dict(normal_msg)
    
    text_blocks = parsed_msg_dict["TextBlocks"]

    tl1_info = {}
    tl1_params = []
    tl1_info["RawResponse"] = parsed_msg_dict["RawResponse"]
    for line in text_blocks.split("\r\n"):
        if '  "' in line:
            tl1_params.append(line)
    for idx, value in enumerate(tl1_params):
        arrayval = []
        stuff_before_first_colon, _, stuff_after_first_colon = value.strip().replace('\"','').replace('\\','').partition(':')
        if stuff_before_first_colon == '':
            aid = "Component-{0}".format(idx)
        elif ',' in stuff_before_first_colon:
            aid, aid_type =  stuff_before_first_colon.split(',')
        else:
            aid = stuff_before_first_colon
        stuff_inbetwn_first_and_second_colon, _, stuff_after_second_colon = stuff_after_first_colon.partition(':')
        parameters_and_state_data = stuff_after_second_colon
        tl1_info[aid] = {}
        # Colon is required in case we get an IS/OOS string in b/w - E.g., AUXTOSCHG=DISABLED
        if ":IS" in parameters_and_state_data or ":OOS" in parameters_and_state_data:
            rev_state_meta, _, rev_parameters = parameters_and_state_data[::-1].partition(':')
            state_meta = rev_state_meta[::-1]
            parameters = rev_parameters[::-1]
        else:
            parameters = parameters_and_state_data
            state_meta = ''
        tl1_info[aid]['Parameters'] = {}
        if '=' in parameters:
            fields = parameters.split(',')
            for field in fields:
                try:
                    # In certain cases the field string contains multiple equal-to chars.
                    # In such cases we partition on the first one and assign 
                    # the remaining string to the key.
                    if field.count('=') > 1:
                        key, eq_char, val = field.partition('=')
                    else:
                        key, val = field.split('=')
                except ValueError:
                    #Ignore, if there is no field with =, probably,
                    # there is a comma in value itself.
                    #Add this field to the value itself.
                    val += ',%s' %field
                val = val.strip()
                if 'OPMPWR' in field and ('#' in val or '&' in val):
                    if '#' in val:
                        arrayval = val.split('#')
                    elif '&' in val:
                        arrayval = val.split('&')
                    updarrayval = []
                    for item in arrayval:
                        try:
                            updarrayval.append(float(item))
                        except ValueError:
                            #Ignore if there are any strings
                            continue
                    tl1_info[aid]['Parameters'][key.strip()] = updarrayval
                else:
                    tl1_info[aid]['Parameters'][key.strip()] = val.strip().replace('\"','').replace('\\','')
        else:
            if ":IND" in normal_msg or ":RLS" in normal_msg:
                tl1_info[aid]['Parameters']['ARC'] = stuff_inbetwn_first_and_second_colon.replace('\"','').replace('\\','')
            elif "-DAY" in normal_msg:
                tl1_info[aid]['Parameters']['BackupSchedule'] = parameters
            else:
                tl1_info[aid]['Parameters']['Entity'] = parameters
        
        if state_meta != '':
            state_meta_ = state_meta.replace('\"','').replace('\\','')
            primary_state, _, secondary_state = state_meta_.partition(',')
            if '-' in primary_state:
                primary_state, _, primary_state_qualifier = primary_state.partition('-')
                tl1_info[aid]['Parameters']['PST'] = primary_state
                tl1_info[aid]['Parameters']['PSTQ'] = primary_state_qualifier
            else:
                tl1_info[aid]['Parameters']['PST'] = primary_state
            if secondary_state != '':
                tl1_info[aid]['Parameters']['SST'] = secondary_state

    return tl1_info
