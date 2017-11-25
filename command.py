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
        timeout = float(config["defaultTimeout"]) if "defaultTimeout" in config else None

        error_regex=status_regex=accuracy_regex=accuracy_value_regex=loss_regex=loss_value_regex=".\A"
        min_accuracy_improvement=min_loss_improvement=999999999.9
        if "stdoutParsing" in config:
            configStdoutParsing = config["stdoutParsing"]

            if "errorPattern" in configStdoutParsing:
                error_regex = configStdoutParsing["errorPattern"]

            if "statusPattern" in configStdoutParsing:
                status_regex = configStdoutParsing["statusPattern"] 
                if "maxTimeSinceLastStatusMsg" in configStdoutParsing:
                    max_time_since_last_status_msg = float(configStdoutParsing["maxTimeSinceLastStatusMsg"])
                else:
                    raise ValueError("Define max. time since last status message!")

            if "accuracyPattern" in configStdoutParsing:
                accuracy_regex = configStdoutParsing["accuracyPattern"]
                if "minAccuracyFunctionImprovementSinceLastIteration" in configStdoutParsing:
                    min_accuracy_improvement = float(configStdoutParsing["minAccuracyFunctionImprovementSinceLastIteration"])
                else:
                    raise ValueError("Define min. accuracy imporvement since last iteration")
                if "accuracyValuePattern" in configStdoutParsing:
                    accuracy_value_regex = configStdoutParsing["accuracyValuePattern"]
                else:
                    raise ValueError("Define accuracy function value regex!")

            if "lossPattern" in configStdoutParsing:
                loss_regex = configStdoutParsing["lossPattern"]
                if "minLossFunctionImprovementSinceLastIteration" in configStdoutParsing:
                    min_loss_improvement = float(configStdoutParsing["minLossFunctionImprovementSinceLastIteration"])
                else:
                    raise ValueError("Define min. loss imporvement since last iteration")
                if "lossValuePattern" in configStdoutParsing:
                    loss_value_regex = configStdoutParsing["lossValuePattern"]
                else:
                    raise ValueError("Define loss function value regex!")

        params = Parameters.parse_params(config)
        return cls(cmd, env, path, timeout, error_regex, status_regex, accuracy_regex, accuracy_value_regex, loss_regex, loss_value_regex, min_accuracy_improvement, min_loss_improvement, params)

    def __init__(self, cmd, env="", path="", timeout=None, error_regex=".\A", status_regex=".\A", accuracy_regex=".\A", accuracy_value_regex=".\A", loss_regex=".\A", loss_value_regex=".\A", min_accuracy_improvement=999999999.9, min_loss_improvement=999999999.9, params = None):
        self.env = env
        self.cmd = cmd
        self.path = path
        self.timeout = timeout
        self.error_regex = error_regex
        self.status_regex = status_regex
        self.accuracy_regex = accuracy_regex
        self.accuracy_value_regex = accuracy_value_regex
        self.loss_regex = loss_regex
        self.loss_value_regex = loss_value_regex
        self.min_accuracy_improvement = min_accuracy_improvement
        self.min_loss_improvement = min_loss_improvement
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
        proc = subprocess.Popen(cmd_par, stdin= subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid, universal_newlines=True)
        
        """ Poll process for new output until finished
        Search for various output patterns: error, status, loss, accuracy
        """
        while True:
            next_line = proc.stdout.readline()
            if proc.poll() is not None and next_line == "":
                break
            print("Processed stdout: " + next_line)

        try:
            out, err = proc.communicate(timeout=self.timeout)
            errors = re.findall(self.error_regex, out.decode(), flags=re.I|re.M)
            error = '\n'.join(errors) if errors else ""
            if errors:
                return Execution(params, False, error, 0, out.decode(), err.decode())
            else:
                return Execution(params, False, error, 1, out.decode(), err.decode())
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(proc.pid),signal.SIGTERM)
            out, err = proc.communicate()
            return Execution(params, True, "timeout", 124, out.decode(), err.decode())

    def get_parametrizations(self):
        return self.params.parametrizations if self.params else []

    def get_param_names(self):
        return self.params.names if self.params else []