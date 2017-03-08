from sacred import Experiment
import json
import subprocess

ex = Experiment('sacred_test')

@ex.config
def config():
    cfgfile=None

@ex.automain
def main(cfgfile):
    config = json.load(open(cfgfile))
    cmd_string = "{0} {1} {2}".format(
        "" if config["env"] == "" else config["env"],
        "" if config["path"] =="" else "cd " + config["path"] + "&& ",
        config["cmd"])
    params = config["params"]
    if len(params) <= 1:
        cmd_string += " " + config["params"][0]["value"][0]
        subprocess.call(cmd_string,shell=True)
    else:
        paramlist = [[x] for x in params[0]["value"]]
        print(paramlist)
        for param in params[1:]:
            values = param["value"]
            paramlist2 = []
            for v in values:
                for p in paramlist:
                    paramlist2.append(p + [v])
            paramlist = paramlist2
        print(paramlist)
        for par in paramlist:
            cmd_par = cmd_string + " " + " ".join(par)
            subprocess.call(cmd_par,shell=True)
