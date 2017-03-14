import requests

class SlackNotifier():
    @classmethod
    def parse_slack(cls, config):
        webhook = config["url"]
        return cls(webhook)

    def __init__(self, webhook):
        self.webhook = webhook

    def save_complete(self,par_alloc):
        data='{"text": ":white_check_mark: for configuration ' + par_alloc + '"}'
        print(data)
        requests.post(self.webhook, headers={'Content-type': 'application/json'}, data=data)

    def save_fail(self,par_alloc, error):
        data='{"text": ":x: for configuration ' + par_alloc + ' with error: ' + error + '"}'
        print(data)
        requests.post(self.webhook, headers={'Content-type': 'application/json'}, data=data)
