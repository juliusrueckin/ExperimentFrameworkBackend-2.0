import re
import csv
import time

class CSVWriter():
    """This class writes persists results of experiment runs into a csv file."""
    def __init__(self,path, name, env, cmd, names):
        self.fields=["timestamp", "name", "env", "cmd", "param", "error"]
        for key in names:
            self.fields.append(key)
        self.time = round(time.time() * 1000)
        self.name = name
        self.env = env
        self.cmd = cmd
        self.param = cmd
        self.create_csv(path)
    
    def create_csv(self, path):
        """Create results file and write header line."""
        self.file = open(path + "results.csv", "w", newline="")
        self.writer = csv.DictWriter(self.file, self.fields, restval=None)
        self.writer.writeheader()

    def save_complete(self, params, result):
        """Save a successful run. Store data regarding the run, parameters and result values."""
        self.add_run_data(result)
        result["param"] = params
        self.writer.writerow(result)

    def save_fail(self, params, error):
        """Save a failed run. Store data regarding the run, parameters and the occurred error."""
        result = {"error": error, "param": params}
        self.add_run_data(result)
        self.writer.writerow(result)

    def add_run_data(self, entry):
        """Save information of the run in addition to its results

        This includes the name of the experiment, environment variables, the executed command and 
        the timestamp of execution        
        """
        entry["name"] = self.name
        entry["env"] = self.env
        entry["cmd"] = self.cmd
        entry["timestamp"] = self.time
