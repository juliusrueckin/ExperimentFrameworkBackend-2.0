from sacred import Experiment
import json
import subprocess
import re
import itertools
import time
import os

import parser
import writer
import plot

ex = Experiment('sacred_test')

@ex.config
def config():
    cfgfile=None

def extract_parameters(params):
    param_names = [p["name"] for p in params]
    params = [x["value"] for x in params]
    param_list = [perm for perm in itertools.product(*params)]
    return param_names, param_list

@ex.automain
def main(cfgfile):
    config = json.load(open(cfgfile))
    env = "" if config["env"] == "" else config["env"]
    cmd = config["cmd"]
    name = config["name"] if "name" in config else ""
    a = parser.Parser(config["outputs"] if "outputs" in config else [])
    resultdir = "results/" + str(round(time.time()*1000)) + "/"
    if not os.path.exists(resultdir):
        os.makedirs(resultdir)
    csvwriter = writer.CSVWriter(resultdir, name, env, cmd, a.names())
    cmd_string = "{0} {1} {2}".format(
        env, "" if config["path"] =="" else "cd " + config["path"] + "&& ", config["cmd"])
    timeout = float(config["timeout"]) if "timeout" in config else None
    names, param_list = extract_parameters(config["params"])
    p = plot.Plotter(config["plots"], resultdir, name,a.names(), names)
    for par in param_list:
        par_alloc = ",".join([names[i] + "=" + par[i] for i in range(0,len(names))])
        cmd_par = cmd_string + " " + " ".join(par)
        try:
            proc = subprocess.run(cmd_par,stdout=subprocess.PIPE, shell=True, timeout=timeout)
            open(resultdir + "stdout", "wb+").write(proc.stdout)
            result = a.parse(proc.stdout.decode())
            print(result)
            csvwriter.save_complete(par_alloc, dict(result))
            p.save_complete(par_alloc, dict(result))
        except subprocess.TimeoutExpired:
            csvwriter.save_fail(par_alloc, "timeout")
    p.plot()




