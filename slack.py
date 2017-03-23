import requests
import collections

class SlackNotifier():
    """This class uses slack webhooks to send notifications about the progress of an experiment."""
    @classmethod
    def parse_slack(cls, config):
        """Read the json configuration and create an instance of SlackNotifier from it"""
        webhook = config["url"] if "url" in config else ""
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
        """Notify about the start of an experiment and define its environment and commands."""
        if self.webhook:
            data = '{{"text": "Experiment {0} with variables {1} started"}}'
            self.send_message(data.format(self.cmd, self.env))
    
    def finish_experiment(self):
        """Notify about the termination of an experiment, summarize complete and failed runs."""
        if self.webhook:
            data = '{{"text": "Experiment finished, {0} completed and {1} failed runs"}}'
            self.send_message(data.format(self.completed, self.failed))

    def save_complete(self,par_alloc):
        """If verbose, notify the successful termination of a single run."""
        self.completed += 1
        if self.webhook and self.verbose:
            data = '{{"text": ":white_check_mark: for configuration {0}"}}'
            self.send_message(data.format(par_alloc))

    def save_fail(self,par_alloc, error):
        """If verbose, notify the failed termination of a single run."""
        self.failed += 1
        if self.webhook and self.verbose:
            data='{{"text": ":x: for configuration {0} with error: {1}"}}'
            self.send_message(data.format(par_alloc, error))

    def send_message(self,data):
        """Prepare and send the POST request to Slack."""
        requests.post(self.webhook, headers={'Content-type': 'application/json'}, data=data)
