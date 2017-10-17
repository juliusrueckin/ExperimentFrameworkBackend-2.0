import requests
import collections

class SlackNotifier():
    """This class uses slack webhooks to send notifications about the progress of an experiment."""
    @classmethod
    def parse_slack(cls, config):
        """Read the json configuration and create an instance of SlackNotifier from it"""
        if "slack" in config:
            webhook = config["slack"]["webhook_url"]
            verbose = True if config["slack"]["verbose"] else False
            icon = config["slack"]["icon"]
            bot_name = config["slack"]["bot_name"]
            return cls(webhook, verbose, icon, bot_name)
        else:
            return cls("", False, "", "")
        

    def __init__(self, webhook, verbose, icon, bot_name):
        self.webhook = webhook
        self.verbose = verbose
        self.icon = icon
        self.bot_name = bot_name

        self.completed = 0
        self.failed = 0

    def start_experiment(self, command):
        """Notify about the start of an experiment and define its environment and commands."""
        if self.webhook:
            data = '{{"text": "Experiment {0} with variables {1} started", "icon_emoji": "{2}", "username": "{3}"}}'
            self.send_message(data.format(command.cmd, command.env, self.icon, self.bot_name))
    
    def finish_experiment(self):
        """Notify about the termination of an experiment, summarize complete and failed runs."""
        if self.webhook:
            data = '{{"text": "Experiment finished, {0} completed and {1} failed runs", "icon_emoji": "{2}", "username": "{3}"}}'
            self.send_message(data.format(self.completed, self.failed, self.icon, self.bot_name))

    def save_complete(self,par_alloc,result):
        """If verbose, notify the successful termination of a single run."""
        self.completed += 1
        if self.webhook and self.verbose:
            data = '{{"text": ":white_check_mark: for configuration {0}", "icon_emoji": "{1}", "username": "{2}"}}'
            self.send_message(data.format(par_alloc, self.icon, self.bot_name))

    def save_fail(self,par_alloc, error):
        """If verbose, notify the failed termination of a single run."""
        self.failed += 1
        if self.webhook and self.verbose:
            data='{{"text": ":x: Error {0} for run with configuration {1}", "icon_emoji": "{2}", "username": "{3}"}}'
            self.send_message(data.format(error, par_alloc, self.icon, self.bot_name))

    def send_message(self,data):
        """Prepare and send the POST request to Slack."""
        requests.post(self.webhook, headers={'Content-type': 'application/json'}, data=data)
