import requests
import collections

class SlackNotifier():
    @classmethod
    def parse_slack(cls, config):
        webhook = config["url"]
        env = config["env"]
        cmd = config["cmd"]
        verbose = True if "verbose" in config else False
        return cls(webhook, env, cmd, verbose)

    def __init__(self, webhook, env, cmd, verbose):
        self.webhook = webhook
        self.env = env
        self.cmd = cmd
        self.verbose = verbose
        self.completed = 0
        self.failed = 0

    def start_experiment(self):
        data='{"text": "Experiment ' + self.cmd + ' with variables ' + self.env + ' started"}'
        self.send_message(data)
    
    def finish_experiment(self):
        data='{"text": "Experiment finished, ' + str(self.completed) + ' completed and ' + str(self.failed) + 'failed runs"}'
        self.send_message(data)

    def save_complete(self,par_alloc):
        data='{"text": ":white_check_mark: for configuration ' + par_alloc + '"}'
        self.send_message(data)
        self.completed += 1

    def save_fail(self,par_alloc, error):
        data='{"text": ":x: for configuration ' + par_alloc + ' with error: ' + error + '"}'
        self.send_message(data)
        self.failed += 1

    def send_message(self,data):
        requests.post(self.webhook, headers={'Content-type': 'application/json'}, data=data)
