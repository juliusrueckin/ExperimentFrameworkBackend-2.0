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

        """
        Parse all given stdoutput patterns and check for each given pattern whether
        required additional information are given. Otherwise raise an exception to
        prevent calculation errors in stdout parsing logic later on.
        """
        error_regex=status_regex=accuracy_regex=accuracy_value_regex=loss_regex=loss_value_regex=progress_regex=progress_value_regex=".\A"
        min_accuracy_improvement=min_loss_improvement=max_time_since_last_status_msg=999999999.9
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

            if "progressPattern" in configStdoutParsing:
                progress_regex = configStdoutParsing["progressPattern"]
                if "progressValuePattern" in configStdoutParsing:
                    progress_value_regex = configStdoutParsing["progressValuePattern"]
                else:
                    raise ValueError("Define progress value regex!")

        params = Parameters.parse_params(config)
        return cls(cmd, env, path, timeout, error_regex, status_regex, max_time_since_last_status_msg, accuracy_regex, accuracy_value_regex, loss_regex, loss_value_regex, min_accuracy_improvement, min_loss_improvement, progress_regex, progress_value_regex, params)

    def __init__(self, cmd, env="", path="", timeout=None, error_regex=".\A", status_regex=".\A", max_time_since_last_status_msg=999999999.9, accuracy_regex=".\A", accuracy_value_regex=".\A", loss_regex=".\A", loss_value_regex=".\A", min_accuracy_improvement=999999999.9, min_loss_improvement=999999999.9, progress_regex=".\A", progress_value_regex=".\A", params = None):
        self.env = env
        self.cmd = cmd
        self.path = path
        self.timeout = timeout
        self.error_regex = error_regex
        self.status_regex = status_regex
        self.max_time_since_last_status_msg = max_time_since_last_status_msg
        self.accuracy_regex = accuracy_regex
        self.accuracy_value_regex = accuracy_value_regex
        self.loss_regex = loss_regex
        self.loss_value_regex = loss_value_regex
        self.min_accuracy_improvement = min_accuracy_improvement
        self.min_loss_improvement = min_loss_improvement
        self.progress_regex = progress_regex
        self.progress_value_regex = progress_value_regex
        self.params = params

        self.last_status_occured = time.time()
        self.last_accuracy = 0.0
        self.last_loss = 9999999.9

    def get_execute_command(self):
        """Assemble the command to execute from environment, path and cmd."""
        if self.path:
            return self.env + " cd " + self.path + " && " + self.cmd
        else:
            return self.env + " " + self.cmd

    def process_stdout(self, next_output, proc):
        print("Processed stdout: " + next_output)

        """
        If error pattern occured, kill algorithm's process.
        """
        occured_errors = re.findall(self.error_regex, next_output, flags=re.I|re.M)
        if len(occured_errors) > 0:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            #raise ValueError("Error pattern occured!")
        
        """
        If status pattern occured and max. time since last status pattern exceeded,
        kill algirthm's process.
        """
        occured_stats = re.findall(self.status_regex, next_output, flags=re.I|re.M)
        if len(occured_stats) > 0:
            if time.time() - self.last_status_occured > self.max_time_since_last_status_msg:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                #raise ValueError("Max. time since last status message exceeded!")
            else: 
                self.last_status_occured = time.time()

        """
        If accuracy pattern occured and accuracy function did not improve enough,
        kill algorithm's process.
        """
        occured_accuracy_patterns = re.findall(self.accuracy_regex, next_output, flags=re.I|re.M)
        if len(occured_accuracy_patterns) > 0:
            accuracy_pattern_content = occured_accuracy_patterns[-1]
            current_accuracy = float(re.findall(self.accuracy_value_regex, accuracy_pattern_content, flags=re.I|re.M)[-1])
            accuracy_improvement = current_accuracy - self.last_accuracy
            if accuracy_improvement < self.min_accuracy_improvement:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                #raise ValueError("Min. accuracy improvement not reached!")
            else:
                self.last_accuracy = current_accuracy

        """
        If loss pattern occured and loss function did not improve enough,
        kill algorithm's process.
        """
        occured_loss_patterns = re.findall(self.loss_regex, next_output, flags=re.I|re.M)
        if len(occured_loss_patterns) > 0:
            loss_pattern_content = occured_loss_patterns[-1]
            current_loss = float(re.findall(self.loss_value_regex, loss_pattern_content, flags=re.I|re.M)[-1])
            loss_improvement = self.last_loss - float(current_loss)
            if loss_improvement < self.min_loss_improvement:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                #raise ValueError("Min. loss improvement not reached!")
            else:
                self.last_loss = current_loss

        """
        If progress pattern occured, process progress value and send it to rails api in
        order to display progress visually in rails front end.
        """
        occured_progess_patterns = re.findall(self.progress_regex, next_output, flags=re.I|re.M)
        if len(occured_progess_patterns) > 0:
            progress_pattern_content = occured_progess_patterns[-1]
            progress_value = float(re.findall(self.progress_value_regex, progress_pattern_content, flags=re.I|re.M)[-1])
            print("Processed new progress: " + str(progress_value) + "% \n")

    def execute(self, params):
        """Execute the command parametrized by the given parameters

        Open a subprocess to execute the command. Poll process for new output until finished.
        Search for various output patterns: error, status, loss, accuracy, progress. After the 
        subprocess ends collect the contents of stdout and stderr. If the execution stops with 
        an error extract the error given the optional error regex from the configuration. Return
        these with an exit_code. All given stdoutpatterns occur during run time (also the error
        pattern, nevertheless it checked after termination too).

        Can optionally set a timeout in the configuration. If so, terminate the subprocess and all
        children after the timeout, collect stdout and stderr so far and return them. Additionally
        set the timeout flag to True
        """
        cmd_par = self.get_execute_command() + " " + " ".join(params)
        proc = subprocess.Popen(cmd_par, stdin= subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid, universal_newlines=True)
        
        while True:
            next_line = proc.stdout.readline()
            if proc.poll() is not None and next_line == "":
                break
            self.process_stdout(next_line, proc)

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