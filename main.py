import json
import re
import itertools
import time
import os
import sys
import collections
import multiprocessing as mp

from parser import Parser
from command import Command
from command import Execution
from writer import CSVWriter
from plot import Plotter
from slack import SlackNotifier

Parameters = collections.namedtuple('Parameters', ['names', 'assignments'])

class Experiment():
    def __init__(self, config):
        self.name = config["name"] if "name" in config else ""
        self.cores = int(config["cores"]) if "cores" in config else 1
        self.command = Command.parse_command(config)
        self.params = self.extract_parameters(config["params"])
        self.result_dir = "results/" + str(round(time.time()*1000)) + "/"
        os.makedirs(self.result_dir)
        self.parser = Parser.parse_outputs(config)
        self.writer = CSVWriter(self.result_dir, self.name, self.command.env, self.command.cmd, self.parser.names())
        self.plotter = Plotter(config, self.result_dir, self.name, self.parser.names(), self.params.names)
        self.slack = SlackNotifier.parse_slack(config)
    
    def extract_parameters(self,params):
        param_names = [p["name"] for p in params]
        params = [x["value"] for x in params]
        param_list = [perm for perm in itertools.product(*params)]
        return Parameters(param_names, param_list)

    def run_experiment(self):
        self.slack.start_experiment()
        with mp.Pool(3) as pool:
            res = [pool.apply_async(self.command.execute, (par,), callback=self.handle_result) for par in self.params.assignments]
            for r in res:
                r.wait()
        self.slack.finish_experiment()
        self.plotter.plot()

    def handle_result(self, execution):
        par = execution.params
        par_alloc = ",".join([self.params.names[i] + "=" + par[i] for i in range(0,len(par))])
        with open(self.result_dir + str(par) + "stdout", "w+") as out:
            out.write(execution.stdout)
        with open(self.result_dir + str(par) + "stderr", "w+") as err:
            err.write(execution.stderr)
        if execution.exit_code:
            self.writer.save_fail(par_alloc, execution.error)
            self.slack.save_fail(par_alloc, execution.error)
        else:
            result = self.parser.parse(execution.stdout)
            self.writer.save_complete(par_alloc, dict(result))
            self.plotter.save_complete(par_alloc, dict(result))
            self.slack.save_complete(par_alloc)
        

cfgfile = sys.argv[1]
config = json.load(open(cfgfile))
exp = Experiment(config)
exp.run_experiment()
