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
from writer import CSVWriter
from plotter import Plotter
from slack import SlackNotifier
from mail import MailNotifier
from utilization_bot import UtilizationBot
from telegram_bot import TelegramNotifier

Parameters = collections.namedtuple('Parameters', ['names', 'assignments'])

class Experiment():

    def __init__(self, config):
        self.name = config["title"] if "title" in config else ""
        self.cores = int(config["cores"]) if "cores" in config else 1
        self.serialize_runs = True if "serialize_runs" in config else False
        self.command = Command.parse_command(config)
        self.result_dir = "results/" + str(round(time.time()*1000)) + "/"
        os.makedirs(self.result_dir)
        self.parser = Parser.parse_outputs(config)
        self.observers = []

        #add telegram utilization bot
        if "telegram" in config:
            self.utilizationBot = UtilizationBot.parse_utilization_bot(config, os.getpid())

        #add observers
        if "plots" in config:
            self.observers.append(Plotter(config,self.parser.names(), self.result_dir))
        if "slack" in config:
            self.observers.append(SlackNotifier.parse_slack(config))
        if "csv" in config:
            self.observers.append(CSVWriter(self.result_dir, self.name, self.parser.names()))
        if "mail" in config:
            self.observers.append(MailNotifier.parse_mail(config, self.result_dir + "results.csv", self.name))
        if "telegram" in config:
            self.observers.append(TelegramNotifier.parse_telegram(config))
    
    def set_amount_of_parallel_process(self):
        if self.serialize_runs:
            return 1
        else:
            return 3

    def run_experiment(self):
        for ob in self.observers:
            ob.start_experiment(self.command)
        with mp.Pool(self.set_amount_of_parallel_process()) as pool:
            res = [pool.apply_async(self.command.execute, (par,), callback=self.handle_result) 
                for par in self.command.get_parametrizations()]
            for r in res:
                r.wait()
        for ob in self.observers:
            ob.finish_experiment()

    def handle_result(self, execution):
        par = execution.params
        par_alloc = ",".join([self.command.get_param_names()[i] + "=" + par[i] for i in range(0,len(par))])
        with open(self.result_dir + str(par) + "stdout", "w+") as out:
            out.write(execution.stdout)
        with open(self.result_dir + str(par) + "stderr", "w+") as err:
            err.write(execution.stderr)
        if execution.exit_code == 0:
            for ob in self.observers:
                ob.save_fail(par_alloc, execution.error)
        else:
            result = self.parser.parse(execution.stdout)
            for ob in self.observers:
                ob.save_complete(par_alloc, result)        

if __name__ == "__main__":
    cfgfile = sys.argv[1]
    config = json.load(open(cfgfile,"r"))
    exp = Experiment(config)
    exp.run_experiment()