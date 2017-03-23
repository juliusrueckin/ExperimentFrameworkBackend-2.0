import unittest
import json

import httmock

from slack import SlackNotifier

class TestSlack(unittest.TestCase):

    def setUp(self):
        with open("tests/slack_config.json","r") as file:
            config = json.load(file)
        with open("tests/slack_config_verbose.json","r") as file:
            config_verbose = json.load(file)
        self.slack = SlackNotifier.parse_slack(config)
        self.v_slack = SlackNotifier.parse_slack(config_verbose)

        self.expected_data = ""

    @httmock.all_requests
    def handle_post(self, url, request):
        self.assertEqual("http://example.org/", url.geturl())
        if self.expected_data:
            self.assertEqual(self.expected_data, request.body)
        return {'status_code':200}

    @httmock.all_requests
    def fail_on_post(self,url,request):
        self.fail("Non verbose Slack should not send a message")


    def test_parse_slack(self):
        self.assertTrue(self.v_slack.webhook and self.v_slack.env and self.v_slack.cmd and
            self.v_slack.verbose, msg="Error parsing Slack from json")
        self.assertFalse(self.slack.verbose, msg="Error for parsing verbose flag")

    def test_send_message(self):
        with httmock.HTTMock(self.handle_post):
            self.slack.send_message('{"text":"test"}')

    def test_start_experiment(self):
        self.expected_data = '{"text": "Experiment echo 1 with variables A=hello started"}'
        with httmock.HTTMock(self.handle_post):
            self.slack.start_experiment()

    def test_finish_experiment(self):
        self.expected_data = '{"text": "Experiment finished, 0 completed and 0 failed runs"}'
        with httmock.HTTMock(self.handle_post):
            self.slack.finish_experiment()

    def test_save_complete(self):
        self.expected_data = '{"text": ":white_check_mark: for configuration a=1"}'
        with httmock.HTTMock(self.handle_post):
            self.v_slack.save_complete("a=1")
        with httmock.HTTMock(self.fail_on_post):
            self.slack.save_complete("a=1")

    def test_save_fail(self):
        self.expected_data = '{"text": ":x: for configuration a=1 with error: timeout"}'
        with httmock.HTTMock(self.handle_post):
            self.v_slack.save_fail("a=1", "timeout")
        with httmock.HTTMock(self.fail_on_post):
            self.slack.save_fail("a=1", "timeout")


    


