from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: infnstdout
    type: stdout
    short_description: Ansible screen output
    description:
        - Output callback that is built atop the default output callback for the ansible-playbook with
          a few additions and changes, to hide sensitive data, to indicate partial status and have a different color 
          for task who's status is PARTIAL, and to have a consistent indentation for JSON results.
    requirements:
      - set as stdout in configuration
'''

import re

from ansible import constants as C
from ansible.playbook.task_include import TaskInclude
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import colorize, hostcolor
from ansible.module_utils import six

# These values use ansible.constants for historical reasons, mostly to allow
# unmodified derivative plugins to work. However, newer options added to the
# plugin are not also added to ansible.constants, so authors of derivative
# callback plugins will eventually need to add a reference to the common docs
# fragment for the 'default' callback plugin

# these are used to provide backwards compat with old plugins that subclass from default
# but still don't use the new config system and/or fail to document the options
COMPAT_OPTIONS = (('display_skipped_hosts', C.DISPLAY_SKIPPED_HOSTS),
                  ('display_ok_hosts', True),
                  ('show_custom_stats', C.SHOW_CUSTOM_STATS),
                  ('display_failed_stderr', False),)

replace_value_map =	{ "password": "*****","NE_Pwd": "*****","shared_secret_key":"*****", "pass_phrase": "*****"}

# To hide the secrets in the TL1 commands passed as inputs
# TODO: Move these into a constants file
ED_FXFR_STR = "ED-FXFR"
COPY_RFILE_STR = "COPY-RFILE"
ED_RADIUS_STR = "ED-RADIUS"
ENT_CERT_STR = "ENT-CERT"
RADSS_STR = "RADSS"
PASSPHRASE_STR = "PASSPHRASE"
PRIFTPPID_STR = "PRIFTPPID"
PRIDSTFILENAME_STR = "PRIDSTFILENAME"


class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'infnstdout'

    def __init__(self):

        self._play = None
        self._last_task_banner = None
        self._last_task_name = None
        self._task_type_cache = {}
        self._partial_exec_count = {} # For tasks who's status is partial
        super(CallbackModule, self).__init__()

    def _replace_item(self,obj, replacedic):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, dict):
                    obj[k] = self._replace_item(v, replacedic)
                elif isinstance(v, list):
                    new_v = []
                    for entry in v:
                        new_entry = self._replace_item(entry, replacedic)
                        new_v.append(new_entry)
                    obj[k] = new_v
            for k,v in replacedic.items():
                if k in obj:
                    obj[k] = v
        return obj

    def _make_masked_tl1_cmd(self, tl1_cmd_str):
        # TODO: Move this to a separate file
        masked_tl1_cmd_str = tl1_cmd_str
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

    def _clean_results(self, result, task_action):
        super(CallbackModule, self)._clean_results(result, task_action)
        
        result = self._replace_item(result, replace_value_map)

        result_ = result.get("msg", result)

        if type(result_) is dict:
            # Sometimes we might get other stuff :)
            result_.pop("changed", None)
            result_.pop("failed", None)
            result_.pop("failed_when_result", None)

            if self._display.verbosity < 3:
                for key,value in six.iteritems(result_):
                    if type(value) is dict:
                        if value.get("Command", None) is not None:
                            result_[key].pop("Command")
                        if value.get("result", None) is not None and value["result"].get("RawResponse", None) is not None:
                            result_[key]["result"].pop("RawResponse")
                        if value.get("error", None) is not None and value["error"].get("RawResponse", None) is not None:
                            result_[key]["error"].pop("RawResponse")
            else:
                # Hide sensitive data in TL1 Command strings
                commands_and_inputs = result_.get("invocation", {}).get("module_args", {}).get("commands_and_inputs", {})
                for command,input_parameters in six.iteritems(commands_and_inputs):
                    commands_and_inputs.pop(command)
                    new_command = self._make_masked_tl1_cmd(command)
                    commands_and_inputs[new_command] = input_parameters

                for key,value in six.iteritems(result_):
                    if type(value) is dict:
                        if value.get("Command", None) is not None:
                            masked_command_str = self._make_masked_tl1_cmd(value["Command"])
                            value["Command"] = masked_command_str

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        # for backwards compat with plugins subclassing default, fallback to constants
        for option, constant in COMPAT_OPTIONS:
            try:
                value = self.get_option(option)
            except (AttributeError, KeyError):
                value = constant
            setattr(self, option, value)

    def v2_runner_on_failed(self, result, ignore_errors=False):

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        self._clean_results(result._result, result._task.action)

        if self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        self._handle_exception(result._result, use_stderr=self.display_failed_stderr)
        self._handle_warnings(result._result)

        if result._task.loop and 'results' in result._result:
            self._process_items(result)

        else:
            if delegated_vars:
                self._display.display("fatal: [%s -> %s]: FAILED! => %s" % (result._host.get_name(), delegated_vars['ansible_host'],
                                                                            self._dump_results(result._result, indent=4)),
                                      color=C.COLOR_ERROR, stderr=self.display_failed_stderr)
            else:
                self._display.display("fatal: [%s]: FAILED! => %s" % (result._host.get_name(), self._dump_results(result._result, indent=4)),
                                      color=C.COLOR_ERROR, stderr=self.display_failed_stderr)

        if ignore_errors:
            self._display.display("...ignoring", color=C.COLOR_SKIP)

    def v2_runner_on_ok(self, result):

        delegated_vars = result._result.get('_ansible_delegated_vars', None)

        if isinstance(result._task, TaskInclude):
            return
        else:
            # To indicate partial in the status
            is_task_partial = False
            if result._result.get('status', '') == "PARTIAL":
                status_display_str = "partial"
                color = C.COLOR_HIGHLIGHT
                if self._partial_exec_count.get(result._host.get_name(), 0) == 0:
                    self._partial_exec_count[result._host.get_name()] = 0
                self._partial_exec_count[result._host.get_name()] += 1
                is_task_partial = True

            if result._result.get('changed', False):
                if self._last_task_banner != result._task._uuid:
                    self._print_task_banner(result._task)

                if is_task_partial is False:
                    status_display_str = "changed"
                    color = C.COLOR_CHANGED

                if delegated_vars:
                    msg = "%s: [%s -> %s]" % (status_display_str, result._host.get_name(), delegated_vars['ansible_host'])
                else:
                    msg = "%s: [%s]" % (status_display_str, result._host.get_name())

            else:
                if not self.display_ok_hosts:
                    return

                if is_task_partial is False:
                    status_display_str = "ok"
                    color = C.COLOR_OK

                if self._last_task_banner != result._task._uuid:
                    self._print_task_banner(result._task)

                if delegated_vars:
                    msg = "%s: [%s -> %s]" % (status_display_str, result._host.get_name(), delegated_vars['ansible_host'])
                else:
                    msg = "%s: [%s]" % (status_display_str, result._host.get_name())

        self._handle_warnings(result._result)

        if result._task.loop and 'results' in result._result:
            self._process_items(result)
        else:
            self._clean_results(result._result, result._task.action)

            # if (self._display.verbosity > 0 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
            msg += " => %s" % (self._dump_results(result._result, indent=4),)
            self._display.display(msg, color=color)

    def v2_runner_on_skipped(self, result):

        if self.display_skipped_hosts:

            self._clean_results(result._result, result._task.action)

            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            if result._task.loop and 'results' in result._result:
                self._process_items(result)
            else:
                msg = "skipping: [%s]" % result._host.get_name()
                self._display.display(msg, color=C.COLOR_SKIP)

    def v2_runner_on_unreachable(self, result):
        if self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        if delegated_vars:
            self._display.display("fatal: [%s -> %s]: UNREACHABLE! => %s" % (result._host.get_name(), delegated_vars['ansible_host'],
                                                                             self._dump_results(result._result, indent=4)),
                                  color=C.COLOR_UNREACHABLE)
        else:
            self._display.display("fatal: [%s]: UNREACHABLE! => %s" % (result._host.get_name(), self._dump_results(result._result, indent=4)), color=C.COLOR_UNREACHABLE)

    def v2_playbook_on_no_hosts_matched(self):
        self._display.display("skipping: no hosts matched", color=C.COLOR_SKIP)

    def v2_playbook_on_no_hosts_remaining(self):
        self._display.banner("NO MORE HOSTS LEFT")

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._task_start(task, prefix='TASK')

    def _task_start(self, task, prefix=None):
        # Cache output prefix for task if provided
        # This is needed to properly display 'RUNNING HANDLER' and similar
        # when hiding skipped/ok task results
        if prefix is not None:
            self._task_type_cache[task._uuid] = prefix

        # Preserve task name, as all vars may not be available for templating
        # when we need it later
        if self._play.strategy == 'free':
            # Explicitly set to None for strategy 'free' to account for any cached
            # task title from a previous non-free play
            self._last_task_name = None
        else:
            self._last_task_name = task.get_name().strip()

            # Display the task banner immediately if we're not doing any filtering based on task result
            if self.display_skipped_hosts and self.display_ok_hosts:
                self._print_task_banner(task)

    def _print_task_banner(self, task):
        # args can be specified as no_log in several places: in the task or in
        # the argument spec.  We can check whether the task is no_log but the
        # argument spec can't be because that is only run on the target
        # machine and we haven't run it thereyet at this time.
        #
        # So we give people a config option to affect display of the args so
        # that they can secure this if they feel that their stdout is insecure
        # (shoulder surfing, logging stdout straight to a file, etc).
        args = ''
        if not task.no_log and C.DISPLAY_ARGS_TO_STDOUT:
            args = u', '.join(u'%s=%s' % a for a in task.args.items())
            args = u' %s' % args

        prefix = self._task_type_cache.get(task._uuid, 'TASK')

        # Use cached task name
        task_name = self._last_task_name
        if task_name is None:
            task_name = task.get_name().strip()

        self._display.banner(u"%s [%s%s]" % (prefix, task_name, args))
        if self._display.verbosity >= 2:
            path = task.get_path()
            if path:
                self._display.display(u"task path: %s" % path, color=C.COLOR_DEBUG)

        self._last_task_banner = task._uuid

    def v2_playbook_on_cleanup_task_start(self, task):
        self._task_start(task, prefix='CLEANUP TASK')

    def v2_playbook_on_handler_task_start(self, task):
        self._task_start(task, prefix='RUNNING HANDLER')

    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            msg = u"PLAY"
        else:
            msg = u"PLAY [%s]" % name

        self._play = play

        self._display.banner(msg)

    def v2_on_file_diff(self, result):
        if self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        if result._task.loop and 'results' in result._result:
            for res in result._result['results']:
                if 'diff' in res and res['diff'] and res.get('changed', False):
                    diff = self._get_diff(res['diff'])
                    if diff:
                        self._display.display(diff)
        elif 'diff' in result._result and result._result['diff'] and result._result.get('changed', False):
            diff = self._get_diff(result._result['diff'])
            if diff:
                self._display.display(diff)

    def v2_runner_item_on_ok(self, result):

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        self._clean_results(result._result, result._task.action)
        if isinstance(result._task, TaskInclude):
            return
        else:
            # To indicate partial in the status
            is_task_partial = False
            if result._result.get('status', '') == "PARTIAL":
                msg = "partial"
                color = C.COLOR_HIGHLIGHT
                if self._partial_exec_count.get(result._host.get_name(), 0) == 0:
                    self._partial_exec_count[result._host.get_name()] = 0
                self._partial_exec_count[result._host.get_name()] += 1
                is_task_partial = True

            if result._result.get('changed', False):
                if self._last_task_banner != result._task._uuid:
                    self._print_task_banner(result._task)
                
                if is_task_partial is False:
                    msg = "changed"
                    color = C.COLOR_CHANGED
            else:
                if not self.display_ok_hosts:
                    return

                if is_task_partial is False:
                    msg = "ok"
                    color = C.COLOR_OK

                if self._last_task_banner != result._task._uuid:
                    self._print_task_banner(result._task)

        if delegated_vars:
            msg += ": [%s -> %s]" % (result._host.get_name(), delegated_vars['ansible_host'])
        else:
            msg += ": [%s]" % result._host.get_name()

        msg += " => (item=%s)" % (self._get_item_label(result._result),)

        msg += " => %s" % self._dump_results(result._result, indent=4)
        self._display.display(msg, color=color)

    def v2_runner_item_on_failed(self, result):
        if self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        self._clean_results(result._result, result._task.action)
        self._handle_exception(result._result)

        msg = "failed: "
        if delegated_vars:
            msg += "[%s -> %s]" % (result._host.get_name(), delegated_vars['ansible_host'])
        else:
            msg += "[%s]" % (result._host.get_name())

        self._handle_warnings(result._result)
        self._display.display(msg + " (item=%s) => %s" % (self._get_item_label(result._result), self._dump_results(result._result, indent=4)), color=C.COLOR_ERROR)

    def v2_runner_item_on_skipped(self, result):
        if self.display_skipped_hosts:
            if self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)

            self._clean_results(result._result, result._task.action)
            msg = "skipping: [%s] => (item=%s) " % (result._host.get_name(), self._get_item_label(result._result))
            self._display.display(msg, color=C.COLOR_SKIP)

    def v2_playbook_on_include(self, included_file):
        msg = 'included: %s for %s' % (included_file._filename, ", ".join([h.name for h in included_file._hosts]))
        if 'item' in included_file._args:
            msg += " => (item=%s)" % (self._get_item_label(included_file._args),)
        self._display.display(msg, color=C.COLOR_SKIP)

    def v2_playbook_on_stats(self, stats):
        self._display.banner("PLAY RECAP")
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)

            self._display.display(u"%s : %s %s %s %s %s" % (
                hostcolor(h, t),
                colorize(u'ok', t['ok'], C.COLOR_OK),
                colorize(u'changed', t['changed'], C.COLOR_CHANGED),
                colorize(u'unreachable', t['unreachable'], C.COLOR_UNREACHABLE),
                colorize(u'failed', t['failures'], C.COLOR_ERROR),
                colorize(u'partial', self._partial_exec_count.get(h, 0), C.COLOR_HIGHLIGHT),
                ),
                screen_only=True
            )

            self._display.display(u"%s : %s %s %s %s %s" % (
                hostcolor(h, t, False),
                colorize(u'ok', t['ok'], None),
                colorize(u'changed', t['changed'], None),
                colorize(u'unreachable', t['unreachable'], None),
                colorize(u'failed', t['failures'], None),
                colorize(u'partial', self._partial_exec_count.get(h, 0), C.COLOR_HIGHLIGHT),
                ),
                log_only=True
            )

        self._display.display("", screen_only=True)

        # print custom stats if required
        if stats.custom and self.show_custom_stats:
            self._display.banner("CUSTOM STATS: ")
            # per host
            # TODO: come up with 'pretty format'
            for k in sorted(stats.custom.keys()):
                if k == '_run':
                    continue
                self._display.display('\t%s: %s' % (k, self._dump_results(stats.custom[k], indent=1).replace('\n', '')))

            # print per run custom stats
            if '_run' in stats.custom:
                self._display.display("", screen_only=True)
                self._display.display('\tRUN: %s' % self._dump_results(stats.custom['_run'], indent=1).replace('\n', ''))
            self._display.display("", screen_only=True)

    def v2_playbook_on_start(self, playbook):
        if self._display.verbosity > 1:
            from os.path import basename
            self._display.banner("PLAYBOOK: %s" % basename(playbook._file_name))

        if self._display.verbosity > 3:
            # show CLI options
            if self._options is not None:
                for option in dir(self._options):
                    if option.startswith('_') or option in ['read_file', 'ensure_value', 'read_module']:
                        continue
                    val = getattr(self._options, option)
                    if val and self._display.verbosity > 3:
                        self._display.display('%s: %s' % (option, val), color=C.COLOR_VERBOSE, screen_only=True)

    def v2_runner_retry(self, result):
        task_name = result.task_name or result._task
        msg = "FAILED - RETRYING: %s (%d retries left)." % (task_name, result._result['retries'] - result._result['attempts'])
        if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
            msg += "Result was: %s" % self._dump_results(result._result, indent=4)
        self._display.display(msg, color=C.COLOR_DEBUG)

    def v2_playbook_on_notify(self, handler, host):
        if self._display.verbosity > 1:
            self._display.display("NOTIFIED HANDLER %s for %s" % (handler.get_name(), host), color=C.COLOR_VERBOSE, screen_only=True)