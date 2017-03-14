import json
import subprocess
import re
import itertools
import time
import os
import sys
import collections

import parser
import command
import writer
import plot
import slack

Parameters = collections.namedtuple('Parameters', ['names', 'assignments'])

class Experiment():
    def __init__(self, config):
        self.name = config["name"] if "name" in config else ""
        self.command = command.Command.parse_command(config)
        self.params = self.extract_parameters(config["params"])
        self.result_dir = "results/" + str(round(time.time()*1000)) + "/"
        os.makedirs(self.result_dir)
        self.parser = parser.Parser(config["outputs"] if "outputs" in config else [])
        self.writer = writer.CSVWriter(self.result_dir, self.name, self.command.env, self.command.cmd, self.parser.names())
        self.plotter = plot.Plotter(config["plots"] if "plots" in config else [], self.result_dir, self.name, self.parser.names(), self.params.names)
        self.slack = slack.SlackNotifier.parse_slack(config)
    
    def extract_parameters(self,params):
        param_names = [p["name"] for p in params]
        params = [x["value"] for x in params]
        param_list = [perm for perm in itertools.product(*params)]
        return Parameters(param_names, param_list)

    def run_experiment(self):
        for par in self.params.assignments:
            par_alloc = ",".join([self.params.names[i] + "=" + par[i] for i in range(0,len(par))])
            execution = self.command.execute(par)
            with open(self.result_dir + str(par) + "stdout", "w+") as out:
                out.write(execution.stdout)
            with open(self.result_dir + str(par) + "stderr", "w+") as err:
                err.write(execution.stderr)
            if execution.timeout:
                self.writer.save_fail(par_alloc, "timeout")
            elif execution.exit_code:
                errors = re.findall("^(.*?(?:(?:error)|(?:exception)).*?)$", 
                    execution.stderr, flags=re.I|re.M)
                print(errors)
                error = '\n'.join(errors) if errors else execution.exit_code
                self.writer.save_fail(par_alloc, error)
            else:
                result = self.parser.parse(execution.stdout)
                self.writer.save_complete(par_alloc, dict(result))
                self.plotter.save_complete(par_alloc, dict(result))
                self.slack.save_complete(par_alloc)
        self.plotter.plot()

cfgfile = sys.argv[1]
config = json.load(open(cfgfile))
exp = Experiment(config)
exp.run_experiment()
