import unittest
import json

import httmock

from command import Command

class TestCommand(unittest.TestCase):

    def setUp(self):
        with open("tests/command_config.json","r") as file:
            config = json.load(file)
        with open("tests/command_path_config.json","r") as file:
            config_path = json.load(file)
        self.command = Command.parse_command(config)
        self.p_command = Command.parse_command(config_path)
        
    def test_get_execute_command(self):
        expected = "A=test echo 1 && sleep"
        self.assertEqual(expected, self.command.get_execute_command(),
            msg="Error parsing command with env and cmd")
        expected = " cd ~ && python3 -c '1/0'"
        self.assertEqual(expected, self.p_command.get_execute_command(),
            msg="Error parsing command with path and cmd")

    def test_execute_complete(self):
        result = self.command.execute(["1"])
        self.assertEqual(0, result.exit_code, msg="wrong exit code for succesfull command")
        self.assertEqual('1\n', result.stdout, msg="Wrong captured output for executed command")

    def test_execute_error(self):
        result = self.p_command.execute([])
        self.assertNotEqual(0,result.exit_code, msg="wrong exit code for errorenous command")
        self.assertNotEqual("", result.stderr, msg="Error should be captured in stderr")
        self.assertEqual("ZeroDivisionError: division by zero", result.error, 
            msg="Regex should be able to extract the occurred error from stderr")
    
    def test_execute_timeout(self):
        result = self.command.execute(["3"])
        self.assertNotEqual(0, result.exit_code, msg="timeout should not have 0 exit code")
        self.assertTrue(result.timeout, msg="timeout flag should be set after a timeout")
