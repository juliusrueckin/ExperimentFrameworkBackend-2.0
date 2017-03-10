import re
import csv
import time

class CSVWriter():

    def __init__(self,path, name, env, cmd, names):
        self.fields=["timestamp", "name", "env", "cmd", "param", "error"]
        for key in names:
            self.fields.append(key)
        self.time = round(time.time() * 1000)
        self.name = name
        self.filename = "results" + ".csv"
        self.file = open(path + self.filename, "w", newline="")
        self.writer = csv.DictWriter(self.file, self.fields, restval=None)
        self.writer.writeheader()
        self.env = env
        self.cmd = cmd
        self.param = cmd

    def save_complete(self, params, result):
        self.add_metadata(result)
        result["param"] = params
        self.writer.writerow(result)

    def save_fail(self, params, error):
        result = {"error": error, "param": params}
        self.add_metadata(result)
        self.writer.writerow(result)

    def add_metadata(self, entry):
        entry["name"] = self.name
        entry["env"] = self.env
        entry["cmd"] = self.cmd
        entry["timestamp"] = self.time
