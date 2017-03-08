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
        "" if config["env"] is None else config["env"],
        "" if config["path"] is None else "cd " + config["path"] + "&& ",
        config["cmd"])
    cmd_string += " " + config["params"][0]["value"][0]
    print(cmd_string)
    subprocess.call(cmd_string,shell=True)

#R_HOME=/usr/lib/R;LD_LIBRARY_PATH=/usr/lib/R/lib:/usr/lib/R/bin:/home/lukas/R/x86_64-pc-linux-gnu-library/3.2/rJava/jri:;R_SHARE_DIR=/usr/share/R/share;R_INCLUDE_DIR=/usr/share/R/include;R_DOC_DIR=/usr/share/R/doc
