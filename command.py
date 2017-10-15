import subprocess
import collections
import os
import signal
import time
import re

from param import Parameters

Execution = collections.namedtuple('Execution', ['params', 'timeout', 'error', 'exit_code', 'stdout', 'stderr'])

class Command():
    """This class stores thereatc execution information (params, environment, path, cmd) and executes them.
    It handles timeouts and errors when executing runs
    """
    @classmethod
    def parse_command(cls, config):
        """Extract the configuration from the .json file."""
        cmd = config["cmd"]
        path = config["path"] if "path" in config else ""
        env = config["env"] if "env" in config else ""
        timeout = float(config["timeout"]) if "timeout" in config else None
        error_regex = config["error"] if "error" in config else ".\A"
        params = Parameters.parse_params(config)
        return cls(cmd, env, path, timeout, error_regex, params)

    def __init__(self, cmd, env="", path="", timeout=None, error_regex=".\A", params = None):
        self.env = env
        self.cmd = cmd
        self.path = path
        self.timeout = timeout
        self.error_regex = error_regex
        self.params = params

    def get_execute_command(self):
        """Assemble the command to execute from environment, path and cmd."""
        if self.path:
            return self.env + " cd " + self.path + " && " + self.cmd
        else:
            return self.env + " " + self.cmd

    def execute(self, params):
        """Execute the command parametrized by the given parameters

        Open a subprocess to execute the command. After the subprocess ends collect the contents
        of stdout and stderr. If the execution stops with an error extract the error given the optional
        error regex from the configuration. Return these with an exit_code 

        Can optionally set a timeout in the configuration. If so, terminate the subprocess and all
        children after the timeout, collect stdout and stderr so far and return them. Additionally
        set the timeout flag to True
        """
        cmd_par = self.get_execute_command() + " " + " ".join(params)
        proc = subprocess.Popen(cmd_par,stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        try:
            out, err = proc.communicate(timeout=self.timeout)
            errors = re.findall(self.error_regex, err.decode(), flags=re.I|re.M)
            error = '\n'.join(errors) if errors else ""
            return Execution(params, False, error, proc.returncode, out.decode(), err.decode())
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(proc.pid),signal.SIGTERM)
            out, err = proc.communicate()
            return Execution(params, True, "timeout", 124, out.decode(), err.decode())

    def get_parametrizations(self):
        return self.params.parametrizations if self.params else []

    def get_param_names(self):
        return self.params.names if self.params else []


