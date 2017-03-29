import re
import csv
import time

class CSVWriter():
    """This class writes persists results of experiment runs into a csv file."""
    def __init__(self,path, name, names):
        self.fields=["timestamp", "name", "env", "cmd", "param", "error"]
        for key in names:
            self.fields.append(key)
        self.time = round(time.time() * 1000)
        self.name = name
        self.path = path
    
    def start_experiment(self, command):
        """Create results file and write header line."""
        self.env = command.env
        self.cmd = command.cmd
        self.file = open(self.path + "results.csv", "w", newline="")
        self.writer = csv.DictWriter(self.file, self.fields, restval=None)
        self.writer.writeheader()

    def save_complete(self, params, result):
        res = dict(result)
        """Save a successful run. Store data regarding the run, parameters and result values."""
        self.add_run_data(res)
        res["param"] = params
        self.writer.writerow(res)

    def save_fail(self, params, error):
        """Save a failed run. Store data regarding the run, parameters and the occurred error."""
        result = {"error": error, "param": params}
        self.add_run_data(result)
        self.writer.writerow(result)

    def finish_experiment(self):
        self.file.close()

    def add_run_data(self, entry):
        """Save information of the run in addition to its results

        This includes the name of the experiment, environment variables, the executed command and 
        the timestamp of execution        
        """
        entry["name"] = self.name
        entry["env"] = self.env
        entry["cmd"] = self.cmd
        entry["timestamp"] = self.time
