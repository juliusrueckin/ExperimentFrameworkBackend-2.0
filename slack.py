import requests

class SlackNotifier():
    @classmethod
    def parse_slack(cls, config):
        webhook = config["url"]
        return cls(webhook)

    def __init__(self, webhook):
        self.webhook = webhook

    def save_complete(self,par_alloc):
        data='{"text": "Experiment with configuration ' + par_alloc + ' passed succesfully"}'
        print(data)
        requests.post(self.webhook, headers={'Content-type': 'application/json'}, data=data)
