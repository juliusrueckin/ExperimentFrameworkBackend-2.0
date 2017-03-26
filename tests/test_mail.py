import unittest
import json

from unittest.mock import Mock
from mail import MailNotifier

class TestMail(unittest.TestCase):

    def setUp(self):
        with open("tests/mail_config.json","r") as file:
            config = json.load(file)
        self.mail = MailNotifier.parse_mail(config)

    def test_parse_mail(self):
        self.assertTrue(self.mail.server == "localhost:0" and self.mail.user == "Usermail" 
                        and self.mail.password == "***",
                        msg = "Error parsing mail configuration from .json file")
        self.assertTrue(self.mail.cmd == "echo 1" and self.mail.env == "A=hello",
                        msg = "Error parsing command information")
    
    def test_start_experiment(self):
        self.mail.start_experiment()
        expected = "Experiment echo 1 with variables A=hello started\n"
        self.assertEqual(expected, self.mail.message,
            msg = "Wrong text for start of experiment")

    def test_save_complete(self):
        self.mail.save_complete("a=1")
        expected = "    Completed run for configuration a=1"
        self.assertEqual(expected, self.mail.message, msg = "Wrong text for completed run")

    def test_save_fail(self):
        self.mail.save_fail("a=1", "timeout")
        expected = "    Error timeout for run with configuration a=1"
        self.assertEqual(expected, self.mail.message, msg = "Wrong text for failed run")

    def test_finish_experiment(self):
        self.mail.send_mail = Mock(side_effect=self.check_mail)
        self.mail.finish_experiment()
        expected = "Experiment finished, 0 completed and 0 failed runs"
        self.assertEqual(expected, self.mail.message, msg = "Wrong text for finished experiment")

    def check_mail(self):
        self.assertEqual("Experiment finished, 0 completed and 0 failed runs", self.mail.message,
            msg = "Wrong email body for sending the mail")


    
