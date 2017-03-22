import subprocess
import collections
import os
import signal
import time
import re

Execution = collections.namedtuple('Execution', ['params', 'timeout', 'error', 'exit_code', 'stdout', 'stderr'])

class Command():
    @classmethod
    def parse_command(cls, config):
        cmd = " exec " + config["cmd"]
        path = " cd " + config["path"] + " && " if "path" in config else ""
        env = config["env"] if "env" in config else ""
        timeout = float(config["timeout"]) if "timeout" in config else None
        error_regex = config["error"] if "error" in config else ".\A"
        return cls(env,path, cmd, timeout, error_regex)

    def __init__(self,env, path, cmd, timeout, error_regex):
        self.env = env
        self.cmd = cmd
        self.path = path
        self.timeout = timeout
        self.error_regex = error_regex

    def execute(self, params):
        cmd_par = self.env + self.path + self.cmd + " " + " ".join(params)
        print (cmd_par)
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


