import subprocess
import collections
import os
import signal

Execution = collections.namedtuple('Execution', ['timeout', 'exit_code', 'stdout', 'stderr'])

class Command():
    @classmethod
    def parse_command(cls, config):
        cmd = " exec " + config["cmd"]
        path = " cd " + config["path"] + " && " if "path" in config else ""
        env = config["env"] if "env" in config else ""
        timeout = float(config["timeout"]) if "timeout" in config else None
        return cls(env,path, cmd, timeout)

    def __init__(self,env, path, cmd, timeout):
        self.env = env
        self.cmd = cmd
        self.path = path
        self.timeout = timeout

    def execute(self, params):
        cmd_par = self.env + self.path + self.cmd + " " + " ".join(params)
        print (cmd_par)
        proc = subprocess.Popen(cmd_par,stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        try:
            out, err = proc.communicate(timeout=self.timeout)
            return Execution(False, proc.returncode, out.decode(), err.decode())
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(proc.pid),signal.SIGTERM)
            out, err = proc.communicate()
            return Execution(True, None, out.decode(), err.decode())
        except:
            os.killpg(os.getpgid(proc.pid),signal.SIGTERM)
            out, err = proc.communicate()
            return Execution(False, proc.returncode, out.decode(), err.decode())
