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
from plotter import Plotter
from slack import SlackNotifier
from mail import MailNotifier

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
        self.observers = []
        if "plots" in config:
            self.observers.append(Plotter(config,self.parser.names(), self.params.names, self.result_dir))
        if "url" in config:
            self.observers.append(SlackNotifier.parse_slack(config))
        if "mail" in config:
            self.observers.append(MailNotifier.parse_mail(config))
        if "csv" in config:
            self.observers.append(CSVWriter(self.result_dir, self.name, self.command.env, self.command.cmd, self.parser.names()))
    
    def extract_parameters(self,params):
        param_names = [p["name"] for p in params]
        params = [x["value"] for x in params]
        param_list = [perm for perm in itertools.product(*params)]
        return Parameters(param_names, param_list)

    def run_experiment(self):
        for ob in self.observers:
            ob.start_experiment()
        with mp.Pool(3) as pool:
            res = [pool.apply_async(self.command.execute, (par,), callback=self.handle_result) for par in self.params.assignments]
            for r in res:
                r.wait()
        for ob in self.observers:
            ob.finish_experiment()

    def handle_result(self, execution):
        par = execution.params
        par_alloc = ",".join([self.params.names[i] + "=" + par[i] for i in range(0,len(par))])
        with open(self.result_dir + str(par) + "stdout", "w+") as out:
            out.write(execution.stdout)
        with open(self.result_dir + str(par) + "stderr", "w+") as err:
            err.write(execution.stderr)
        if execution.exit_code:
            for ob in self.observers:
                ob.save_fail(par_alloc, execution.error)
        else:
            result = self.parser.parse(execution.stdout)
            for ob in self.observers:
                ob.save_complete(par_alloc, result)        

cfgfile = sys.argv[1]
config = json.load(open(cfgfile,"r"))
exp = Experiment(config)
exp.run_experiment()
